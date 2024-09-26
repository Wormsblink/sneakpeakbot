#import default python modules
from datetime import datetime
import time
import traceback

#import other modules
import login
import getlists
import bot
import config

r = login.bot_login()

while True:
   try:
       bot.run_bot(r, getlists.replied_articles(config.repliedlist),getlists.approved_list(config.approvelist))
       time.sleep(60)
   except Exception as err:
       print(traceback.format_exc())
       print("Fatal error at " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ", " + str(err))
       time.sleep(3600)
