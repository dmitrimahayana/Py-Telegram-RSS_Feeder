import os
import libsql_client

BOT_TOKEN = os.environ.get('BOT_TOKEN')  # the one you saved in previous step
CHANNEL_ID = os.environ.get('BOT_CHANNEL_ID')  # don't forget to add this
DB_TOKEN = os.environ.get('TURSO_API_TOKEN')


def query_clear_tursodb():
    client = libsql_client.create_client_sync(
        url="libsql://upwork-rss-feeder-dmitrimahayana.turso.io",
        auth_token=DB_TOKEN
    )
    try:
        print('Trying to drop table to Turso DB ...')
        sql = "drop table rss_upwork;"
        client.execute(sql)
    except Exception as e:
        pass

    try:
        print('Trying to create table to Turso DB ...')
        sql = "CREATE TABLE rss_upwork (id_date text, title text, link text, summary text, primary key (id_date));"
        client.execute(sql)
    except Exception as e:
        pass
    client.close()
