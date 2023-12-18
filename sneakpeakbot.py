#Python 3
#first from termimal - pip install spacy, newspaper3k, praw, bs4, pandas, spacy-universal-sentence-encoder
#then spacy download en_core_web_sm (in terminal)

import config

import pandas as pd

import praw
import time
from datetime import datetime
import os
import re
import warnings
import traceback

from heapq import nlargest

from newspaper import Article
from urllib import request
from bs4 import BeautifulSoup

import spacy
import spacy_universal_sentence_encoder
nlp = spacy.load('en_core_web_sm')
nlp2 = spacy_universal_sentence_encoder.load_model('en_use_lg')

from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation

warnings.filterwarnings("ignore",message=r"\[W007\]",category=UserWarning)

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
                        user_agent = "Sneakpeakbot v1.5c")
        print("Log in successful!")
        print(datetime.now().strftime('%d %b %y %H:%M:%S'))
        return r

def run_bot(r, replied_articles_id,approvedlist):

    for submission in r.subreddit('singapore').new(limit=10):

    #Disabled bot call comment
    #for comment in r.subreddit('singapore').comments(limit = 20):
        #if ("!sneakpeak" in comment.body): 

            #submission=comment.submission

            if ((submission.selftext=="" and submission.url.startswith(tuple(approvedlist))) and not submission.url.startswith("https://www.reddit.com")):

                fullreply=""
                article_title="ERROR"
                articlereply=""
                similarity_reply=""
                parsed_article=""
                keywords=""
                keywords_string=""

                if (submission.id in replied_articles_id):
                    pass
                    #print(submission.id + " is in replied database")

                elif (check_top_level_comments(submission)==True):
                    print("bot comment detected in top level comments for " + submission.id)

                else:
                    article_error_flag = False

                    try:
                        parsed_article=parse_article(submission.url)
                        articlereply = get_summary(parsed_article)
                    except:
                        article_error_flag = True
                        articlereply = "There was an error reading the article text. This may be due to a paywall."
                        print("Article summary error flag triggered on " + submission.id)

                    try:
                        article_title = get_htmltitle(submission.url)
                    except:
                        article_error_flag = True
                        article_title = "There was an error reading the article title. This "
                        print("Article title error flag triggered on " + submission.id)

                    if(article_error_flag==False):
                
                        replied_database = pd.read_csv("replied_articles.csv",index_col=[0])
                        nReplies = len(replied_database)

                        keywords = get_keywords(parsed_article)
                        keywords_string = ' '.join(keywords)

                        similar_database = check_keywords(keywords_string, replied_database)

                        #print(similar_database)

                        #similar_database = check_similarity(article_title, replied_database)
                        max_similarity_record = similar_database[similar_database.similarity_value == similar_database.similarity_value.max()]

                        similarity_reply = "\n***\n" + "Article keywords: " + keywords_string

                        if (not(max_similarity_record.empty)):
                            try:
                                if (max_similarity_record.loc[0]["similarity_value"]>0.50):
                                    similarity_reply = similarity_reply + "\n\nThe keywords are " + str(round(max_similarity_record.loc[0]["similarity_value"]*100)) + "% similar to: [" + max_similarity_record.loc[0]["title"] + "](https://www.reddit.com/r/singapore/comments/" + max_similarity_record.loc[0]["id"] + ")"
                            except:
                                pass

                        print("New entry for " + submission.id + " in Database at " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

                        append_to_database = pd.DataFrame({"id": [submission.id], "title": [article_title], "keywords": [keywords_string]})
                        replied_database = pd.concat([replied_database, append_to_database])
                        replied_database.to_csv('replied_articles.csv')
                    else:
                        print("there was an article error")
                        #there was an article error

                    fullreply = "Title: " + article_title + " \n\n"
                    fullreply = fullreply + articlereply + similarity_reply + "\n\n" + str(nReplies) + " articles replied in my database. " + "[v1.5c - added Lemma tokens and Tensorflow USE](" + "https://github.com/Wormsblink/sneakpeakbot" + ") | Happy Holidays! | PM SG_wormsbot if bot is down."
                    submission.reply(fullreply)
                    #print(fullreply)
                    print("Replied to submission " + submission.id + " by " + submission.author.name)

            else:
                fullreply=""

def check_top_level_comments(submission):
    bot_replied_flag = False
    for top_level_comment in submission.comments:
        if (top_level_comment.author=="SG_wormsbot"):
            bot_replied_flag = True
    return bot_replied_flag

def get_replied_articles():
        
        if not os.path.isfile("replied_articles.csv"):
                blank_database=pd.DataFrame(columns=['id','title', 'keywords'])
                blank_database.to_csv("replied_articles.csv")
                replied_articles_id = []
        else:
                replied_database = pd.read_csv("replied_articles.csv")
                replied_articles_id = replied_database['id'].tolist()
                #replied_articles_id = replied_articles_id.split("\n")

        return replied_articles_id

def get_error_log():
        
        if not os.path.isfile("error_log.csv"):
                blank_database=pd.DataFrame(columns=['id','URL'])
                blank_database.to_csv("error_log.csv")
                error_database = []
        else:
                error_database = pd.read_csv("error_log.csv")
                error_database_id = error_database['id'].tolist()
                #replied_articles_id = replied_articles_id.split("\n")

        return error_database_id


def get_approved_list():
    with open("approved_sites_list.txt", "r") as f:
        approved_list = f.read()
        approved_list = list(filter(None, approved_list.split("\n")))

    return approved_list

def parse_article(article_url):

    article = Article(article_url)
    article.download()

    #Currently Broken
    #if(html.find(class_='paid-premium st-flag-1') == 'For Subscribers'):
    #    return("READ TEXT ERROR")
    
    article.parse()
    
    newstext = article.text

    return newstext

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

def get_keywords(parsed_article):

    word_frequencies = get_word_frequencies(parsed_article)

    word_frequencies = {k.lower(): v for k, v in word_frequencies.items()}

    keywords = sorted(word_frequencies, key=word_frequencies.get, reverse = True)[:8]

    return keywords

def check_keywords(keywords_string, replied_database):

    #Similarity by keywords

    if(type(keywords_string) is float):
        keywords_string = str(keywords_string)

    similar_database = replied_database.copy().tail(min(len(replied_database.index),100))
    similar_database["similarity_value"] = ""
    replied_database_keywords = replied_database["keywords"].tolist()

    temp_new_keywords = nlp2(' '.join([str(t) for t in keywords_string.split() if (not t in list(STOP_WORDS) or not t in punctuation)]))

    for replied_keywords in replied_database_keywords:
        temp_replied_keywords = nlp2(' '.join([str(t) for t in replied_keywords.split() if (not t in list(STOP_WORDS) or not t in punctuation)]))
        
        similarity_value = temp_new_keywords.similarity(temp_replied_keywords)
        
        similar_database["similarity_value"][similar_database.keywords == replied_keywords] = similarity_value

    return similar_database

def check_similarity(article_title, replied_database):

    #Similarity by title

    similar_database = replied_database.copy().tail(min(len(replied_database.index),100))
    similar_database["similarity_value"] = ""
    replied_articles_titles = replied_database["title"].tolist()

    temp_article_title = nlp(' '.join([str(t) for t in article_title.split() if (not t in list(STOP_WORDS) or not t in punctuation)]))
    
    for replied_title in replied_articles_titles:
        temp_replied_title = nlp(' '.join([str(t) for t in replied_title.split() if (not t in list(STOP_WORDS) or not t in punctuation)]))
        
        similarity_value = temp_article_title.similarity(temp_replied_title)
        similar_database["similarity_value"][similar_database.title == replied_title] = similarity_value

    return similar_database

def get_summary(newstext):

    #print(newstext)

    if not newstext:
        
        error_database = get_error_log()

        append_to_database = pd.DataFrame({"id": [submission.id], "URL": [submission.url]})
                        error_database = pd.concat([error_database, append_to_database])
                        error_database.to_csv('error_log.csv')

        return("Article parsing Failed. This may be edue to non-standard HTML elements in the article. This event has been logged into error database.")
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

    word_frequencies = get_word_frequencies(text)
    
    max_frequency=max(word_frequencies.values())
    
    for word in word_frequencies.keys():
        word_frequencies[word]=word_frequencies[word]/max_frequency
    sentence_tokens= [sent for sent in doc.sents]
    sentence_scores = {}
    
    for sent in sentence_tokens:
        for word in sent:
            if word.lemma_ in word_frequencies.keys():
                if sent not in sentence_scores.keys():                            
                    sentence_scores[sent]=word_frequencies[word.lemma_]
                else:
                    sentence_scores[sent]+=word_frequencies[word.lemma_]
    
    select_length=int(len(sentence_tokens)*per)
    summary=nlargest(select_length, sentence_scores,key=sentence_scores.get)
    
    final_summary=[word.text for word in summary]
    summary=''.join(final_summary)

    return summary

def get_word_frequencies(text):
    
    doc= nlp(text)
    word_frequencies={}
    
    for word in doc:
        if word.text.lower().isalpha():
            if word.text.lower() not in punctuation:
                if len(word.text)>1:
                    if word.lemma_ not in list(STOP_WORDS):
                        if word.lemma_ not in word_frequencies.keys():
                            word_frequencies[word.lemma_] = 1
                        else:
                            word_frequencies[word.lemma_] += 1
    return word_frequencies

def get_stop_words():

    with open("stop_words_list.txt", "r") as f:
        stop_words_list = f.read()
        stop_words_list = list(filter(None, stop_words_list.split("\n")))

    return stop_words_list

# Main

r = bot_login()

stop_words_list = get_stop_words()

for word in stop_words_list:
    nlp.Defaults.stop_words.add(word)

#run_bot(r, get_replied_articles(),get_approved_list())

while True:
   try:
       run_bot(r, get_replied_articles(),get_approved_list())
       time.sleep(60)
   except Exception as err:
       print(traceback.format_exc())
       print("Fatal error at " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ", " + str(err))
       time.sleep(36000)
