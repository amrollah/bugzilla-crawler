#!/usr/bin/env python
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.

# update.py: Make changes to an existing bug

from __future__ import print_function

import time

import bugzilla

# public test instance of bugzilla.redhat.com. It's okay to make changes
URL = "partner-bugzilla.redhat.com"
bzapi = bugzilla.Bugzilla(URL)
if not bzapi.logged_in:
    print("This example requires cached login credentials for %s" % URL)
    bzapi.interactive_login()


# Similar to build_query, build_update is a helper function that handles
# some bugzilla version incompatibility issues. All it does is return a
# properly formatted dict(), and provide friendly parameter names.
# The param names map to those accepted by XMLRPC Bug.update:
# https://bugzilla.readthedocs.io/en/latest/api/core/v1/bug.html#update-bug
#
# Example bug: https://partner-bugzilla.redhat.com/show_bug.cgi?id=427301
# Don't worry, changing things here is fine, and won't send any email to
# users or anything. It's what partner-bugzilla.redhat.com is for!
bug = bzapi.getbug(427301)
print("Bug id=%s original summary=%s" % (bug.id, bug.summary))

update = bzapi.build_update(summary="new example summary %s" % time.time())
bzapi.update_bugs([bug.id], update)

# Call bug.refresh() to update its cached state
bug.refresh()
print("Bug id=%s new summary=%s" % (bug.id, bug.summary))


# Now let's add a comment
comments = bug.getcomments()
print("Bug originally has %d comments" % len(comments))

update = bzapi.build_update(comment="new example comment %s" % time.time())
bzapi.update_bugs([bug.id], update)

# refresh() actually isn't required here because comments are fetched
# on demand
comments = bug.getcomments()
print("Bug now has %d comments. Last comment=%s" % (len(comments),
    comments[-1]["text"]))


# The 'bug' object actually has some old convenience APIs for specific
# actions like commenting, and closing. However these aren't recommended:
# they encourage splitting up bug edits when really batching should be done
# as much as possible, not only to make your code quicker and save strain
# on the bugzilla instance, but also to avoid spamming bugzilla users with
# redundant email from two modifications that could have been batched.
