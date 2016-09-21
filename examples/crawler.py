from __future__ import print_function
import random
from time import sleep
import win_inet_pton
import bugzilla
import sqlite3
from stem import Signal
from stem.control import Controller
import logging
from datetime import datetime
import os

Instances = [
    {"name": "mozilla", "URL": "bugzilla.mozilla.org",
    "states": ["UNCONFIRMED", "NEW", "ASSIGNED", "REOPENED", "RESOLVED", "VERIFIED", "CLOSED"]},
    {"name": "redhat", "URL": "bugzilla.redhat.com",
     "states": ["NEW", "VERIFIED", "ASSIGNED", "MODIFIED", "ON_DEV", "ON_QA", "RELEASE_PENDING", "POST"]},
    {"name": "kernel", "URL": "bugzilla.kernel.org",
     "states": ["NEW", "ASSIGNED", "REOPENED", "RESOLVED", "VERIFIED", "REJECTED", "DEFERRED", "CLOSED"]},
    {"name": "genome", "URL": "bugzilla.gnome.org",
     "states": ["UNCONFIRMED", "NEW", "ASSIGNED", "REOPENED", "NEEDINFO", "VERIFIED", "RESOLVED"]},
    {"name": "kde", "URL": "bugs.kde.org",
     "states": ["UNCONFIRMED", "CONFIRMED", "ASSIGNED", "REOPENED", "RESOLVED", "NEEDSINFO", "VERIFIED", "CLOSED"]},
    {"name": "gentoo", "URL": "bugs.gentoo.org",
     "states": ["UNCONFIRMED", "CONFIRMED", "VERIFIED", "RESOLVED", "IN_PROGRESS"]},
    {"name": "XFCE", "URL": "bugzilla.xfce.org",
     "states": ["UNCONFIRMED", "NEW", "ASSIGNED", "REOPENED", "NEEDINFO", "RESOLVED", "VERIFIED", "CLOSED"]},
    {"name": "libre-office", "URL": "bugs.documentfoundation.org", "states": [
        "UNCONFIRMED", "NEW", "ASSIGNED", "REOPENED", "NEEDINFO", "RESOLVED", "VERIFIED", "PLEASETEST", "CLOSED"]},
    {"name": "mandriva", "URL": "issues.openmandriva.org",
     "states": ["UNCONFIRMED", "ACKED", "NEEDINFO", "CONFIRMED", "IN_PROGRESS", "VERIFIED", "RESOLVED"]},
    {"name": "open-suse", "URL": "bugzilla.suse.com",
     "states": ["UNCONFIRMED", "CONFIRMED", "IN_PROGRESS", "REOPENED", "VERIFIED", "RESOLVED", "NEW"]},
    {"name": "Wine", "URL": "bugs.winehq.org",
     "states": ["UNCONFIRMED", "NEW", "ASSIGNED", "STAGED", "NEEDINFO", "REOPENED", "RESOLVED", "CLOSED"]},
    {"name": "mageia", "URL": "bugs.mageia.org",
     "states": ["UNCONFIRMED", "ASSIGNED", "REOPENED", "RESOLVED", "VERIFIED", "NEW"]},
    {"name": "washington-uni", "URL": "http://bugzilla.dre.vanderbilt.edu",
     "states": ["UNCONFIRMED", "NEW", "ASSIGNED", "REOPENED", "RESOLVED", "VERIFIED", "CLOSED"]},
    {"name": "berkeley", "URL": "chess.eecs.berkeley.edu/bugzilla/xmlrpc.cgi",
     "states": ["UNCONFIRMED", "NEW", "ASSIGNED", "REOPENED", "RESOLVED", "VERIFIED", "CLOSED"]},
    {"name": "GCC", "URL": "gcc.gnu.org/bugzilla/xmlrpc.cgi", "states": [
        "UNCONFIRMED", "NEW", "ASSIGNED", "SUSPENDED", "WAITING", "REOPENED", "RESOLVED", "VERIFIED", "CLOSED"]},
    {"name": "apache", "URL": "bz.apache.org/bugzilla/xmlrpc.cgi",
     "states": ["UNCONFIRMED", "NEW", "ASSIGNED", "REOPENED", "NEEDINFO", "RESOLVED", "VERIFIED", "CLOSED"]},
    {"name": "eclipse", "URL": "bugs.eclipse.org/bugs/xmlrpc.cgi",
    "states": ["UNCONFIRMED", "NEW", "ASSIGNED", "REOPENED", "RESOLVED", "VERIFIED", "CLOSED"]},
    {"name": "open-office", "URL": "bz.apache.org/ooo/xmlrpc.cgi",
    "states": ["UNCONFIRMED", "CONFIRMED", "ACCEPTED", "REOPENED", "RESOLVED", "VERIFIED", "CLOSED"]},
    {"name": "novell", "URL": "bugzilla.novell.com",
    "states": ["UNCONFIRMED", "IN_PROGRESS", "REOPENED", "VERIFIED", "RESOLVED", "NEW", "CONFIRMED"]},
    {"name": "X-org", "URL": "bugs.freedesktop.org", "states": [
       "UNCONFIRMED", "NEW", "ASSIGNED", "REOPENED", "NEEDINFO", "RESOLVED", "VERIFIED", "PLEASETEST", "CLOSED"]},
]


