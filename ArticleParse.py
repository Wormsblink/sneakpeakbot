from newspaper import Article
from urllib import request
from bs4 import BeautifulSoup

def get_title(article_url):

    requested_site = request.Request(article_url, headers={"User-Agent": "Mozilla/5.0"})
    html = request.urlopen(requested_site).read().decode('utf8','ignore')
    html[:60]

    soup = BeautifulSoup(html, 'html.parser')
    bs_title = soup.find('title')

    try:
        cleaned_title = bs_title.string.split("|", 1)[0]
        split_title = cleaned_title.split(" - ")
        parsed_title = split_title[0]

        if (len(split_title) > 1):
            for title_segment in split_title[1:]:
                if (not(title_segment[0].isupper())):
                    parsed_title = parsed_title + " - " + title_segment
    except:
        parsed_title = "Error obtaining title"

    return parsed_title

def parse_text(article_url):

    article = Article(article_url)
    article.download()
    article.parse()
    newstext = article.text

    return newstext

