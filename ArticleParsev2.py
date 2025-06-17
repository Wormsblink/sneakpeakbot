from selenium import webdriver
from newspaper import Article
from urllib import request
from bs4 import BeautifulSoup

def get_html(article_url):

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36");
    driver = webdriver.Chrome(options = options)
    driver.get(article_url)
    html = driver.page_source
    driver.quit()

    return html

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

def parse_text_bs(article_url):

    html = get_html(article_url)
    soup = BeautifulSoup(html, features="html.parser")

    for script in soup(["script", "style"]):
        script.extract()

    newstext = soup.body.get_text(separator='\n\n', strip=True)
    
    sens = newstext.splitlines()
    CleanedSens= list(filter(lambda s: len(s.split()) >= 10, sens))
    newstext = "\n\n".join(CleanedSens)

    return newstext

def parse_text(article_url):

    html = get_html(article_url)
    article = Article(" ")
    article.set_html(html)
    article.parse()

    newstext = article.text

    sens = newstext.splitlines()
    CleanedSens= list(filter(lambda s: len(s.split()) >= 10, sens))
    newstext = "\n\n".join(CleanedSens)

    return newstext
