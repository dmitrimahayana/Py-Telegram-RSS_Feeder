"""
Tutorial Create BOT Telegram
1. Go to telegram and search @botfather
2. Create a New BOT
3. Save the Token
4. Change BOT setting to be allowed join a group
5. Run this url https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
6. Get Channel/Chat ID
"""
import os
import requests
import datetime
import feedparser
import psycopg2
import pytz
import time
import re
import sys
import socket
import pandas as pd
from dotenv import load_dotenv
from config_local import postgres_config, local_pc_name
# from extract_project_info import *

load_dotenv()  # take environment variables from .env.`

BOT_TOKEN = os.environ.get('BOT_TOKEN')  # the one you saved in previous step
BOT_CHANNEL_ID = os.environ.get('BOT_CHANNEL_ID')  # don't forget to add this


def query_insert_postgres(id, title, link, summary):
    host = postgres_config["host"]
    if socket.gethostname() != local_pc_name:
        host = "postgresdb"

    conn = psycopg2.connect(host=host,
                            port=postgres_config["port"],
                            database=postgres_config["database"],
                            user=postgres_config["user"],
                            password=postgres_config["password"], )

    with conn.cursor() as cur:
        sql = "INSERT INTO rss_upwork(id, title, link, summary) VALUES (%s, %s, %s, '');"
        cur.execute(sql, (id, title, link))
        conn.commit()


def send_message(message):
    response = requests.get(
        f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={BOT_CHANNEL_ID}&text={message}')
    print("Telegram API response code:", response.status_code, response.reason)
    if response.status_code == 200:
        print(message)
    else:
        print(f"BOT_TOKEN: {BOT_TOKEN} CHANNEL_ID:{BOT_CHANNEL_ID}")


def read_rss(page=10):
    # Dict
    data = []

    # Read mapping file
    df_list_rss = pd.read_excel("./Mapping RSS/Mapping.xlsx", sheet_name="Input")
    df_list_rss = df_list_rss[df_list_rss["Active"] == "Yes"]

    # Iterate mapping data
    for index, row in df_list_rss.iterrows():
        url = str(row["URL"]).replace("paging=0%3B10", f"paging=0%3B{page}")
        skill = row["Skill"]
        feed = feedparser.parse(url)

        # # Check if the current hour is between 8 PM and 8 AM
        # current_hour = datetime.datetime.now().hour
        # if 20 <= current_hour or current_hour < 8:
        #     # Main task
        #     print(f"Running {skill} task...")
        # else:
        #     print(f"Outside of the time range. Exiting {skill} task...")
        #     sys.exit()

        # with sync_playwright() as playwright:
        #     browser, page = open_browser(playwright)
        counter = 0
        for entry in feed.entries:
            # Create dict
            dict_feed = {
                "job_id": datetime.datetime.now(),
                "title": entry.title,
                "link": entry.link,
                "summary": entry.summary,
                "published": entry.published,
            }
            # Format date time
            date_format = "%a, %d %b %Y %H:%M:%S %z"
            date_object = datetime.datetime.strptime(dict_feed["published"], date_format)
            gmt_plus_7 = pytz.timezone('Etc/GMT-7')
            converted_date_gmt7 = date_object.astimezone(gmt_plus_7)
            formatted_date = converted_date_gmt7.strftime('%Y-%m-%d %H:%M:%S')
            # Format telegram bot message
            id = dict_feed['link']
            title = dict_feed['title'].replace("'", "").replace("&amp;", " ").replace("  ", " ")
            title = re.sub(r'[^a-zA-Z0-9\s]+', '', title)
            link = dict_feed['link']
            # Query database
            try:
                # Insert data to postgres
                query_insert_postgres(id, title, link, "")  # Insert to postgres db
                # Extract job details
                # jobs_posted, hire_rate, budget, status = scrape_upwork(page, link)  # scrape job info with playwright
                message = (f'Job Title: {title}'
                           f'\nSkill: {skill}'
                           f'\nPublished: {formatted_date}'
                           # f'\nClient Total Jobs: {jobs_posted}'
                           # f'\nHire Rate: {hire_rate}'
                           # f'\nJob Budget: {budget}'
                           # f'\nJob Type: {status}'
                           f'\nLink: {link}')
                # Send telegram bot message
                send_message(message)
                print(message)
                time.sleep(1)
            except Exception as e:
                print(f"No message for Telegram Bot due to {e}")
                pass
            data.append(dict_feed)
            counter = counter + 1

            # close_browser(browser)


if __name__ == "__main__":
    read_rss()
