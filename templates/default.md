###[/u/{{ comment.to_user.username }} aqui está o seu RedditNióbio!](https://i.imgur.com/55fMDFL.jpg)  
***  
{% if comment.to_user.points <= 1 %}
/u/{{ comment.to_user.username }} ganhou um RedditNióbio pela primeira vez! (Recebido de: /u/{{ comment.from_user.username }})  
{% else %}
/u/{{ comment.to_user.username }} já ganhou RedditNióbio {{ comment.to_user.points }} vezes. (Recebido de: /u/{{ comment.from_user.username }})  
{% endif %}  
^(Como ainda tenho pouco karma só poderei comentar a cada 9 minutos, porém os pontos serão contados independentemente disso.)  
^^[ ^^[créditos](https://www.reddit.com/r/brasil/comments/71o41b/sou_uma_pessoa_que_possui_sinestesia_da/dncl6dw/) ^^| ^^[desenvolvedor](https://www.reddit.com/u/CaioWzy) ^^| ^^[código-fonte](https://github.com/CaioWzy/RedditNiobioBot) ^^]