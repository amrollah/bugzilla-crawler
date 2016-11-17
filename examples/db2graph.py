#!/usr/bin/python2.7.11

import argparse
from datetime import datetime
import sqlite3

# The relative or full address to folder containing bugzilla databases
db_dir = ""  # "D:\python-bugzilla\examples\\"


def valid_date(s):
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return s
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)


parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", action="store_true", help="increase output verbosity")
parser.add_argument("db", help="the name of Bugzilla database file")
parser.add_argument('-s', "--start_date", help="The Start Date - format YYYY-MM-DD ", required=True, type=valid_date)
parser.add_argument('-e', "--end_date", help="The End Date - format YYYY-MM-DD ", required=True, type=valid_date)
parser.add_argument("-w_s", "--include_submitter", action="store_true",
                    help="include the bug reporter user in graph")
parser.add_argument("-c", "--clique", action="store_true",
                    help="add all the link combinations between users")
args = parser.parse_args()
db_path = "{0}{1}.db".format(db_dir, args.db)
edges = []
cur = None
try:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
except Exception, e:
    print(repr(e))
    exit(1)
cur.execute("SELECT * FROM comments WHERE creation_time BETWEEN ? AND ? ORDER BY bug_id ASC, creation_time ASC",
            (args.start_date, args.end_date))
res = cur.fetchall()
bug_reporters = []

last_commenter = None
cur_bug = None
cur_bug_reporter = None
cur_bug_commenters = set()
for comment in res:
    commenter_user = comment[2]
    if comment[1] != cur_bug:
        cur_bug_reporter = None
        try:
            cur.execute("SELECT creator_user_id FROM bugs WHERE id = ?", (comment[1],))
            cur_bug_reporter = cur.fetchone()[0]
        except Exception, e:
            print("Error occurred in loading the bug for comment {0}".format(comment[0]))
        cur_bug = comment[1]
        last_commenter = None
        cur_bug_commenters = set()
    bug_reporters.append(cur_bug_reporter)
    if not args.include_submitter and (commenter_user == cur_bug_reporter):
        continue
    if args.clique:
        if commenter_user not in cur_bug_commenters:
            for commenter in cur_bug_commenters:
                edge = "{0} {1}\n".format(commenter_user, commenter)
                if edge not in edges:
                    edges.append(edge)
                edge = "{0} {1}\n".format(commenter, commenter_user)
                if edge not in edges:
                    edges.append(edge)
            cur_bug_commenters.add(commenter_user)
    else:
        if last_commenter and last_commenter != commenter_user:
            edge = "{0} {1}\n".format(commenter_user, last_commenter)
            if edge not in edges:
                edges.append(edge)
        last_commenter = commenter_user

with open("{0}.edges".format(args.db), 'w+') as edges_file:
    edges_file.writelines(edges)
with open("comments.txt", 'w+') as comments_file:
    comments_file.writelines(["{0} ------- {1}\n".format(cmt, bug_reporters[idx]) for idx, cmt in enumerate(res)])
