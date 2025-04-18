import pandas as pd
import os

def stop_words(filepath):

    with open(filepath, "r") as f:
        stop_words_list = f.read()
        stop_words_list = list(filter(None, stop_words_list.split("\n")))

    return stop_words_list

def approved_list(filepath):
    with open(filepath, "r") as f:
        approved_list = f.read()
        approved_list = list(filter(None, approved_list.split("\n")))

    return approved_list

def replied_articles(filepath):
        
        if not os.path.isfile(filepath):
                blank_database=pd.DataFrame(columns=['id','title', 'keywords','sentiment'])
                blank_database.to_csv(filepath)
                replied_articles_id = []
        else:
                replied_database = pd.read_csv(filepath)
                replied_articles_id = replied_database['id'].tolist()

        return replied_articles_id

def error_articles(filepath):

        if not os.path.isfile(filepath):
                blank_database=pd.DataFrame(columns=['id','title', 'keywords', 'resolved'])
                blank_database.to_csv(filepath)
                error_articles_id = []
        else:
                error_database = pd.read_csv(filepath)
                error_articles_id = error_database['id'].tolist()

        return error_articles_id 
    
def error_log(filepath):
        
        if not os.path.isfile(filepath):
                blank_database=pd.DataFrame(columns=['id','URL'])
                blank_database.to_csv(filepath)
                error_database = []
        else:
                error_database = pd.read_csv(filepath)
                error_database_id = error_database['id'].tolist()

        return error_database_id
