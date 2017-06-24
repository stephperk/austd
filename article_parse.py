###requires python 2.7
### see http://newspaper.readthedocs.io/en/latest/user_guide/install.html#install for installation and dependency guide
import newspaper
from newspaper import Article


def process_article(link):
    art ={}
    try:
        url=link
        article= Article(url)
        article.download()
        article.parse()
        art["title"] = article.title
        art["authors"] = article.authors
        art["text_parsed"] = article.text
        #art['date']
    except:
        pass
    return art
