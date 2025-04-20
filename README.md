1. Setup

  From termimal - pip install spacy, newspaper3k, praw, bs4, pandas, spacy-universal-sentence-encoder, asent, pyate, xml_html_clean

  then run - spacy download en_core_web_sm

  also download en_use_lg model for spacy (pip install https://github.com/MartinoMensio/spacy-universal-sentence-encoder/releases/download/v0.4.6/en_use_lg-0.4.6.tar.gz#en_use_lg-0.4.6)

2. Package conflcits
   
  numpy version 2.0.0 or greater is incompatible with spacy. Downgrade to version 1.26.4 until thinc is fixed
