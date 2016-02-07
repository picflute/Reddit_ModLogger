#!/usr/local/bin/python3.4

import praw
import time
import requests
from requests.auth import HTTPBasicAuth
import warnings
import sys
import json

warnings.simplefilter("ignore", ResourceWarning)


_oauth_scopes = {"modlog"}
_oauth_start = 0
_oauth_length = 3300

def init_reddit_session():
    counter = 0
    while 1:
        if counter >= 20:
            log("Retrying too much. 7 minutes, 20 attempts")
            sys.exit()
        try:
            global _oauth_start
            global _oauth_length

            try:
                reddit_login = json.load(open('reddit_connection.config'))
            except (OSError, IOError):
                print("Couldn't open reddit_connection.config")
                sys.exit()

            user_agent = reddit_login["user_agent"]
            client_id = reddit_login["client_id"]
            client_secret = reddit_login["client_secret"]
            redirect_uri = reddit_login["redirect_uri"]
            username = reddit_login["username"]
            password = reddit_login["password"]

            print("Connecting to reddit...")
            r = praw.Reddit(user_agent=user_agent)

            print("logging in...")

            client_auth = HTTPBasicAuth(client_id, client_secret)
            headers = {"User-Agent": user_agent, "connection": "close"}
            data = {"grant_type": "password", "username": username, "password": password}
            response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, headers=headers, data=data)
            response_content = response.json()
            if "error" in response_content and response_content["error"] != 200:
                print("failed!\nResponse code = {}".format(response_content["error"]))
                return None

            token = response_content["access_token"]
            if response_content["token_type"] != "bearer":
                return None
            _oauth_start = time.time()
            _oauth_length = response_content["expires_in"] - 500
            r.set_oauth_app_info(client_id, client_secret, redirect_uri)
            r.set_access_credentials(_oauth_scopes, access_token=token)

            print("done!")

            return r
        except:
            print("Login failed... retrying in 20 seconds.")
            counter += 1
            time.sleep(20)


def destroy_reddit_session(r):
    r.clear_authentication()


def renew_reddit_session(r):
    global _oauth_start
    global _oauth_length
    if time.time() - _oauth_start >= _oauth_length:
        _oauth_start = time.time()
        print("Renewing oauth token")
        return init_reddit_session()
    return r


def send_modmail(r, subreddit, title, body):
    r.send_message("/r/"+subreddit, title, body)
    print("Sending modmail to " + subreddit)


def send_pm(r, user, title, body, from_sr=None):
    r.send_message(user, title, body, from_sr=from_sr)
    print("Sent message to /u/" + user.name)