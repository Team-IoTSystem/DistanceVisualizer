import MySQLdb


def mysql_connect(host, user, passwd, db, charset='utf8'):
    conn = MySQLdb.connect(host, user, passwd, db, charset=charset)
    cur = conn.cursor(MySQLdb.cursors.DictCursor)
    return conn, cur


def select_latest(conn, cur, dev_mac, rpimac):
    cur.execute("""SELECT a.id, a.macaddr, a.pwr, a.distance, a.rpimac
                   FROM distance AS a INNER JOIN
                   (SELECT MAX(id) AS latest FROM distance GROUP BY macaddr, rpimac) AS b
                   ON a.id = b.latest AND macaddr=%s AND rpimac=%s""", (dev_mac, rpimac))
    conn.commit()
    return cur.fetchone()

