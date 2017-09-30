import os
import yaml
import time
import logging
from praw import Reddit
from .database import Database
from .helpers import render_template
from sqlalchemy.exc import IntegrityError


class RedditBot:

    def __init__(self, mode='watch'):

        self.mode = mode

        self._setup_logging()
        self._logger.info('The Bot is now starting')
        self._load_config()
        self._setup_database()
        self._setup_reddit()

    def _setup_logging(self):
        if not os.path.exists('logs'):
            os.makedirs('logs')

        logger = logging.getLogger(__name__)
        formatter = logging.Formatter('%(asctime)s '
                                      '[%(levelname)s] '
                                      '%(message)s')
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        fh = logging.FileHandler('logs/{}.log'
                                 .format(self.mode))
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)
        logger.addHandler(ch)
        logger.addHandler(fh)
        self._logger = logger

    def _load_config(self):
        try:
            with open('config.yml', 'r') as file:
                self._config = yaml.load(file)
            self._logger.info('Loaded config file.')
        except Exception as e:
            self._logger.critical('Couldn\'t load config file.')
            self._logger.critical(e)
            raise

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

    def watch(self):

        self._logger.info('Watching for new comments.')

        subreddits_list = '+'.join(self._config['bot']['subreddits'])
        subreddits = self._reddit.subreddit(subreddits_list)

        while True:
            try:
                for comment in subreddits.stream.comments():
                    self._logger.info('Comment base36_id found: {}.'.format(comment.id))
                    parent = comment.parent()

                    commands = self._config['bot']['commands']

                    if comment.body.lower().startswith(tuple(commands)):
                        if comment.author and parent.author:
                            if comment.author != parent.author:

                                self._logger.info('Comment base36_id: {} matches command.'.format(comment.id))

                                from_user = self._db.get_or_add_user(username=comment.author)
                                to_user = self._db.get_or_add_user(username=parent.author)

                                # Verifica se usuario ja votou para o mesmo comentario
                                if not self._db.get_comment(from_user_id = from_user.id,
                                                            parent_base36_id = parent.id):
                                    try:
                                        self._db.add_comment(
                                            parent_base36_id = parent.id,
                                            base36_id = comment.id,
                                            from_user_id = from_user.id,
                                            to_user_id = to_user.id
                                        )
                                        to_user.points += 1
                                        self._db.session.commit()
                                        self._logger.info('Added to database!')

                                    except IntegrityError:
                                        self._logger.info('Already added to database!')
                                        self._db.session.rollback()

            except Exception as e:
                self._logger.error('Tried to read comments stream'
                                   ' but failed, trying again!')
                self._logger.error(e)
            time.sleep(5)

    def reply(self):

        self._logger.info('Looking for new comments to reply to.')

        while True:
            comments = self._db.get_comments(status='TO_REPLY')
            try:
                for comment in comments:
                    self._logger.info('Replying to comment base36_id: {}'.format(comment.base36_id))
                    reddit_comment = self._reddit.comment(id=comment.base36_id)
                    render = render_template('default.md', comment=comment)
                    reddit_comment.reply(render)
                    comment.status = 'DONE'
                    self._db.session.commit()
                    self._logger.info('Replied to comment base36_id: {}'.format(comment.base36_id))
                    time.sleep(5)
                self._db.session.commit()
                time.sleep(5)
            except Exception as e:
                comment.status = 'ERROR'
                self._db.session.commit()
                self._logger.error('Something went wrong!')
                self._logger.error(e)
