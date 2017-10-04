# RedditNióbioBot

RedditNiobioBot é um Reddit Bot inspirado no /u/RedditSilverRobot que permite 
que os usuários possam premiar o conteúdo dos outros com um ponto (RedditNióbio).
## Instalação (GNU/Linux)
Clone este repositório:
```sh
git clone git@github.com:CaioWzy/RedditNiobioBot.git
```
Instale as dependências:
```sh
pip install -r requeriments.txt
```
## Configuração
Renomeie o arquivo config.sample.yml para config.yml e preencha as informações 
seguindo as orientações dos comentários contigos no arquivo.  
## Uso
O bot possui dois modos: watch e reply, os dois executam em loop infinito 
devem ser iniciados. O modo watch busca por novos comentários e o reply 
responde aos comentários.
Para iniciar o bot em watch mode:
```sh
./Bot.py watch
```
Para iniciar o bot em reply mode:
```sh
./Bot.py reply
```