# state_intersect = Instances[0]["states"]
# for instance in Instances:
#     state_intersect = list(set(state_intersect).intersection(instance["states"]))
#     print(state_intersect)

# ['classification', 'creator', 'cc', 'depends_on', 'creation_time', 'is_open', 'keywords', 'id', 'severity',
#  'is_confirmed', 'is_creator_accessible', 'priority', 'platform', 'version', 'status', 'product', 'blocks',
#  'qa_contact', 'see_also', 'component', 'groups', 'target_milestone', 'is_cc_accessible', 'url', 'whiteboard',
#  'summary', 'op_sys', 'assigned_to', 'resolution', 'last_change_time']

##  ['classification', 'creator', 'depends_on', 'creation_time', 'is_open', 'id', 'severity', 'is_confirmed',
#  'priority', 'platform', 'version', 'status', 'product', 'component', 'url', 'assigned_to', 'resolution',
#  'last_change_time']
# ['creator', 'text', 'creation_time', 'bug_id', 'id']  # 'time',


def get_database_bugzilla(db_name):
    try:
        if os.path.exists(db_name):
            os.remove(db_name)
        if os.path.exists(db_name + "-journal"):
            os.remove(db_name + "-journal")
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        cur.execute('''DROP TABLE IF EXISTS users''')
        cur.execute('''DROP TABLE IF EXISTS bugs''')
        cur.execute('''DROP TABLE IF EXISTS comments''')
        cur.execute('''CREATE TABLE users
             (id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL)''')
        cur.execute('''CREATE TABLE bugs
             (id INTEGER UNIQUE NOT NULL, creator_user_id INTEGER, assigned_to_user_id INTEGER, classification TEXT, product TEXT, component TEXT, status TEXT, depends_on TEXT, creation_time DATETIME, is_open BOOLEAN, is_confirmed BOOLEAN, severity TEXT, priority TEXT, platform TEXT, version TEXT, url TEXT, resolution TEXT, last_change_time DATETIME, FOREIGN KEY(creator_user_id) REFERENCES users(id), FOREIGN KEY(assigned_to_user_id) REFERENCES users(id))''')
        cur.execute('''CREATE TABLE comments
             (id INTEGER UNIQUE NOT NULL, bug_id INTEGER, creator_user_id INTEGER, creation_time DATETIME, FOREIGN KEY(bug_id) REFERENCES bugs(id), FOREIGN KEY(creator_user_id) REFERENCES users(id))''')
        conn.commit()
        return conn
    except Exception, e:
        logging.exception(repr(e))
        if conn:
            conn.rollback()
            conn.close()


def renew_ip():
    print('getting new ip ...')
    try:
        with Controller.from_port(port=9040) as controller:
            controller.authenticate(password="123456")
            controller.signal(Signal.NEWNYM)
            sleep(random.randint(3, 7))
    except Exception, e:
        logging.exception(repr(e))


def convert_date(date):
    """
    :param date: the date input from a bugzilla instance. Example: <DateTime '19980408T19:02:34' at 2d1a530>
    :return: string format of input date to be readable by sqlite
    """
    return str(datetime.strptime(str(date), '%Y%m%dT%H:%M:%S'))


