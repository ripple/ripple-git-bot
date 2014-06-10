#!/usr/bin/python

# Imported Modules:

import github

# Initialization Parameters:

params = {
    botname : "<<the name of the ripple bot>>",
    password : "<<the password to the ripple bot's account>>",
    orgname : "ripple",
    cibotname : "mtrippled"
    }

# Middleware Functions:

def check(commentlist, memberlist, infodict):
    votes = {}
    if infodict["creator"] in memberlist:
        votes[infodict["creator"]] = 1
    for user, comment in commentlist:
        if user in memberlist:
            if comment == "lgtm":
                votes[user] = 1
            elif comment == "veto":
                votes[user] = float("-inf")
    if sum(votes.values()) >= 2:
        return "Merged by "+infodict["botname"]+". "+infodict["status"]+". Verified looks good to "+", ".join(votes.keys())+"."
    return False

def status(pull, authname):
    """Returns Basic Information For The Comments On The Pull In A List."""
    checked = False
    for commit in pull.get_commits():
        checked = False
        for status in commit.get_statuses():
            if formatting(status.creator.login) == cibotname:
                if formatting(status.state) == "success":
                    checked = True
                    break
                else:
                    return False
        if not checked:
            return False
    if checked:
        return "Verified passes tests by "+authname+"."
    else:
        return False

# Utility Functions:

def formatting(inputstring):
    """Insures All Strings Follow A Uniform Format For Ease Of Comparison."""
    out = ""
    for c in inputstring:
        if c in string.printable:
            out += c
    return str(out).strip().lower()

def commentlist(pull):
    """Returns Basic Information For The Comments On The Pull In A List."""
    comments = pull.get_issue_comments()
    commentlist = []
    for comment in comments:
        commentlist.append((formatting(comment.user.login), formatting(comment.body)))
    return commentlist

# Connecting To Github:

client = github.Github(params["botname"], params["password"])
org = client.get_organization(params["orgname"])
members = org.get_members()

# Creating The Necessary Objects:

openpulls = {}
for repo in org.get_repos():
    openpulls[repo] = []
    for pull in repo.get_pulls():
        if not pull.is_merged():
            openpulls[repo].append(pull)

memberlist = []
for member in members:
    memberlist.append(formatting(member.login))

# Running The Middleware On The Objects:

for repo in openpulls:
    for pulls in openpulls[repo]:
        for pull in pulls:
            if pull.mergeable:
                result = status(pull, params["cibotname"])
                if result:
                    infodict = {
                        "creator":formatting(pull.user.login),
                        "repo":repo,
                        "pulls":pulls,
                        "pull":pull,
                        "openpulls":openpulls,
                        "client":client,
                        "org":org,
                        "members":members,
                        "status":result
                        }
                    infodict.update(params)
                    message = check(commentlist(pull), memberlist, infodict)
                    if message:
                        pull.create_issue_comment(message)
                        pull.merge(message)
