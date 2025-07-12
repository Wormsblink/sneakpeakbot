from datetime import datetime
import pandas as pd

import ArticleParsev2
import nlpv2
import config


def run_bot(r, replied_articles_id,approvedlist):

    for submission in r.subreddit(config.subreddit).new(limit=config.submissionlimit):

    #Disabled bot call comment
    #for comment in r.subreddit('singapore').comments(limit = 20):
        #if ("!sneakpeak" in comment.body): 

            #submission=comment.submission

            if ((submission.selftext=="" and submission.url.startswith(tuple(approvedlist))) and not submission.url.startswith("https://www.reddit.com")):

                fullreply = ""
                article_title = "Title Error"
                articlereply = ""
                similarity_reply = ""
                parsed_article = ""
                keywords = ""
                keywords_string ="Keywords Error"
                keywords_reply = ""
                nReplies = 0
                article_sentiment = 0
                sentiment_reply = ""

                try:
                    replied_database = pd.read_csv(config.repliedlist,index_col=[0])
                    nReplies = len(replied_database)
                except:
                    pass

                if (submission.id in replied_articles_id):
                    pass

                elif (check_top_level_comments(submission)==True):
                    print("bot comment detected in top level comments for " + submission.id + ". This may be an error in the database")

                else:
                    article_error_flag = False

                    try:
                        article_title = ArticleParsev2.get_title(submission.url)
                        parsed_article=ArticleParsev2.parse_text(submission.url)
                        articlereply = nlpv2.get_summary(parsed_article)
                    except:
                        article_error_flag = True

                    if(article_error_flag==False):
                
                        keywords = nlpv2.get_keywords(parsed_article)
                        keywords_string = ', '.join(keywords)

                        article_sentiment = round(nlpv2.get_sentiment(articlereply),2)
                        title_sentiment = round(nlpv2.get_sentiment(article_title),2)

                        sentiment_reply = "Title mood: " + nlpv2.classify_sentiment(title_sentiment) + " (sentiment value " + str(title_sentiment) + "). \n\n" "Article mood: " + nlpv2.classify_sentiment(article_sentiment) + " (sentiment value " + str(article_sentiment) + ")\n\n"

                        similar_database = nlpv2.check_keywords(keywords_string, replied_database)

                        #print(similar_database) 

                        #similar_database = check_similarity(article_title, replied_database)
                        max_similarity_record = similar_database[similar_database.similarity_value == similar_database.similarity_value.max()]

                        keywords_reply = "Article keywords: " + keywords_string + "\n\n"

                        if (not(max_similarity_record.empty)):
                            try:
                                if (max_similarity_record.loc[0]["similarity_value"]>config.similaritypercent):
                                    similarity_reply = "The keywords are " + str(round(max_similarity_record.loc[0]["similarity_value"]*100)) + "% similar to: [" + max_similarity_record.loc[0]["title"] + "](https://www.reddit.com/r/singapore/comments/" + max_similarity_record.loc[0]["id"] + ")"
                            except:
                                pass
                                
                        print("New entry for " + submission.id + " in Database at " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

                        append_to_database = pd.DataFrame({"id": [submission.id], "title": [article_title], "keywords": [keywords_string], "sentiment": [article_sentiment]})
                        replied_database = pd.concat([replied_database, append_to_database])
                        replied_database.to_csv(config.repliedlist)
                    else:
                        articlereply = "There was an error reading the article text. This may be due to paywall / anti ad-blocker."
                        error_database = pd.read_csv(config.errorlist,index_col=[0])
                        append_to_database = pd.DataFrame({"id": [submission.id], "title": [article_title], "keywords": [keywords_string], "resolved": ["No"]})
                        error_database = pd.concat([error_database, append_to_database])
                        error_database.to_csv(config.errorlist)

                    fullreply ="Title: " + article_title + " \n\n"
                    fullreply = fullreply + keywords_reply + sentiment_reply
                    fullreply = fullreply + articlereply + similarity_reply + "\n***\n" + "Article id " + submission.id + " | " + str(nReplies) + " articles replied in my database. [v" + config.version + "](https://github.com/Wormsblink/sneakpeakbot) " + "| PM SG_wormsbot if bot is down."
                    
                    if (config.replymode == True):
                        submission.reply(fullreply)
                    else:
                        print(fullreply)

                    print("Replied to submission " + submission.id + " by " + submission.author.name)

            else:
                pass

def check_top_level_comments(submission):
    bot_replied_flag = False
    for top_level_comment in submission.comments:
        if (top_level_comment.author==config.username):
            bot_replied_flag = True
    return bot_replied_flag