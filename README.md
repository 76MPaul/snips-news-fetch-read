# Snips-News-Fetch&Reading

Ce module développé pour Snips vous permet de récupérer les news disponible grâce à NewsAPI.
Il permet actuellement : 
  - de récupérer et vous énoncer les gros titres :
    - de manière globale sur un pays disponible (par défaut pour la France),
    - sur l'une des catégories suivante : 
      - business 
      - entertainment 
      - health 
      - science 
      - sports 
      - technology
    -  sur une source disponible dans l'API.
  - de récupérer les articles disponibles sur l'une des 30 000 sources de NewsAPI
  - de lire un article précédement trouvé.

## Usages :

Ce module s'intègre dans votre gestionnaire d'événements Snips.

  - Créer une instance de newsHandler :
  ```
    from modules.news.newsHandler import newsHandler
  	self.news = newsHandler()
  ```
  - Appeler newsFetch pour gérer l'événement
  ```
  	text = self.news.newsFetch(slots,intentname)
  ```

## sources :
  NewsAPI - https://newsapi.org/docs/endpoints/everything
  NewsPaper3k - https://newspaper.readthedocs.io/en/latest/


## Todo :

  - Ajouter des exemples

## Changelog :

  - 23/09/2018 - Initial Commit
