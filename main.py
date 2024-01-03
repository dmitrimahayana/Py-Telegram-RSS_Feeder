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

import psycopg2
import requests
import datetime
import feedparser
import pytz

BOT_TOKEN = os.environ.get('BOT_TOKEN')  # the one you saved in previous step
CHANNEL_ID = os.environ.get('BOT_CHANNEL_ID')  # don't forget to add this
DB_URL = os.environ.get('COCKROACHDB_URL')


def send_message(message):
    requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHANNEL_ID}&text={message}')


def read_rss(skill, page: int = 20):
    url = ""
    data = []

    if skill == "python":
        url = f"https://www.upwork.com/ab/feed/jobs/rss?location=Americas%2CEurope%2COceania&verified_payment_only=1&q=python&sort=recency&paging=0%3B{page}&api_params=1&securityToken=d76b00a86ffa60baeb01da154db76acbc3e3fb340eb668f28c222bb46639c8703ab081313822496c9034327bdea763a7d925b795c8689537c032172bc7d66703&userUid=1183197118515154944&orgUid=1183197118523543553"
    elif skill == "datascraping":
        url = f"https://www.upwork.com/ab/feed/jobs/rss?location=Americas%2CEurope%2COceania&q=data+scraping&verified_payment_only=1&sort=recency&paging=0%3B{page}&api_params=1&securityToken=d76b00a86ffa60baeb01da154db76acbc3e3fb340eb668f28c222bb46639c8703ab081313822496c9034327bdea763a7d925b795c8689537c032172bc7d66703&userUid=1183197118515154944&orgUid=1183197118523543553"
    elif skill == "airflow":
        url = f"https://www.upwork.com/ab/feed/jobs/rss?location=Americas%2CEurope%2COceania&q=airflow&verified_payment_only=1&sort=recency&paging=0%3B{page}&api_params=1&securityToken=d76b00a86ffa60baeb01da154db76acbc3e3fb340eb668f28c222bb46639c8703ab081313822496c9034327bdea763a7d925b795c8689537c032172bc7d66703&userUid=1183197118515154944&orgUid=1183197118523543553"
    elif skill == "spark":
        url = f"https://www.upwork.com/ab/feed/jobs/rss?location=Americas%2CEurope%2COceania&q=apache+spark&verified_payment_only=1&sort=recency&paging=0%3B{page}&api_params=1&securityToken=d76b00a86ffa60baeb01da154db76acbc3e3fb340eb668f28c222bb46639c8703ab081313822496c9034327bdea763a7d925b795c8689537c032172bc7d66703&userUid=1183197118515154944&orgUid=1183197118523543553"
    elif skill == "kafka":
        url = f"https://www.upwork.com/ab/feed/jobs/rss?location=Americas%2CEurope%2COceania&q=kafka&verified_payment_only=1&sort=recency&paging=0%3B{page}&api_params=1&securityToken=d76b00a86ffa60baeb01da154db76acbc3e3fb340eb668f28c222bb46639c8703ab081313822496c9034327bdea763a7d925b795c8689537c032172bc7d66703&userUid=1183197118515154944&orgUid=1183197118523543553"
    elif skill == "machinelearning":
        url = f"https://www.upwork.com/ab/feed/jobs/rss?location=Americas%2CEurope%2COceania&verified_payment_only=1&q=machine+learning&sort=recency&paging=0%3B{page}&api_params=1&securityToken=d76b00a86ffa60baeb01da154db76acbc3e3fb340eb668f28c222bb46639c8703ab081313822496c9034327bdea763a7d925b795c8689537c032172bc7d66703&userUid=1183197118515154944&orgUid=1183197118523543553"

    feed = feedparser.parse(url)
    conn = psycopg2.connect(DB_URL)

    counter = 0
    for entry in feed.entries:
        dict_feed = {
            "job_id": datetime.datetime.now(),
            "title": entry.title,
            "link": entry.link,
            "summary": entry.summary,
            "published": entry.published,
        }
        date_format = "%a, %d %b %Y %H:%M:%S %z"
        date_object = datetime.datetime.strptime(dict_feed["published"], date_format)
        gmt_plus_7 = pytz.timezone('Etc/GMT-7')
        converted_date_gmt7 = date_object.astimezone(gmt_plus_7)
        formatted_date = converted_date_gmt7.strftime('%Y-%m-%d %H:%M:%S')
        message = (f'Job Title: {dict_feed["title"]}'
                   f'\nPublished: {formatted_date}'
                   f'\nLink: {dict_feed["link"]}')
        with conn.cursor() as cur:
            try:
                sql = "INSERT INTO rss_upwork(id_date,title,link,summary) VALUES (%s, %s, %s, '');"
                cur.execute(sql, (formatted_date + '_' + skill, dict_feed['title'].replace("'", ""), dict_feed['link']))
                conn.commit()
                send_message(message)
                print(message)
            except psycopg2.errors.UniqueViolation:
                print("Duplicate entry detected. The record already exists in the database.")
            except psycopg2.Error as e:
                print(f"An error occurred: {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
        data.append(dict_feed)
        counter = counter + 1


if __name__ == "__main__":
    read_rss("python")
    read_rss("machinelearning")
    read_rss("datascraping")
    read_rss("airflow")
    read_rss("spark")
    read_rss("kafka")