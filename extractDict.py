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
            HAVING count(DISTINCT subreddit)  > 10
            AND count(DISTINCT parent_id) < 3000
            LIMIT 1000)
    GROUP BY author, subreddit""", sql_conn)

df.to_csv('UtilityMatrix.csv', encoding='utf-8', index=False)