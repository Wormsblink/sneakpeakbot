import ArticleParse
import spacy
import asent
import login

r = login.bot_login()

def visualizeArticle(commentID):
        ArticleURL = r.submission(id=commentID).url
        ArticleText = ArticleParse.parse_text(ArticleURL)
        
        nlp = spacy.load('en_core_web_sm')
        nlp.add_pipe("asent_en_v1")
        doc = nlp(ArticleText)
        visual = asent.visualize(doc, style="prediction")

        print(doc._.polarity.compound)

        return  visual

#run test case

def visualizeTitle(commentID):
        ArticleURL = r.submission(id=commentID).url
        ArticleTitle = ArticleParse.get_title(ArticleURL)
        
        nlp = spacy.load('en_core_web_sm')
        nlp.add_pipe("asent_en_v1")
        doc = nlp(ArticleTitle)
        visual = asent.visualize(doc, style="prediction")

        print (doc._.polarity.compound)

        return visual

commentID = "1k3f0np"
        
#visualizer = visualizeArticle(commentID)
visualizer = visualizeTitle(commentID)

print(visualizer)