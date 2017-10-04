import os
import yaml
import time
import logging
from praw import Reddit
from .database import Database
from .helpers import render_template
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


class RedditBot:

    def __init__(self, mode='watch'):

        self._mode = mode

        # Configura e inicia banco de dados, reddit e etc...
        # assim que o objeto Redditbot foi instanciado.

        self._setup_logging()
        self._logger.info('The Bot is now starting in {} mode.'
                          .format(self._mode))
        self._load_config()
        self._setup_database()
        self._setup_reddit()

    # Configura o formato de saída dos logs, também o arquivo.
    # O bot executa dois processos separados, um "watch" e outro
    # "reply", cada processo tem o seu log.

    def _setup_logging(self):
        if not os.path.exists('logs'):
            os.makedirs('logs')

        self._logger = logging.getLogger(__name__)
        formatter = logging.Formatter('%(asctime)s '
                                      '[%(levelname)s] '
                                      '%(message)s')
        self._logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        fh = logging.FileHandler('logs/{}.log'
                                 .format(self._mode))
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)
        self._logger.addHandler(ch)
        self._logger.addHandler(fh)

    # Carrega o arquivo de configuração, qualquer erro
    # logga e raise a exception

    def _load_config(self):
        try:
            with open('config.yml', 'r') as file:
                self._config = yaml.load(file)
            self._logger.info('Loaded config file.')
        except Exception as e:
            self._logger.critical('Couldn\'t load config file.')
            self._logger.critical(e)
            raise

    # Cria o objecto Reddit, note que ele não automaticamente
    # conecta aqui, por isso para testar a conexão chamamos então
    # reddit.user.me() para que ele connecte e pegue o usuário
    # se falhar aqui, há um problema com autenticação ou etc...

    def _setup_reddit(self):
        try:
            self._reddit = Reddit(**self._config['reddit'])
            username = self._reddit.user.me()
            self._logger.info('Connected to Reddit as: {}.'
                              .format(username))
        except Exception as e:
            self._logger.critical('Couldn\'t connect to Reddit.')
            self._logger.critical(e)
            raise

    # Configua banco de dados

    def _setup_database(self):
        try:
            database = Database(**self._config['database'])
            self._db = database
            self._logger.info('Connected to database: '
                              '{driver}://{username}@{host}:{port}/{database}'
                              .format_map(self._config['database']))
        except Exception as e:
            self._logger.critical('Couldn\'t connect to database.')
            self._logger.critical(e)
            raise

    # Assiste (ou escuta) o stream de comentários dos subreddits
    # no arquivo de config.

    def watch(self):

        self._logger.info('Watching for new comments.')

        # Caso haja mais de um subreddit, junte-os separados por +,
        # exemplo: brasil+portugal, assim ele trabalhará nos dois
        # subreddits.

        subreddits_list = '+'.join(self._config['bot']['subreddits'])
        subreddits = self._reddit.subreddit(subreddits_list)

        while True:
            try:
                # Assiste o stream de comentários
                for comment in subreddits.stream.comments():
                    self._logger.info('Comment base36_id found: {}.'
                                      .format(comment.id))
                    # pega o comentário anterior ou a submission (publicação)
                    parent = comment.parent()

                    commands = self._config['bot']['commands']

                    # verifica se o corpo do comentário contém algum comando cadastrado na config
                    if comment.body.lower().startswith(tuple(commands)):
                        # a propriedade .author retorna None se a conta tiver sido apagada
                        # então verifica se a conta ainda existe antes de prosseguir.
                        # raramente acontece, mas é uma possibilidade.
                        if comment.author and parent.author:
                            # Verifica se o autor está votando para si mesmo ou para o próprio Bot
                            if comment.author != parent.author \
                            and parent.author != self._reddit.user.me():

                                self._logger.info('Comment base36_id: {} matches command.'
                                                  .format(comment.id))

                                # adiciona o usuario caso não exista no db, caso ja exista
                                # retorna apenas o resultado da query
                                from_user = self._db.get_or_add_user(username=comment.author)
                                to_user = self._db.get_or_add_user(username=parent.author)

                                # Verifica se usuario ja não votou para o mesmo comentario
                                if not self._db.get_comment(from_user_id = from_user.id,
                                                            parent_base36_id = parent.id):
                                    try:
                                        # Adiciona o comentário no db, para ser processado pelo
                                        # reply.
                                        self._db.add_comment(
                                            parent_base36_id = parent.id,
                                            base36_id = comment.id,
                                            from_user_id = from_user.id,
                                            to_user_id = to_user.id
                                        )
                                        # Adiciona +1 pontos ao usuário que recebeu o voto.
                                        to_user.points += 1
                                        self._db.session.commit()
                                        self._logger.info('Added to database!')

                                    except IntegrityError:
                                        self._logger.info('Already added to database!')
                                        self._db.session.rollback()
                                    except SQLAlchemyError:
                                        self._logger.info('Something went wrong with your database, rolling back!')
                                        self._db.session.rollback()

            # Pega qualquer Exception loga e tenta novamente em 5s,
            # Não é uma boa prática at all, mas está 
            # funcionando e não é prioridade.
            # Quem quiser melhorar isso aqui, só mandar PR =)
            except Exception as e:
                self._logger.error('Tried to read comments stream'
                                   ' but failed, trying again!')
                self._logger.error(e)
            time.sleep(5)

    def reply(self):

        self._logger.info('Looking for new comments to reply to.')

        while True:
            # Pega todos os comentários que foram adicionados ao db
            # mas ainda não foram respondidos.
            comments = self._db.get_comments(status='TO_REPLY')
            try:
                for comment in comments:
                    self._logger.info('Replying to comment base36_id: {}'
                                      .format(comment.base36_id))
                    # carrega o comentário
                    reddit_comment = self._reddit.comment(id=comment.base36_id)
                    # renderiza o template e gera o comentário de acordo com as informações
                    # do banco de dados.
                    render = render_template('default.md', comment=comment)
                    # Responde ao comentário e marca o status para DONE
                    reddit_comment.reply(render)
                    comment.status = 'DONE'
                    self._db.session.commit()
                    self._logger.info('Replied to comment base36_id: {}'
                                      .format(comment.base36_id))
                    # timer temporario, por ser uma conta nova devo limitar os comentários entre 9m.
                    #time.sleep(60 * 10)
                    # agora que a conta já tem karma suficiente, limitar apenas para cada dois segundos
                    # no mínimo, mas deixarei 4
                    time.sleep(4)


            # Pega todas as exceptions,
            # péssima prática mas tá valendo por enquanto.
            except Exception as e:
                comment.status = 'ERROR'
                self._db.session.commit()
                self._logger.error('Something went wrong!')
                self._logger.error(e)
            self._db.session.commit()
            time.sleep(5)
