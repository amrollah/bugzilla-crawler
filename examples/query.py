#!/usr/bin/env python
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.

# query.py: Perform a few varieties of queries

from __future__ import print_function

import time

import bugzilla

# public test instance of bugzilla.redhat.com. It's okay to make changes
# URL = "partner-bugzilla.redhat.com"
# URL = "bugzilla.gnome.org"
URL = "bugzilla.mozilla.org"

bzapi = bugzilla.Bugzilla(URL)
limit = 10000

# build_query is a helper function that handles some bugzilla version
# incompatibility issues. All it does is return a properly formatted
# dict(), and provide friendly parameter names. The param names map
# to those accepted by XMLRPC Bug.search:
# https://bugzilla.readthedocs.io/en/latest/api/core/v1/bug.html#search-bugs
query = bzapi.build_query(
    # product="gjs",
    # component="python-bugzilla"
    # resolution="---",
    f1="resolution",
    o1="isempty",
    include_fields=["id", "summary"]
)

# Since 'query' is just a dict, you could set your own parameters too, like
# if your bugzilla had a custom field. This will set 'status' for example,
# but for common opts it's better to use build_query
# query["status"] = "CLOSED"

# query() is what actually performs the query. it's a wrapper around Bug.search
t1 = time.time()
bugs = bzapi.query(query)
t2 = time.time()
print("Found %d bugs with our query" % len(bugs))
print("Query processing time: %s" % (t2 - t1))

query = bzapi.build_query(
    # product="gjs",
    # component="python-bugzilla"
    # resolution="---",
    f1="resolution",
    o1="isnotempty",
    limit=limit,
    offset=0,
    include_fields=["id", "summary"]
)
result_count = limit
while result_count == limit:
    bugs = bzapi.query(query)
    result_count = len(bugs)
    print("Found %d bugs with our query" % len(bugs))
    query["offset"] += limit


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
