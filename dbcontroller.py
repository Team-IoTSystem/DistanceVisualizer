import MySQLdb


def mysql_connect(host, user, passwd, db, charset='utf8'):
    conn = MySQLdb.connect(host, user, passwd, db, charset=charset)
    cur = conn.cursor()
    return conn, cur
