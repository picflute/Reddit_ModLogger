#!/usr/local/bin/python3.4

import mysql.connector
from mysql.connector import errorcode
import sys
import warnings
import json
from datetime import datetime, date, time

warnings.simplefilter("ignore", ResourceWarning)

mysql_config = json.load(open('mysql_connection.config'))
user_name = mysql_config["user_name"]
password = mysql_config["password"]
host = mysql_config["host"]
database = mysql_config["database"]

try:
    sql = mysql.connector.connect(user=user_name,
                                password=password,
                                host=host,
                                database=database)
    cursor = sql.cursor()

except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with your user name or password")
    sys.exit()
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
    sys.exit()
  else:
    print(err)
    sys.exit()

TABLES = {}
TABLES['modlog'] = (
    "CREATE TABLE modlog ("
        "id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,"
        "day INT NOT NULL,"
        "moderator VARCHAR(20) NOT NULL,"
        "action VARCHAR(20) NOT NULL,"
        "count INT NOT NULL,"
        "subreddit VARCHAR(20) NOT NULL,"
        "CONSTRAINT unique_entries UNIQUE (day, moderator, action, subreddit)"
        ") ENGINE=InnoDB;")

TABLES['automod'] = (
    "CREATE TABLE automod ("
        "id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,"
        "day INT NOT NULL,"
        "reason VARCHAR(50) NOT NULL,"
        "count INT NOT NULL,"
        "subreddit VARCHAR(20) NOT NULL,"
        "CONSTRAINT unique_entries UNIQUE (day, reason, subreddit)"
        ") ENGINE=InnoDB;")

for name, ddl in TABLES.items():
    try:
        print("Creating table: ".format(name), end='')
        cursor.execute(ddl)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("OK (Existed)")
        else:
            print()
            print(err.msg)
            print(ddl)
            sys.exit()
    else:
        print("OK")


def insert_sql(statement):
    try:
        cursor.execute(statement)
        sql.commit()
        return 1
    except Exception as err:
        print("Exception while inserting...")
        print(err)
        return 0


def select_sql(statement):
    try:
        cursor.execute(statement)
        return cursor.fetchall()
    except Exception as err:
        print("Exception selecting...")
        print(err)
        return 0


def insert_modlog(day, mod, action, count, subreddit):
    statement = "INSERT INTO modlog (day, moderator, action, count, subreddit) VALUES({day}, '{mod}', '{action}', {count}, '{subreddit}');".format(day=day, mod=mod, action=action, count=count, subreddit=subreddit)
    return insert_sql(statement)


def insert_automod(day, reason, count, subreddit):
    reason = (reason[:50] + '..') if len(reason) > 50 else reason
    statement = "INSERT INTO automod (day, reason, count, subreddit) VALUES({day}, '{reason}', {count}, '{subreddit}');".format(day=day, reason=reason, count=count, subreddit=subreddit)
    return insert_sql(statement)


def get_modlog_by_day(day, subreddit):
    statement = "SELECT * FROM modlog WHERE day={day};".format(day=day)
    return select_sql(statement)


def get_automod_by_day(day, subreddit):
    statement = "SELECT * FROM automod WHERE day={day};".format(day=day)
    return select_sql(statement)

def get_count_by_action_for_timeframe(epoch_time_1, epoch_time_2, subreddit):
    if epoch_time_1 > epoch_time_2:
        temp_epoch_time = epoch_time_2
        epoch_time_2 = epoch_time_1
        epcoh_time_1 = temp_epoch_time
    statement = "SELECT moderator, action, SUM(count) FROM modlog WHERE day > {start_epoch_time} AND day < {end_epoch_time} AND subreddit = '{subreddit}' GROUP BY moderator, action;".format(start_epoch_time=int(epoch_time_1), end_epoch_time=int(epoch_time_2), subreddit=subreddit)
    return select_sql(statement)

