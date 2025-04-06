import os
import logging
from heapq import nlargest
import re
import config

from string import punctuation

import getlists

logging.disable(logging.WARNING)
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import pandas as pd
import spacy
import spacy_universal_sentence_encoder
nlp = spacy.load('en_core_web_sm')

import asent
nlp.add_pipe('asent_en_v1')

from pyate.term_extraction_pipeline import TermExtractionPipeline
nlp.add_pipe("combo_basic")

nKeywords = config.nKeywords

nlp2 = spacy_universal_sentence_encoder.load_model('en_use_lg')

stop_words_list = getlists.stop_words("stop_words_list.txt")

from spacy.lang.en.stop_words import STOP_WORDS

for word in stop_words_list:
    nlp.Defaults.stop_words.add(word)

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

def get_keywords(parsed_article):
    doc = nlp(parsed_article)
    keywords_series = doc._.combo_basic.sort_values(ascending=False)[:nKeywords]

    keywords = keywords_series.index.values.tolist()

    return keywords

def get_keywords_by_frequency(parsed_article):

    #not in use

    word_frequencies = get_word_frequencies(parsed_article)

    word_frequencies = {k.lower(): v for k, v in word_frequencies.items()}

    keywords = sorted(word_frequencies, key=word_frequencies.get, reverse = True)[:8]

    return keywords

def get_keywords_OLD(parsed_article):

    #this function is deprecated

    doc = nlp(parsed_article)
    keywords = {}

    for chunk in doc.noun_chunks:
        base_noun = chunk.root.text.lower()

        if base_noun not in punctuation and base_noun not in list(STOP_WORDS):
            if chunk.root.text not in keywords.keys():
                keywords[chunk.root.text]=1
            else:
                keywords[chunk.root.text]+=1

    keywords = sorted(keywords, key=keywords.get, reverse = True)[:5]

    return keywords


def check_keywords(keywords_string, replied_database):

    #Similarity by keywords

    if(type(keywords_string) is float):
        keywords_string = str(keywords_string)

    similar_database = replied_database.copy().tail(min(len(replied_database.index),config.similaritylength))
    similar_database["similarity_value"] = ""
    replied_database_keywords = replied_database["keywords"].tolist()

    temp_new_keywords = nlp2(' '.join([str(t) for t in keywords_string.split() if (not t in list(STOP_WORDS) or not t in punctuation)]))

    for replied_keywords in replied_database_keywords:
        temp_replied_keywords = nlp2(' '.join([str(t) for t in replied_keywords.split() if (not t in list(STOP_WORDS) or not t in punctuation)]))
        
        similarity_value = temp_new_keywords.similarity(temp_replied_keywords)
        
        similar_database.loc[similar_database['similarity_value'] == replied_keywords] = similarity_value

        #similar_database["similarity_value"][similar_database.keywords == replied_keywords] = similarity_value

    return similar_database

def check_similarity(article_title, replied_database):

    #Similarity by title - currently not in use

    similar_database = replied_database.copy().tail(min(len(replied_database.index),config.similaritylength))
    similar_database["similarity_value"] = ""
    replied_articles_titles = replied_database["title"].tolist()

    temp_article_title = nlp(' '.join([str(t) for t in article_title.split() if (not t in list(STOP_WORDS) or not t in punctuation)]))
    
    for replied_title in replied_articles_titles:
        temp_replied_title = nlp(' '.join([str(t) for t in replied_title.split() if (not t in list(STOP_WORDS) or not t in punctuation)]))
        
        similarity_value = temp_article_title.similarity(temp_replied_title)
        similar_database["similarity_value"][similar_database.title == replied_title] = similarity_value

    return similar_database

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

def get_summary(newstext):

    #print(newstext)

    if not newstext:
        
        error_database = getlists.error_log("error_log.csv")

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

def get_sentiment(analysistext):
    doc = nlp(analysistext)
    return doc._.polarity.compound

def classify_sentiment(score):
    if (-1.00 <= score < -0.75):
        return "Fall of Singapore"
    elif(-0.75 <= score < -0.65):
        return "Calamity"
    elif(-0.65 <= score < -0.50):
        return "Disastrous"
    elif(-0.50 <= score < -0.30):
        return "Terrible"
    elif(-0.30 <= score < -0.20):
        return "Bad"
    elif(-0.20 <= score < 0.20):
        return "Neutral"
    elif(0.20 <= score < 0.30):
        return "Good"
    elif(0.30 <= score < 0.50):
        return "Fantastic"
    elif(0.50 <= score < 0.65):
        return "Miraculous"
    elif(0.65 <= score < 0.75):
        return "Estatic"
    elif(0.75 <= score < 1.00):
        return "Glory to Singapore"
    else:
        return "N/A"