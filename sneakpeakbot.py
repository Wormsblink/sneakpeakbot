import config
import praw
import time
from datetime import datetime
import os
import re

from heapq import nlargest

from newspaper import Article
from urllib import request
from bs4 import BeautifulSoup

import spacy
nlp = spacy.load('en_core_web_sm')
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation

nlp = spacy.load("en_core_web_sm")

        # spacy en_core_web_sm
        # most efficient 
        # spacy en_core_web_trf
        # most accurate


def bot_login():
        print ("Logging in...")
        r = praw.Reddit(username = config.username,
                        password = config.password,
                        client_id = config.client_id,
                        client_secret = config.client_secret,
                        user_agent = "Sneakpeakbot v0.7")
        print("Log in successful!")
        print(datetime.now().strftime('%d %b %y %H:%M:%S'))
        return r

def run_bot(r, replied_articles_id):

    for comment in r.subreddit('Singapore').comments(limit = 20):
        if ("!sneakpeak" in comment.body): 
            
            #print("bot was called")

            submission=comment.submission

            #print("found submission")

            if (submission.selftext=="" and not submission.url.startswith("https://www.reddit.com")):

                fullreply=""
                articlereply=""

                if (submission.id in replied_articles_id):
                    fullreply=""
                    #print("Duplicate found. Previously replied to comment " + submission.id)
                else:

                    articlereply="There was an error reading the article text. This may be due to a paywall"

                    #print(submission.url)

                    try:
                        article_summary = get_summary(submission.url)
                    except:
                        article_summary = "READ TEXT ERROR"

                    #print("getting article summary")

                    if(article_summary=="READ TEXT ERROR"):
                        print("Error reading text")
                        articlereply = "There was an error reading the article text. This may be due to a paywall."
                    elif(article_summary=="TEXT LENGTH ERROR"):
                        print("Text Length Error")
                    else:
                        print("Text reading successful")
                        articlereply = get_summary(submission.url)
                        article_title = get_htmltitle(submission.url)
                        fullreply = "#" + article_title + " \n\n"

                    fullreply = fullreply + articlereply + "\n\n***\n\n" + "[v0.7 (Beta)](" + "https://github.com/Wormsblink/sneakpeakbot" + ") | PM SG_wormsbot if bot is down."

                    #print(fullreply)

                    submission.reply(fullreply)

                    print("Replied to submission " + submission.id + " by " + submission.author.name)
        
                    with open ("replied_articles.txt", "a") as f:
                        f.write(submission.id + "\n")

            else:
                fullreply=""
                #print("wrong submission type")

    #print("Sleeping for 10 seconds")
    time.sleep(10)

def get_replied_articles():
        if not os.path.isfile("replied_articles.txt"):
                open("replied_articles.txt", 'w').close()
                replied_articles_id = []
        else:
                with open("replied_articles.txt", "r") as f:
                        replied_articles_id = f.read()
                        replied_articles_id = replied_articles_id.split("\n")

        return replied_articles_id

def get_htmltitle(article_url):

    requested_site = request.Request(article_url, headers={"User-Agent": "Mozilla/5.0"})
    html = request.urlopen(requested_site).read().decode('utf8')
    html[:60]

    soup = BeautifulSoup(html, 'html.parser')
    bs_title = soup.find('title')

    cleaned_title = bs_title.string.split("|", 1)[0]
    cleaned_title = cleaned_title.split("-", 1)[0]

    return cleaned_title


def get_summary(article_url):

    article = Article(article_url)
    article.download()
    article.parse()
    
    newstext = article.text

    #print(newstext)

    if not newstext:
        return("READ TEXT ERROR")
    else:

        summarized_article = newstext
        percentSentences = 90
        
        if (len(summarized_article)>8000):
            while (len(summarized_article)>8000):
                #print("attempting to summarize")
                #print(len(summarized_article))
                summarized_article = summarize_text(summarized_article, percentSentences/100)

    cleaned_article = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', summarized_article)

    return cleaned_article

def summarize_text(text, per):
    
    ##

    doc= nlp(text)
    tokens=[token.text for token in doc]
    word_frequencies={}
    
    for word in doc:
        if word.text.lower() not in list(STOP_WORDS):
            if word.text.lower() not in punctuation:
                if word.text not in word_frequencies.keys():
                    word_frequencies[word.text] = 1
                else:
                    word_frequencies[word.text] += 1
    max_frequency=max(word_frequencies.values())
    
    for word in word_frequencies.keys():
        word_frequencies[word]=word_frequencies[word]/max_frequency
    sentence_tokens= [sent for sent in doc.sents]
    sentence_scores = {}
    
    for sent in sentence_tokens:
        for word in sent:
            if word.text.lower() in word_frequencies.keys():
                if sent not in sentence_scores.keys():                            
                    sentence_scores[sent]=word_frequencies[word.text.lower()]
                else:
                    sentence_scores[sent]+=word_frequencies[word.text.lower()]
    
    select_length=int(len(sentence_tokens)*per)
    summary=nlargest(select_length, sentence_scores,key=sentence_scores.get)
    
    final_summary=[word.text for word in summary]
    summary=''.join(final_summary)

    return summary

# Main

r = bot_login()
while True:
    run_bot(r, get_replied_articles())