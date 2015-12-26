import sqlite3
import random
import pandas as pd
from math import sqrt

sql_conn = sqlite3.connect('database.sqlite')

df = pd.read_sql("""
    SELECT
      author
      , subreddit
      , count(*) as nbComment
    FROM May2015
    WHERE
        author IN (
            SELECT
                author
            FROM
                May2015
            GROUP BY author
            HAVING count(DISTINCT subreddit)  > 4
            AND count(DISTINCT parent_id) < 3000
            LIMIT 1000)
    GROUP BY author, subreddit""", sql_conn)

test = []
y = []
for author, subs in df.groupby('author'):
    testSize = int(sqrt(len(subs)))
    rows = random.sample(range(0,len(subs)), testSize)
    i = 0
    for sub, nbComment in subs['nbComment'].groupby(subs['subreddit']): 
        if i in rows:
            y.append((author, sub, int(nbComment)))
        else:
            test.append((author, sub, int(nbComment)))
        i += 1
columns = ['author', 'subreddit', 'nbComment']
dfTest = pd.DataFrame(test, columns=columns)
dfY = pd.DataFrame(y, columns=columns)

dfTest.to_csv('testData.csv', encoding='utf-8', index=False)
dfY.to_csv('yData.csv', encoding='utf-8', index=False)