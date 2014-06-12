#!/usr/bin/python

# Imported Modules:

from __future__ import print_function
import github
import string

# Middleware Functions:

def status(pull, params):
    """Checks Whether Or Not pull Has Been Signed Off On By The CI Build Manager."""
    printdebug(params, "            Checking status...")
    checked = False
    commit = listify(pull.get_commits())[-1]                            # Only the last commit will have CI build statuses on it
    printdebug(params, "            Found commit.")
    checked = False
    for status in commit.get_statuses():                                # Loops through each status on the commit
        name = formatting(status.creator.login)
        printdebug(params, "                Found status from bot "+name+".")
        if name == params["cibotname"]:                                 # Checks if the status was made by the CI bot
            state = formatting(status.state)
            if state == "success":                                      # Checks if the status from the most recent comment by the CI bot is success
                checked = True
                printdebug(params, "                    CI bot reports commit passed tests.")
                break
            elif state == "pending":
                printdebug(params, "                    CI bot reports commit tests in progress.")
                return False                                            # Pending doesn't mean success
            else:
                printdebug(params, "                    CI bot reports commit failed tests.")
                return False                                            # We only care about the most recent status from the CI bot, so if that isn't success, then end
    if not checked:
        printdebug(params, "                CI bot not reporting for this commit.")
        return False
    if checked:
        printdebug(params, "            Status is success.")
        return True
    else:
        printdebug(params, "            Status is failure.")
        return False

def check(commentlist, memberlist, params):
    """Checks That At Least votecount Members Have Commented LGTM And None Commented VETO."""
    printdebug(params, "            Checking comments...")
    votes = {}
    if params["creator"] in memberlist:
        votes[params["creator"]] = 1                        # If the creator is a member, give them a vote
        printdebug(params, "                Got LGTM vote from "+params["creator"]+".")
    for user, comment in commentlist:
        if user in memberlist:
            if startswithany(comment, params["lgtms"]):     # If a member commented LGTM, give them a vote
                votes[user] = 1
                printdebug(params, "                Got LGTM vote from "+user+".")
            elif startswithany(comment, params["vetoes"]):  # If a member commented VETO, give them a veto
                votes[user] = float("-inf")
                printdebug(params, "                Got VETO vote from "+user+".")
            elif startswithany(comment, params["downs"]):   # If downs is set up, this will allow downvoting
                votes[user] = -1
                printdebug(params, "                Got DOWN vote from "+user+".")
    if sum(votes.values()) >= params["votecount"]:
        printdebug(params, "            Found no VETO votes, at least "+str(params["votecount"])+" LGTM votes.")
        params["voters"] = ", ".join(votes.keys())
        return messageproc(params, params["message"])
    else:
        printdebug(params, "            Found less than "+str(params["votecount"])+" LGTM votes, or a VETO vote.")
        return False

# Utility Functions:

def startswithany(inputstring, inputlist):
    """Determines Whether A String Starts With Any Of The Items In A List."""
    for item in inputlist:
        if inputstring.startswith(item):
            return True
    return False

def formatting(inputstring):
    """Insures All Strings Follow A Uniform Format For Ease Of Comparison."""
    out = ""
    for c in inputstring:
        if c in string.printable:       # Strips out all non-ascii characters
            out += c
    return str(out).strip().lower()     # Strips initial and trailing whitespace, and makes the whole thing lowercase

def listify(pagelist):
    """Turns A github List Into A Python List."""
    out = []
    for item in pagelist:               # github lists can often only be traversed as iters, this turns them into actual lists
        out.append(item)
    return out

def commentlist(pull):
    """Returns Basic Information For The Comments On The Pull In A List."""
    comments = pull.get_issue_comments()
    commentlist = []
    for comment in comments:
        commentlist.append((formatting(comment.user.login), formatting(comment.body)))      # Makes a tuple of the name of the commenter and the body of the comment
    return commentlist

def messageproc(params, message):
    """Replaces Variables In A Message."""
    out = ""
    varstring = None                                # Everything since the last < is stored in varstring
    for c in message:
        if varstring != None:
            if c == "<":                            # If there's another < in the varstring, start a new one
                out += "<"+varstring
                varstring = None
            elif c != ">":
                varstring += c
            elif varstring in params:               # If the varstring exists, substitute it
                out += str(params[varstring])
                varstring = None
            else:                                   # Otherwise, don't do anything
                out += "<"+varstring+">"
                varstring = None
        elif c == "<":                              # If a < is found, open up a new varstring
            varstring = ""
        else:
            out += c
    if varstring != None:                           # Check to see whether anything is still left in the varstring
        out += "<"+varstring
    return out