def create_bug(bug):
    if bug.id in ["", " ", None, 0, "null"]:
        return False
    creator = {"username": bug.creator}
    creator_success = get_or_create_user(creator)
    assigned_to = {"username": bug.assigned_to}
    assigned_to_success = get_or_create_user(assigned_to)
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO bugs(id, creator_user_id, assigned_to_user_id, classification, product, status, depends_on, creation_time, is_open, is_confirmed, severity, priority, platform, version, url, resolution, last_change_time) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (bug.id, creator['id'] if creator_success else None, assigned_to['id'] if assigned_to_success else None,
             bug.classification, bug.product, bug.status, str(bug.depends_on), convert_date(bug.creation_time),
             bug.is_open,
             bug.is_confirmed, bug.severity, bug.priority, bug.platform, bug.version, bug.url,
             bug.resolution, convert_date(bug.last_change_time)))
        conn.commit()
        print("bug {0} is created.".format(bug.id))
        return True
    except Exception, e:
        logging.exception(repr(e))
        if conn:
            conn.rollback()
        return False


def create_comment(comment, bug, user):
    if comment["bug_id"] != bug.id:
        print("bug.id {0} does not match with comment.bug_id {1}".format(bug.id, comment['bug_id']))
        return False
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO comments(id, bug_id, creator_user_id, creation_time) VALUES (?,?,?,?)", (
            comment['id'], bug.id, user['id'] if 'id' in user else None, convert_date(comment['creation_time'])))
        conn.commit()
        print("comment {0} is created.".format(comment['id']))
        return True
    except Exception, e:
        logging.exception(repr(e))
        if conn:
            conn.rollback()
        return False


def get_or_create_user(user):
    if user['username'] in ["", " ", None, "null"]:
        return False
    try:
        success = False
        cur = conn.cursor()
        cur.execute('SELECT id, username FROM users WHERE username = ?',
                    (user['username'],))
        res = cur.fetchone()
        if res is None or len(res) == 0:
            cur.execute("INSERT INTO users(username) VALUES (?)", (user['username'],))
            user['id'] = cur.lastrowid
            success = True
        else:
            user['id'] = res[0]
        conn.commit()
        if success:
            print("user ({0}) is created.".format(user['username']))
        return True
    except Exception, e:
        logging.exception(repr(e))
        if conn:
            conn.rollback()
        return False


MAX_NUM_RESULT = 10000
global conn

if __name__ == "__main__":
    conn = None
    instance_id = -1
    instance = Instances[instance_id]
    db_path = "{0}.db".format(instance["name"])
    clean = True
    if os.path.exists(db_path) and os.path.getsize("{0}\{1}".format(os.path.dirname(os.path.abspath(__file__)),db_path))>0:
        clean = False
    limit = MAX_NUM_RESULT  # to get all available rows of results (until 10000)
    try:
        if clean:
            conn = get_database_bugzilla(db_path)
        else:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
        print("###########  ", instance['name'], "  #############")
        bzapi = bugzilla.Bugzilla(instance['URL'])
        for state in instance['states']:
            offset = 0
            iteration = 1
            retry = 0
            while True:
                query = bzapi.build_query(
                    status=state,
                    limit=limit,
                    offset=(offset + 2*MAX_NUM_RESULT) if state == "NEW" else offset,
                    include_fields=['classification', 'creator', 'depends_on', 'creation_time', 'is_open',
                                    'id', 'severity', 'is_confirmed', 'priority', 'platform', 'version', 'status',
                                    'product', 'component', 'url', 'assigned_to', 'resolution',
                                    'last_change_time']
                )
                bugs = []
                try:
                    bugs = bzapi.query(query)
                    bug_load_error = False
                    retry = 0
                except Exception, e:
                    logging.exception(repr(e))
                    bug_load_error = True
                    retry += 1
                print("Found {0} bugs in iteration {1}, try {2}".format(len(bugs), iteration, retry+1))
                for bug in bugs:
                    try:
                        success_bug = create_bug(bug)
                        if success_bug:
                            comments = bug.getcomments()
                            print("Found {0} comments for bug {1}".format(len(comments), bug.id))
                            for comment in comments:
                                user = {"username": comment["creator"]}
                                success = get_or_create_user(user)
                                create_comment(comment, bug, user if success else {})
                    except Exception, e:
                        logging.exception(repr(e))
                # if max(offset, limit) > 900:
                #     renew_ip()
                if bug_load_error and (retry<3):
                    continue
                if (not bug_load_error and len(bugs) == 0) or iteration > 50:
                    break
                if limit != 0 and (len(bugs) == limit or len(bugs) == 0):
                    offset += limit
                    iteration += 1
                elif len(bugs) == MAX_NUM_RESULT:
                    offset += MAX_NUM_RESULT
                    iteration += 1
                else:
                    break

    except Exception, e:
        logging.exception(repr(e))
    finally:
        if conn:
            conn.close()
