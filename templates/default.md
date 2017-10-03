###[/u/{{ comment.to_user.username }} aqui está o seu RedditNióbio!](https://i.imgur.com/55fMDFL.jpg)  
***  
{% if comment.to_user.points <= 1 %}
/u/{{ comment.to_user.username }} ganhou um RedditNióbio pela primeira vez! (Recebido de: /u/{{ comment.from_user.username }})  
{% else %}
/u/{{ comment.to_user.username }} já ganhou RedditNióbio {{ comment.to_user.points }} vezes. (Recebido de: /u/{{ comment.from_user.username }})  
{% endif %}  
^(Como ainda tenho pouco karma só poderei comentar a cada 9 minutos, porém os pontos serão contados independentemente disso.)  
^^[ ^^[créditos](https://www.reddit.com/r/brasil/comments/70cie0/libido_muito_alta_n%C3%A3o_consigo_fazer_mais_nada_na/dn2az48/) ^^| ^^[desenvolvedor](https://www.reddit.com/u/CaioWzy) ^^| ^^[código-fonte](https://github.com/CaioWzy/RedditNiobioBot) ^^]