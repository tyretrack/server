#!/usr/bin/env python

import sys
from socket import *
import sqlite3
import time


def listen(conn):
    s = socket(AF_INET, SOCK_DGRAM)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.bind(('', 5606))
    while True:
        data, addr = s.recvfrom(2048)
        conn.execute('INSERT INTO log VALUES (?, ?, ?)', [int(time.time() * 1000), addr[0], sqlite3.Binary(data)])
        conn.commit()


def createDb(filename):
    print(filename)
    conn = sqlite3.connect(filename)

    conn.execute('CREATE TABLE IF NOT EXISTS log(ts INTEGER, ip TEXT, data TEXT);')

    return conn


def main(argv):
    if len(argv) > 1:
        conn = createDb(argv[1])
    else:
        conn = createDb('pjcars-raw2.db')

    listen(conn)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
