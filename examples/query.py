#!/usr/bin/env python
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.

# query.py: Perform a few varieties of queries

from __future__ import print_function
import datetime

import win_inet_pton
import bugzilla
from crawler import Instances

# public test instance of bugzilla.redhat.com. It's okay to make changes
# URL = "partner-bugzilla.redhat.com"
URL = "bugzilla.mozilla.org"
URL = "bugzilla.redhat.com"
URL = "bugzilla.novell.com"
URL = "bugzilla.kernel.org"
URL = "bugzilla.gnome.org"
URL = "bugs.kde.org"
URL = "bugs.gentoo.org"
URL = "bugs.freedesktop.org"
URL = "bugzilla.xfce.org"
URL = "bugs.documentfoundation.org"
URL = "issues.openmandriva.org"
URL = "bugzilla.suse.com"
URL = "bugs.mageia.org"
URL = "http://bugzilla.dre.vanderbilt.edu"
URL = "chess.eecs.berkeley.edu/bugzilla/xmlrpc.cgi"
URL = "gcc.gnu.org/bugzilla/xmlrpc.cgi"
URL = "bz.apache.org/bugzilla/xmlrpc.cgi"
URL = "bugs.eclipse.org/bugs/xmlrpc.cgi"
URL = "bz.apache.org/ooo/xmlrpc.cgi"
URL = "bugs.winehq.org"


limit = 10

# build_query is a helper function that handles some bugzilla version
# incompatibility issues. All it does is return a properly formatted
# dict(), and provide friendly parameter names. The param names map
# to those accepted by XMLRPC Bug.search:
# https://bugzilla.readthedocs.io/en/latest/api/core/v1/bug.html#search-bugs
bug_common_fields = None
cmt_common_fields = None
for inst in Instances:
    print("$$$$$$$$$$$$  ",  inst['name'], "  $$$$$$$$$$$$$$$")
    bzapi = bugzilla.Bugzilla(inst['URL'])
    query = bzapi.build_query(
        # resolution="FIXED",
        status=inst['states'][-1],
        limit=limit,
        offset=0,
        include_fields=['classification', 'creator', 'depends_on', 'creation_time', 'is_open', 'keywords', 'id', 'severity', 'is_confirmed', 'priority', 'platform', 'version', 'status', 'product', 'component', 'url', 'summary', 'assigned_to', 'resolution', 'last_change_time']
    )
    # print(inst['states'][-1])
    bugs = bzapi.query(query)
    # print("Found %d bugs with our query" % len(bugs))
    if len(bugs) > 0:
        print(bugs[0].__dict__)
        print(type(datetime.datetime(bugs[0].creation_time)))
        # if not bug_common_fields:
        #     bug_common_fields = bugs[0]._bug_fields
        # else:
        #     bug_common_fields = list(set(bug_common_fields).intersection(bugs[0]._bug_fields))
        # print(bug_common_fields)
        comms = bugs[0].getcomments()
        if len(comms)>0:
        # print("Found %d comments for first bug" %len(comms))
            print(comms[0])
            # if not cmt_common_fields:
            #     cmt_common_fields = comms[0].keys()
            # else:
            #     cmt_common_fields = list(set(cmt_common_fields).intersection(comms[0].keys()))
            # print(cmt_common_fields)
        else:
            print("NO Comment! ERROR...")
            # exit()
    else:
        print("NO Bug! ERROR...")
        # exit()

# print(bug_common_fields)
# print(cmt_common_fields)

#todo: check the category in the json of bug.
# Since 'query' is just a dict, you could set your own parameters too, like
# if your bugzilla had a custom field. This will set 'status' for example,
# but for common opts it's better to use build_query
# query["status"] = "CLOSED"

# {'count': 7, 'author': 'marja11@xs4all.nl', 'text': 'Mass-reassigning all bugs with "kernel" in the Source RPM field that are assigned to tmb, to the kernel packagers group, because tmb is currently MIA.', 'creator': 'marja11@xs4all.nl', 'creation_time': <DateTime '20160826T09:42:38' at 4c28d00>, 'bug_id': 16759, 'time': <DateTime '20160826T09:42:38' at 4c28558>, 'id': 164363, 'is_private': False}
# query() is what actually performs the query. it's a wrapper around Bug.search
# t1 = time.time()
# bugs = bzapi.query(query)
# t2 = time.time()
# print("Found %d bugs with our query" % len(bugs))
# # print("Query processing time: %s" % (t2 - t1))
# if len(bugs) > 0:
#     # unicode(bugs[0])
#     print(bugs[0]._bug_fields)
#     # for field in bugs[0].__dict__:
#     #     print('"'+ field + '": ' + str(bugs[0].__dict__[field]))
#     comms = bugs[0].getcomments()
#     print("Found %d comments for first bug" %len(comms))
#     # print(bugs[0])
#     print(comms[0])
#
#     # for bug in bugs:
#     #     comms = bug.getcomments()
#     #     for cmt in comms:
#     #         print(cmt)

# query = bzapi.build_query(
#     # product="gjs",
#     # component="python-bugzilla"
#     # resolution="---",
#     f1="resolution",
#     o1="isnotempty",
#     limit=limit,
#     offset=0,
#     include_fields=["id", "summary"]
# )
# result_count = limit
# while result_count == limit:
#     bugs = bzapi.query(query)
#     result_count = len(bugs)
#     print("Found %d bugs with our query" % len(bugs))
#     query["offset"] += limit


# Depending on the size of your query, you can massively speed things up
# by telling bugzilla to only return the fields you care about, since a
# large chunk of the return time is transmitting the extra bug data. You
# tweak this with include_fields:
# https://wiki.mozilla.org/Bugzilla:BzAPI#Field_Control
# Bugzilla will only return those fields listed in include_fields.

# query = bzapi.build_query(
#    product="Fedora",
#    component="python-bugzilla",
#    include_fields=["id", "summary"])
# t1 = time.time()
# bugs = bzapi.query(query)
# t2 = time.time()
# print("Quicker query processing time: %s" % (t2 - t1))


# bugzilla.redhat.com, and bugzilla >= 5.0 support queries using the same
# format as is used for 'advanced' search URLs via the Web UI. For example,
# I go to partner-bugzilla.redhat.com -> Search -> Advanced Search, select
#   Classification=Fedora
#   Product=Fedora
#   Component=python-bugzilla
#   Unselect all bug statuses (so, all status values)
#   Under Custom Search
#      Creation date -- is less than or equal to -- 2010-01-01
#
# Run that, copy the URL and bring it here, pass it to url_to_query to
# convert it to a dict(), and query as usual
# query = bzapi.url_to_query("https://partner-bugzilla.redhat.com/"
#    "buglist.cgi?classification=Fedora&component=python-bugzilla&"
#    "f1=creation_ts&o1=lessthaneq&order=Importance&product=Fedora&"
#    "query_format=advanced&v1=2010-01-01")
# query["include_fields"] = ["id", "summary"]
# bugs = bzapi.query(query)
# print("The URL query returned 22 bugs... "
#      "I know that without even checking because it shouldn't change!... "
#      "(count is %d)" % len(bugs))


# One note about querying... you can get subtley different results if
# you are not logged in. Depending on your bugzilla setup it may not matter,
# but if you are dealing with private bugs, check bzapi.logged_in setting
# to ensure your cached credentials are up to date. See update.py for
# an example usage
