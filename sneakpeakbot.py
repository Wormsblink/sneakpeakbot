import config
import praw
import time
from datetime import datetime
import os

from newspaper import Article

#This is for future spacy nlp summarizing news text

#import spacy
#from spacy.lang.en.stop_words import STOP_WORDS
#nlp = spacy.load("en_core_web_lg")

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
                        user_agent = "Expert Identifier v0.2")
        print("Log in successful!")
        print(datetime.now().strftime('%d %b %y %H:%M:%S'))
        return r

def run_bot(r, replied_articles_id):

    for submission in r.subreddit('sgbotstest').new(limit = 25):

        if (submission.id not in replied_articles_id and not submission.url.startswith("https://www.reddit.com")):

            print(submission.url)

            article_summary = get_summary(submission.url)

            print("getting article summary")

            if(article_summary=="READ TEXT ERROR"):
                print("Error reading text")
                articlereply = "There was an error reading the article text. This may be due to a paywall."

            else:
                print("Text reading successful")
                articlereply = get_summary(submission.url)
                fullreply = articlereply + "\n\n***\n\n" + "[v0.1](" + "https://github.com/Wormsblink/sneakpeakbot" + ") by Sg_Wormsblink and running on Raspberry Pi400 | PM SG_wormsbot if bot is down"

            submission.reply(fullreply)

            print("Replied to submission " + submission.id + " by " + submission.author.name)
            replied_articles_id.append(submission.id)
        
        with open ("replied_articles.txt", "a") as f:
                f.write(submission.id + "\n")

    print("Sleeping for 10 seconds")
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



def get_summary(article_url):

    article = Article(article_url)
    article.download()
    article.parse()
    newstext = article.text

    #print(newstext)

    if not newstext:
        return("READ TEXT ERROR")
    else:
        summarized_article=newstext
        #summarized_article=article.summary

    #print(summarized_article)

    return summarized_article

# Main

api = None

r = bot_login()
while True:
    run_bot(r, get_replied_articles())