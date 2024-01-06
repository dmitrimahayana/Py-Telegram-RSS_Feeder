import os
import libsql_client
import psycopg2
import socket
from config_local import postgres_config, local_pc_name

BOT_TOKEN = os.environ.get('BOT_TOKEN')  # the one you saved in previous step
CHANNEL_ID = os.environ.get('BOT_CHANNEL_ID')  # don't forget to add this
DB_TOKEN = os.environ.get('TURSO_API_TOKEN')


def query_clear_tursodb():
    client = libsql_client.create_client_sync(
        url="libsql://upwork-rss-feeder-dmitrimahayana.turso.io",
        auth_token=DB_TOKEN
    )
    try:
        print('Trying to drop table in Turso DB ...')
        sql = "drop table rss_upwork;"
        client.execute(sql)
    except Exception as e:
        pass

    try:
        print('Trying to create table in Turso DB ...')
        sql = "CREATE TABLE rss_upwork (id_date text, title text, link text, summary text, primary key (id_date));"
        client.execute(sql)
    except Exception as e:
        pass
    client.close()


def query_clear_postgres():
    host = postgres_config["host"]
    if socket.gethostname() != local_pc_name:
        host = "postgresdb"
        print(socket.gethostname(), host)

    conn = psycopg2.connect(host=host,
                            port=postgres_config["port"],
                            database=postgres_config["database"],
                            user=postgres_config["user"],
                            password=postgres_config["password"], )

    with conn.cursor() as cur:
        sql = "TRUNCATE rss_upwork;"
        print('Start to truncate table in postgresdb ...')
        cur.execute(sql)
        conn.commit()
        print('End to truncate table in postgresdb ...')


if __name__ == "__main__":
    query_clear_postgres()
