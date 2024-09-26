import praw
import config
from datetime import datetime

def bot_login():
        print ("Logging in...")
        r = praw.Reddit(username = config.username,
                        password = config.password,
                        client_id = config.client_id,
                        client_secret = config.client_secret,
                        user_agent = "Sneakpeakbot v1.5d")
        print("Log in successful!")
        print(datetime.now().strftime('%d %b %y %H:%M:%S'))
        return r
