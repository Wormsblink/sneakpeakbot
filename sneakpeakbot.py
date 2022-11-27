import config
import praw
import time
from datetime import datetime
import os
from heapq import nlargest

from newspaper import Article

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
                        user_agent = "Expert Identifier v0.2")
        print("Log in successful!")
        print(datetime.now().strftime('%d %b %y %H:%M:%S'))
        return r

def run_bot(r, replied_articles_id):

    for submission in r.subreddit('sgbotstest').new(limit = 5):

        if (submission.id not in replied_articles_id and not submission.url.startswith("https://www.reddit.com") and submission.selftext==""):

            articlereply="There was an error reading the article text. This may be due to a paywall"

            print(submission.url)

            article_summary = get_summary(submission.url)

            print("getting article summary")

            if(article_summary=="READ TEXT ERROR"):
                print("Error reading text")
                articlereply = "There was an error reading the article text. This may be due to a paywall."
            elif(article_summary=="TEXT LENGTH ERROR"):
                print("Text Length Error")
            else:
                print("Text reading successful")
                articlereply = get_summary(submission.url)

            fullreply = articlereply + "\n\n***\n\n" + "[v0.2 (Beta)](" + "https://github.com/Wormsblink/sneakpeakbot" + ") by Sg_Wormsblink and running on Raspberry Pi400 | PM SG_wormsbot if bot is down."
            fullreply = fullreply + "\n\n This is a test on my main account, will transfer to u/SG_wormsbot when karma / age requirements are met. Mods if you want to greenlight the bot PM me"

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
        if (len(newstext)<400):
            summarized_article = newstext
        elif (len(newstext)<800):
            summarized_article = summarize_text(newstext,0.5)
        elif (len(newstext)>1600):
            summarized_article = summarize_text(newstext,0.25)
        elif (len(newstext)<3200):
            summarized_article = summarize_text(newstext,0.125)
        else:
            return("TEXT LENGTH ERROR")

    return summarized_article

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