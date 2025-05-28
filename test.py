import ArticleParse
import spacy
import asent
import login
import nlpv2
from pyate.term_extraction_pipeline import TermExtractionPipeline

r = login.bot_login()

def test_article_text(commentID):
        ArticleURL = r.submission(id=commentID).url.split('?')[0]
        ArticleText = ArticleParse.parse_text(ArticleURL)

        return ArticleText

def test_keywords(commentID):
        ArticleURL = r.submission(id=commentID).url.split('?')[0]
        ArticleText = ArticleParse.parse_text(ArticleURL)

        keywords = nlpv2.get_keywords(ArticleText)

        return keywords

def test_article_sentiment(commentID):
        ArticleURL = r.submission(id=commentID).url.split('?')[0]
        ArticleText = ArticleParse.parse_text(ArticleURL)
        
        nlp = spacy.load('en_core_web_sm')
        nlp.add_pipe("asent_en_v1")
        doc = nlp(ArticleText)
        visual = asent.visualize(doc, style="prediction")

        print(doc._.polarity.compound)

        return  visual

def test_title_sentiment(commentID):
        ArticleURL = r.submission(id=commentID).url.split('?')[0]
        ArticleTitle = ArticleParse.get_title(ArticleURL)
        
        nlp = spacy.load('en_core_web_sm')
        nlp.add_pipe("asent_en_v1")
        doc = nlp(ArticleTitle)
        visual = asent.visualize(doc, style="prediction")

        print (doc._.polarity.compound)

        return visual

def test_nlp(commentID):
        ArticleURL = r.submission(id=commentID).url.split('?')[0]
        ArticleText = ArticleParse.parse_text(ArticleURL)
        nlp = spacy.load('en_core_web_sm')
        nlp.add_pipe('asent_en_v1')
        nlp.add_pipe("combo_basic")

        doc = nlp(ArticleText)
        return doc.text

# Testing Below

commentID = "1jssu43"

#TestReply = test_article_text(commentID)
TestReply = test_keywords(commentID)
#TestReply = test_article_sentiment(commentID)
#TestReply = test_title_sentiment(commentID)
#TestReply = test_nlp(commentID)

print(TestReply)