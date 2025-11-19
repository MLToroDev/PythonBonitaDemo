import psycopg2

conn = psycopg2.connect(
    host='localhost',
    database='doc360',
    user='postgres',
    password='postgres',
)

cur = conn.cursor()
cur.execute("SHOW lc_messages;")
print(cur.fetchone())
