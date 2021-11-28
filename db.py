import pymysql


def get_conn():
    return pymysql.connect(host="localhost",
                           user='root',
                           password='zxy220',
                           db="mycompany",
                           port=3306)
def query_data(sql):
    conn=get_conn()
    try:
        cursor=conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(sql)
        return cursor.fetchall()
    finally:
        conn.close()

def insert_or_update_data(sql):
    conn=get_conn()
    try:
        cursor=conn.cursor()
        cursor.execute(sql)
        conn.commit()
    finally:
        conn.close()