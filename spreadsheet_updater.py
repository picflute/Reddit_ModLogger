#!/usr/local/bin/python3.4

import sys
import time as sleep
from datetime import datetime, date, time
import datetime as datetimebs
import gspread
from oauth2client.client import SignedJwtAssertionCredentials
import json
import mysql_handler as db


def update_automod_last_month(work_sheet, subreddit):
    work_range = work_sheet.range("A1:AZ30")
    work_range[1].value = "total"
    reasons = []

    current_day = datetime.combine(date.today(), time())
    epoch_current_day = int (current_day.strftime("%s"))

    for cell in work_range:
        if cell.row == 1 and not cell.value == "" and not cell.value == "0":
            reasons.append(cell.value)
        else:
            cell.value = ""

    for i in range(1, 30):
        data = db.get_automod_by_day(epoch_current_day - (86400 * i), subreddit)

        work_range[i * 52].value = datetime.fromtimestamp(int(data[0][1])).strftime("%d/%m/%y")
        work_range[i * 52 + 1].value = "=SUM(C" + str(i+1) + ":AZ" + str(i+1) + ")"

        if len(data) <= 0:
            print("No data for an update available")
            sys.exit()

        print("Update cell range")

        for row in data:
            if not row[2] in reasons:
                reasons.append(row[2])
                work_range[len(reasons)].value = row[2]
            work_range[i * 52 + reasons.index(row[2]) + 1].value = row[3]


    for cell in work_range:
        if not cell.col == 1 and cell.value == "" and cell.col <= len(reasons) + 1:
            cell.value = 0

    print("Update spreadsheet")

    update_work_sheet(work_sheet, work_range)

def monthly_mod_matrix(sheet, subreddit):
    first_day_of_this_month = date.today().replace(day=1)
    epoch_current_day = sleep.time()
    epoch_first_day_of_this_month = int(first_day_of_this_month.strftime("%s"))

    if date.today().day == 1 or date.today().day == 2:
        last_month = (first_day_of_this_month - datetimebs.timedelta(days=1))
        last_month = last_month.replace(day=1)
        epoch_first_day_last_month = int(last_month.strftime("%s"))
        results = db.get_count_by_action_for_timeframe(epoch_first_day_last_month, epoch_first_day_of_this_month, subreddit)

        try:
            work_sheet = sheet.worksheet(last_month.strftime("%b %Y"))
        except gspread.WorksheetNotFound:
            work_sheet = sheet.add_worksheet(last_month.strftime("%b %Y"), 50, 52)

        work_range = work_sheet.range("A1:AZ50")

        generated_range = generate_modlog_range(work_range, results)



    results = db.get_count_by_action_for_timeframe(epoch_first_day_of_this_month, epoch_current_day, subreddit)

    try:
        work_sheet = sheet.worksheet(first_day_of_this_month.strftime("%b %Y"))
    except gspread.WorksheetNotFound:
        work_sheet = sheet.add_worksheet(first_day_of_this_month.strftime("%b %Y"), 50, 52)

    work_range = work_sheet.range("A1:AZ50")

    generated_range = generate_modlog_range(work_range, results)

    update_work_sheet(work_sheet, generated_range)

    work_sheet = sheet.worksheet("Burden Sharing")
    work_range = work_sheet.range("A2:A50")

    date_string = first_day_of_this_month.strftime("%b %Y")

    for cell in work_range:
        if cell.value == date_string:
            cell.value = "=\"" + cell.value + "\""
            break
        elif cell.value == "":
                cell.value = "=\"" + date_string + "\""
                break
        else:
            cell.value = "=\"" + cell.value + "\""

    update_work_sheet(work_sheet, work_range)


def generate_mod_matrix(epoch_time, subreddit):
    first_day_of_the_month = datetime.fromtimestamp(epoch_time).replace(day=1)
    first_day_of_following_month = (first_day_of_the_month + datetimebs.timedelta(days=35)).replace(day=1)

    results = db.get_count_by_action_for_timeframe(int(first_day_of_the_month.strftime("%s")), int(first_day_of_following_month.strftime("%s")), subreddit)

    try:
        work_sheet = sheet.worksheet(first_day_of_the_month.strftime("%b %Y"))
    except gspread.WorksheetNotFound:
        work_sheet = sheet.add_worksheet(first_day_of_the_month.strftime("%b %Y"), 50, 52)

    work_range = work_sheet.range("A1:AZ50")

    generated_range = generate_modlog_range(work_range, results)

    update_work_sheet(work_sheet, work_range)

    work_sheet = sheet.worksheet("Burden Sharing")
    work_range = work_sheet.range("A2:A50")

    date_string = first_day_of_the_month.strftime("%b %Y")

    for cell in work_range:
        if cell.value == date_string:
            break
        elif cell.value == "":
                cell.value = "=\"" + date_string + "\""
                break
        else:
            cell.value = "=\"" + cell.value + "\""

    update_work_sheet(work_sheet, work_range)




def update_work_sheet(work_sheet, work_range):
    while(1):
        try:
            work_sheet.update_cells(work_range)
            break
        except gspread.exceptions.HTTPError:
            sleep.sleep(10)
            continue
        except Exception as err:
            print("Unknown exception occured while updating the spreadsheet:")
            print(err)
            break



def generate_modlog_range(work_range, results):
    if results == []:
        for cell in work_range:
            cell.value = ""
        return work_range

    work_range[1].value = "mod totals"
    actions = []
    mods = []

    for cell in work_range:
        if cell.row == 1 and not cell.value == "" and not cell.value == "0":
            actions.append(cell.value)
        else:
            cell.value = ""

    print("Update cell range")

    for row in results:
        if not row[0] in mods:
            mods.append(row[0])
            mod_row = (mods.index(row[0]) + 1)
            work_range[mod_row * 52].value = row[0]
            work_range[mod_row * 52 + 1].value = "=SUM(C" + str(mod_row + 1) + ":AZ" + str(mod_row + 1) + ")"
        if not row[1] in actions:
            actions.append(row[1])
            work_range[actions.index(row[1]) + 1].value = row[1]
        work_range[(mods.index(row[0]) + 1) * 52 + actions.index(row[1]) + 1].value = row[2]

    for cell in work_range:
        if not cell.col == 1 and cell.value == "" and cell.row <= len(mods) + 1 and cell.col <= len(actions) + 1:
            cell.value = 0

    work_range[(len(mods) + 1) * 52].value = "total"
    work_range[(len(mods) + 1) * 52 + 1].value = "=SUM(B2:B" + str(len(mods)) + ")"

    return work_range

def update_subreddit_log(spreadsheet_url, subreddit):

    json_key = json.load(open('gspread_connection.json'))

    scope = ['https://spreadsheets.google.com/feeds']

    print("Connecting to Google")

    credentials = SignedJwtAssertionCredentials(json_key['client_email'], bytes(json_key['private_key'], "utf-8"), scope)
    gc = gspread.authorize(credentials)

    try:
    	sheet = gc.open_by_url(spreadsheet_url)
    except:
    	print("Don't forget to share the spreadsheet with the following e-mail!")
    	print(json_key["client_email"])
    	sys.exit()

    print("Update AutoMod stats")

    try:
        work_sheet = sheet.worksheet("AutoMod Last Month")
    except gspread.WorksheetNotFound:
        work_sheet = sheet.add_worksheet("AutoMod Last Month", 50, 52)

    update_automod_last_month(work_sheet, subreddit)

    print("Update Mod Matrix")

    monthly_mod_matrix(sheet, subreddit)

