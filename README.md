# Reddit_ModLogger
Creates a mod matrix and an overview while storing moderator activity on a daily base.

# Requirements:

* MySQL database
* Python 3.4+

 
# Required Modules:

* praw
* mysql connector
* gspread
 
# Setup:

Follow the instructions on this webpage to obtain the google OAuth2 credentials (just until you got the .json file)
http://gspread.readthedocs.org/en/latest/oauth2.html

Rename this file to: "gspread_connection.json"

Enter the appropriate data into mysql_connection.config and reddit_connection.config.
For the reddit connection you have to setup your own reddit app (in the reddit preferences). If you have issues with that PM me! [/u/Erasio]

[/u/Erasio]: <https://www.reddit.com/message/compose/?to=Erasio>

Copy this spreadsheet: https://docs.google.com/spreadsheets/d/1pEjeoU6HJE94c78o8qTfVuoAFxnAEuepEdcw6EJNhgs/edit?usp=sharing

Add all moderators that should not be counted as humans in the "Excludes" table (totals has to stay there).

Go in the start.py file and enter the desired subreddit name and the spreadsheet url it should send the data to.

Share the spreadsheet with the Email address your bot got from the first step.

Done!
