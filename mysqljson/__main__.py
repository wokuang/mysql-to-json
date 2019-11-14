#!/usr/bin/env python3

"""
mysql-to-json
Connects to a MySQL database and exports selected data to JSON.
copyright 2018 Seth Black
"""

import argparse
import getpass
import json
import MySQLdb
import sys

def cursor_to_dict(cursor):
    data = cursor.fetchone()

    if data is None:
        return None

    desc = cursor.description

    result = {}

    for (name, value) in zip(desc, data):
        result[name[0]] = value

    return result

def main():
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument('-d', '--database', help='MySQL database name.', default='mysql')
    arg_parser.add_argument('-H', '--hostname', help='MySQL host name.', default='127.0.0.1')
    arg_parser.add_argument('-P', '--port', help='MySQL port number.', default=3306, type=int)
    arg_parser.add_argument('-u', '--user', help='MySQL username.', default='root')
    arg_parser.add_argument('-p', '--password', help='Shh! It\'s a secret.', action='store_true')
    arg_parser.add_argument('-e', '--query', help='Query to run.', required=True)

    args = arg_parser.parse_args()

    password = ''

    if args.password == True:
       password = getpass.getpass()

    conn = MySQLdb.connect(host=args.hostname, user=args.user, passwd=password, db=args.database, port=args.port)

    try:
        cursor = conn.cursor()

        cursor.execute(args.query)
    except MySQLdb.Error as e:
        sys.stderr.write('MySQL Error [{}]: {}\n'.format((e.args[0], e.args[1])))
        sys.exit()

    row = cursor_to_dict(cursor)
    count = 1
    es_doc = { "index" : { "_index": "sklogs", "_type" : "_doc", "_id" : "1" } }

    while row is not None:

        es_doc["_id"] = count
        doc_str = json.dumps(es_doc, default=str)
        json_str = json.dumps(row, default=str)

        sys.stdout.write(doc_str)
        sys.stdout.write("\n")
        sys.stdout.write(json_str)
        sys.stdout.write("\n")

        row = cursor_to_dict(cursor)
        count = count + 1

    sys.stdout.write("\n")

if __name__ == "__main__":
    main()
