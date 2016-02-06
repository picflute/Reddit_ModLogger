#!/usr/local/bin/python3.4

import warnings
from datetime import datetime, date, time
import sys
import reddit_utils as reddit
import modlog_stats as modlog
import spreadsheet_updater

warnings.simplefilter("ignore", ResourceWarning)

r = reddit.init_reddit_session()

today_beginning = datetime.combine(date.today(), time())
epoch_today_beginning = int (today_beginning.strftime("%s"))

time_limit = epoch_today_beginning - (86400*2)

mod_actions = modlog.collect_modlog_stats(r, "leagueoflegends", time_limit=time_limit)

spreadsheet_url = ""
subreddit = ""

if subreddit == "" or spreadsheet_url == "":
	print("You have to add a subreddit and a spreadsheet url in the starter.py script in line 21 and 22 (or directly in the function update_subreddit_log in line 27)")
	sys.exit()

spreadsheet_updater.update_subreddit_log(spreadsheet_url, subreddit)
