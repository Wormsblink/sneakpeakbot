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

        return  visual

#run test case
visualizer = visualizeArticle("1gb9yyz")

print(visualizer)