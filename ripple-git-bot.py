#!/usr/bin/python

# Imported Modules:

import github
import string

# Initialization Parameters:

params = {
    "botname" : "<<the name of the ripple bot>>",                     # The name of the ripple bot
    "password" : "<<the password to the ripple bot's account>>",      # The password to the ripple bot's account
    "orgname" : "ripple",                                             # The name of ripple's github organization
    "cibotname" : "mtrippled",                                         # The name of the ripple CI bot
    "hookname" : "ripple-git-bot",                                     # The name of the hook into this file
    "hookurl" : "<<the url of this file>>",                            # The url of this file for hooking into
    "hookevents" : [                                                      # The different events the hook is triggered on
                 "commit_comment",
                 "issue_comment",
                 "pull_request",
                 "member"
                 ],
    "debug" : False                                                 # Turns on and off the debug output
    }

# Middleware Functions:

def check(commentlist, memberlist, infodict):
    """Checks That At Least Two Members Have Commented LGTM And None Commented VETO."""
    votes = {}
    if infodict["creator"] in memberlist:
        votes[infodict["creator"]] = 1          # If the creator is a member, give them a vote
    for user, comment in commentlist:
        if user in memberlist:
            if comment == "lgtm":               # If a member commented LGTM, give them a vote
                votes[user] = 1
            elif comment == "veto":             # If a member commented VETO, give them a veto
                votes[user] = float("-inf")
    if sum(votes.values()) >= 2:
        return "Merged by "+infodict["botname"]+". "+infodict["status"]+". Verified looks good to "+", ".join(votes.keys())+"."
    return False

def status(pull, params):
    """Returns Basic Information For The Comments On The Pull In A List."""
    checked = False
    for commit in pull.get_commits():                                         # Loops through each commit
        checked = False
        for status in commit.get_statuses():                                  # Loops through each status on the commit
            if formatting(status.creator.login) == params["cibotname"]:       # Checks if the status was made by the CI bot
                if formatting(status.state) == "success":                     # Checks if the status from the most recent comment by the CI bot is success
                    checked = True
                    break
                else:
                    return False                                               # We only care about the most recent status from the CI bot, so if that isn't success, then end
        if not checked:
            return False
    if checked:
        return "Verified passes tests by "+params["cibotname"]+"."             # This string will be passed to check in infodict as infodict["status"]
    else:
        return False

def hookbot(repo, params):
    """Makes Sure The Repository Has A Hook In Place To Call The Bot."""
    config = {
        "url":params["hookurl"]                          # The config for the hook
        }
    for hook in repo.get_hooks():                       # Checks each hook to see if it is a hook for the bot
        if hook.name == params["hookname"]:               # If the hook already exists, exit the function
            hook.edit(params["hookname"], config, events=params["hookevents"], active=True)             # Updates the hook for the bot
    repo.create_hook(params["hookname"], config, events=params["hookevents"], active=True)              # Creates a hook for the bot

# Utility Functions:

def formatting(inputstring):
    """Insures All Strings Follow A Uniform Format For Ease Of Comparison."""
    out = ""
    for c in inputstring:
        if c in string.printable:        # Strips out all non-ascii characters
            out += c
    return str(out).strip().lower()     # Strips initial and trailing whitespace, and makes the whole thing lowercase

def commentlist(pull):
    """Returns Basic Information For The Comments On The Pull In A List."""
    comments = pull.get_issue_comments()
    commentlist = []
    for comment in comments:
        commentlist.append((formatting(comment.user.login), formatting(comment.body)))      # Makes a tuple of the name of the commenter and the body of the comment
    return commentlist

# Connecting To Github:

client = github.Github(params["botname"], params["password"])       # Logs into the bot's account
org = client.get_organization(params["orgname"])                    # Accesses ripple's github organization

# Creating The Necessary Objects:

openpulls = {}
for repo in org.get_repos():                                # Loops through each repo in ripple's github
    hookbot(repo, params)                                  # Makes sure the bot is hooked into the repository
    openpulls[repo] = []
    for pull in repo.get_pulls():                           # Loops through each pull request in each repo
        if not pull.is_merged() and pull.mergeable:         # Checks whether the pull request is still open and automatically mergeable
            openpulls[repo].append(pull)

members = org.get_members()                          # Gets a list of members
memberlist = []
for member in members:
    memberlist.append(formatting(member.login))     # Makes a list of member names

# Running The Middleware On The Objects:

for repo in openpulls:                                      # Loops through each layer of the previously constructed dict
    for pulls in openpulls[repo]:
        for pull in pulls:
            result = status(pull, params)      # Calls the status middleware function
            if result:                                      # If the status middleware function gives the okay, proceed
                infodict = {                                # Creates a dictionary of possibly relevant parameters to pass to the check middleware function
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
                infodict.update(params)                     # Includes the original initialization parameters in that
                message = check(commentlist(pull), memberlist, infodict)        # Calls the check middleware function
                if message:                                 # If the middleware function gives the okay,
                    pull.create_issue_comment(message)      # Create a comment with the middleware function's result and
                    pull.merge(message)                     # Merge using the middleware function's result as the description