def printdebug(params, message):
    """Prints A Message If The Debug Variable Is Set To True."""
    if params["debug"]:
        if not "count" in params:
            params["count"] = 0
        for line in message.split("\n"):
            params["count"] += 1
            print(str(params["count"])+". "+str(line))

def hookbot(repo, params):
    """Makes Sure The Repository Has A Hook In Place To Call The Bot."""
    printdebug(params, "        Scanning hooks...")
    if params["hookurl"]:
        config = {
            "url":params["hookurl"]                                                                 # The config for the hook
            }
        for hook in repo.get_hooks():                                                               # Checks each hook to see if it is a hook for the bot
            name = formatting(hook.name)
            printdebug(params, "            Found hook "+name+".")
            if name in params["hooknames"]:                                                          # If the hook already exists, exit the function
                printdebug(params, "                Updating hook...")
                hook.edit(params["hookname"], config, events=params["hookevents"], active=True)     # Updates the hook for the bot
                return True
        printdebug(params, "        Creating new hook "+params["hookname"]+"...")
        repo.create_hook(params["hookname"], config, events=params["hookevents"], active=True)      # Creates a hook for the bot
        return True
    else:
        printdebug(params, "            No hook url found.")
        return False

def repoparams(params, name):
    """Sets The Repository-Specific Parameters."""
    newparams = dict(params)
    if name in params["repoparams"]:
        newparams.update(params["repoparams"]["name"])          # repoparams should be of the format { reponame : { newparam : value } }
    return newparams

# The Main Function:

def main(params):

    # Connecting To Github:

    printdebug(params, "Connecting to GitHub as bot...")
    client = github.Github(params["token"])                     # Logs into the bot's account

    printdebug(params, "Connecting to organization "+params["orgname"]+"...")
    org = client.get_organization(params["orgname"])            # Accesses ripple's github organization

    params.update({                                             # Adds the client and the org to the params
        "client" : client,
        "org" : org
        })

    # Creating The Necessary Objects:

    printdebug(params, "Scanning members...")
    members = org.get_members()                                 # Gets a list of members
    memberlist = []
    for member in members:
        name = formatting(member.login)
        printdebug(params, "    Found member "+name+".")
        memberlist.append(name)                                 # Makes a list of member names

    params.update({                                             # Adds the memberlist to the params
        "members" : memberlist
        })

    printdebug(params, "Scanning repositories...")
    openpulls = {}
    for repo in org.get_repos():                                # Loops through each repo in ripple's github
        name = formatting(repo.name)
        newparams = repoparams(params, name)
        if newparams["enabled"]:                                # Checks whether or not the bot is enabled for this repo
            printdebug(newparams, "    Scanning repository "+name+"...")
            hookbot(repo, newparams)                            # Makes sure the bot is hooked into the repo
            openpulls[repo] = []
            for pull in repo.get_pulls():                       # Loops through each pull request in each repo
                printdebug(newparams, "        Found pull request.")
                if not pull.is_merged() and pull.mergeable:     # Checks whether the pull request is still open and automatically mergeable
                    printdebug(newparams, "            Pull request is open and mergeable.")
                    openpulls[repo].append(pull)

    params.update({                                             # Adds the openpulls to the params
        "pulls" : openpulls
        })

    # Running The Middleware On The Objects:

    printdebug(params, "Running objects...")
    merges = []
    for repo in openpulls:                                      # Loops through each layer of the previously constructed dict
        name = formatting(repo.name)
        newparams = repoparams(params, name)
        if newparams["enabled"]:                                # Checks whether or not the bot is enabled for this repo
            printdebug(newparams, "    Entering repository "+name+"...")
            for pull in openpulls[repo]:
                printdebug(newparams, "        Found pull request.")
                result = status(pull, newparams)                # Calls the status middleware function
                if result:                                      # If the status middleware function gives the okay, proceed
                    newparams.update({                          # Creates a dictionary of possibly relevant parameters to pass to the check middleware function
                        "creator" : formatting(pull.user.login),
                        "repo" : repo,
                        "pull" : pull,
                        "status" : result
                        })
                    message = check(commentlist(pull), memberlist, newparams)       # Calls the check middleware function
                    if message:                                 # If the middleware function gives the okay,
                        merges.append((pull, message))
                        printdebug(newparams, "        Merging pull request with comment '"+message+"'...")
                        pull.create_issue_comment(message)      # Create a comment with the middleware function's result and
                        pull.merge(message)                     # Merge using the middleware function's result as the description
                        printdebug(newparams, "        Pull request merged.")

    # Cleaning Up:

    printdebug(params, "Finished.")
    return memberlist, openpulls, merges
