##first pip install spacy, newspaper3k, praw, bs4, pandas
##then spacy download en_core_web_trf

import config
import praw
import pandas as pd
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

        # spacy en_core_web_sm
        # most efficient
        # spacy en_core_web_md
        # middle ground 
        # spacy en_core_web_trf
        # most accurate


def bot_login():
        print ("Logging in...")
        r = praw.Reddit(username = config.username,
                        password = config.password,
                        client_id = config.client_id,
                        client_secret = config.client_secret,
                        user_agent = "Sneakpeakbot v1.0")
        print("Log in successful!")
        print(datetime.now().strftime('%d %b %y %H:%M:%S'))
        return r

def run_bot(r, replied_articles_id,approvedlist):

    for submission in r.subreddit('singapore').new(limit=10):

    #Disabled bot call comment
    #for comment in r.subreddit('singapore').comments(limit = 20):
        #if ("!sneakpeak" in comment.body): 

            #submission=comment.submission

            if (submission.selftext=="" and not submission.url.startswith("https://www.reddit.com") and submission.url.startswith(tuple(approvedlist))):

                fullreply=""
                articlereply=""
                similarity_reply=""

                if (submission.id in replied_articles_id):
                    fullreply=""
                else:

                    articlereply="There was an error reading the article text. This may be due to a paywall"

                    try:
                        article_summary = get_summary(submission.url)
                    except:
                        article_summary = "READ TEXT ERROR"

                    if(article_summary=="READ TEXT ERROR"):
                        
                        articlereply = "There was an error reading the article text. This may be due to a paywall."
                    elif(article_summary=="TEXT LENGTH ERROR"):
                        print("Text Length Error")
                    else:
                        articlereply = get_summary(submission.url)
                        article_title = get_htmltitle(submission.url)
                
                        replied_database = pd.read_csv("replied_articles.csv",index_col=[0])

                        similar_database = check_similarity(article_title, replied_database)
                        max_similarity_record = similar_database[similar_database.similarity_value == similar_database.similarity_value.max()]

                        #print(max_similarity_record)

                        if (not(max_similarity_record.empty)):
                            if (max_similarity_record.loc[0]["similarity_value"]>0.80):
                                similarity_reply = "***\n\n" + "The article title is " + str(round(max_similarity_record.loc[0]["similarity_value"]*100)) + "% similar to: [" + max_similarity_record.loc[0]["title"] + "](https://www.reddit.com/r/singapore/comments/" + max_similarity_record.loc[0]["id"] + ")"

                        append_to_database = pd.DataFrame({"id": [submission.id], "title": [article_title]})
                        

                        replied_database = pd.concat([replied_database, append_to_database])
                        replied_database.to_csv('replied_articles.csv')

                        print("New entry for " + submission.id + " in Database at " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

                        fullreply = "Original Title: " + article_title + " \n\n"

                    fullreply = fullreply + articlereply + "\n\n" + similarity_reply + "\n***\n\n" + "[v1.0](" + "https://github.com/Wormsblink/sneakpeakbot" + ") | PM SG_wormsbot if bot is down."
                    submission.reply(fullreply)

                    print("Replied to submission " + submission.id + " by " + submission.author.name)

            else:
                fullreply=""
                #print("wrong submission type")

    #print("Sleeping for 10 seconds")
    time.sleep(10)

def get_replied_articles():
        
        if not os.path.isfile("replied_articles.csv"):
                blank_database=pd.DataFrame(columns=['id','title'])
                blank_database.to_csv("replied_articles.csv")
                replied_articles_id = []
        else:
                replied_database = pd.read_csv("replied_articles.csv")
                replied_articles_id = replied_database['id'].tolist()
                #replied_articles_id = replied_articles_id.split("\n")

        return replied_articles_id

def get_approved_list():
    with open("approved_sites_list.txt", "r") as f:
        approved_list = f.read()
        approved_list = approved_list.split("\n")

    return approved_list

def get_htmltitle(article_url):

    requested_site = request.Request(article_url, headers={"User-Agent": "Mozilla/5.0"})
    html = request.urlopen(requested_site).read().decode('utf8')
    html[:60]

    soup = BeautifulSoup(html, 'html.parser')
    bs_title = soup.find('title')

    parsed_title = "Error obtaining title"

    cleaned_title = bs_title.string.split("|", 1)[0]

    split_title = cleaned_title.split(" - ")

    parsed_title = split_title[0]

    if (len(split_title) > 1):
        for title_segment in split_title[1:]:
            if (not(title_segment[0].isupper())):
                parsed_title = parsed_title + " - " + title_segment


    return parsed_title

def check_similarity(article_title, replied_database):

    similar_database = replied_database.copy()

    similar_database["similarity_value"] = ""

    #temp_article_title = nlp(' '.join([str(t) for t in article_title if not t in list(STOP_WORDS)]))

    temp_article_title = nlp(' '.join([str(t) for t in article_title.split() if (not t in list(STOP_WORDS) or not t in punctuation)]))
    
    print(temp_article_title)

    replied_articles_titles = replied_database["title"].tolist()
    
    for replied_title in replied_articles_titles:
        temp_replied_title = nlp(' '.join([str(t) for t in replied_title.split() if (not t in list(STOP_WORDS) or not t in punctuation)]))
        
        print(temp_replied_title)

        similarity_value = temp_article_title.similarity(temp_replied_title)
        similar_database["similarity_value"][similar_database.title == replied_title] = similarity_value

    return similar_database

def get_summary(article_url):

    article = Article(article_url)
    article.download()

    #Currently Broken
    #if(html.find(class_='paid-premium st-flag-1') == 'For Subscribers'):
    #    return("READ TEXT ERROR")
    
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

run_bot(r, get_replied_articles(),get_approved_list())

#while True:
#   try:
#       run_bot(r, get_replied_articles(),get_approved_list())
#       #time.sleep(10)
#   except Exception as e:
#       print("Fatal error at " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ", " + str(e))
#       #time.sleep(10)