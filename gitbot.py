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
            if formatting(status.state) == "success":                   # Checks if the status from the most recent comment by the CI bot is success
                checked = True
                printdebug(params, "                    CI bot reports commit passed tests.")
                break
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

def check(commentlist, memberlist, infodict):
    """Checks That At Least votecount Members Have Commented LGTM And None Commented VETO."""
    printdebug(params, "            Checking comments...")
    votes = {}
    if infodict["creator"] in memberlist:
        votes[infodict["creator"]] = 1          # If the creator is a member, give them a vote
        printdebug(params, "                Got LGTM vote from "+infodict["creator"]+".")
    for user, comment in commentlist:
        if user in memberlist:
            if comment == "lgtm":               # If a member commented LGTM, give them a vote
                votes[user] = 1
                printdebug(params, "                Got LGTM vote from "+user+".")
            elif comment == "veto":             # If a member commented VETO, give them a veto
                votes[user] = float("-inf")
                printdebug(params, "                Got VETO vote from "+user+".")
    if sum(votes.values()) >= infodict["votecount"]:
        printdebug(params, "            Found no VETO votes, at least "+str(infodict["votecount"])+" LGTM votes.")
        infodict["voters"] = ", ".join(votes.keys())
        return messageproc(infodict, infodict["message"])
    else:
        printdebug(params, "            Found less than "+str(infodict["votecount"])+" LGTM votes, or a VETO vote.")
        return False

# Utility Functions:

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
        print(message)

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
            if name == params["hookname"]:                                                          # If the hook already exists, exit the function
                printdebug(params, "                Updating hook...")
                hook.edit(params["hookname"], config, events=params["hookevents"], active=True)     # Updates the hook for the bot
        printdebug(params, "        Creating new hook "+params["hookname"]+"...")
        repo.create_hook(params["hookname"], config, events=params["hookevents"], active=True)      # Creates a hook for the bot
    else:
        printdebug(params, "            No hook url found.")

# The Main Function:

def main(params):

    # Connecting To Github:

    printdebug(params, "Connecting to GitHub under login "+params["botname"]+"...")
    client = github.Github(params["botname"], params["password"])       # Logs into the bot's account

    printdebug(params, "Connecting to organization "+params["orgname"]+"...")
    org = client.get_organization(params["orgname"])                    # Accesses ripple's github organization

    # Creating The Necessary Objects:

    printdebug(params, "Scanning members...")
    members = org.get_members()                                 # Gets a list of members
    memberlist = []
    for member in members:
        name = formatting(member.login)
        printdebug(params, "    Found member "+name+".")
        memberlist.append(name)                                 # Makes a list of member names

    printdebug(params, "Scanning repositories...")
    openpulls = {}
    for repo in org.get_repos():                                # Loops through each repo in ripple's github
        printdebug(params, "    Scanning repository "+formatting(repo.name)+"...")
        hookbot(repo, params)                                   # Makes sure the bot is hooked into the repository
        openpulls[repo] = []
        for pull in repo.get_pulls():                           # Loops through each pull request in each repo
            printdebug(params, "        Found pull request.")
            if not pull.is_merged() and pull.mergeable:         # Checks whether the pull request is still open and automatically mergeable
                printdebug(params, "            Pull request is open and mergeable.")
                openpulls[repo].append(pull)

    # Running The Middleware On The Objects:

    printdebug(params, "Running objects...")
    for repo in openpulls:                                      # Loops through each layer of the previously constructed dict
        printdebug(params, "    Entering repo "+formatting(repo.name)+"...")
        for pull in openpulls[repo]:
            printdebug(params, "        Found pull request.")
            result = status(pull, params)                       # Calls the status middleware function
            if result:                                          # If the status middleware function gives the okay, proceed
                infodict = {                                    # Creates a dictionary of possibly relevant parameters to pass to the check middleware function
                    "creator" : formatting(pull.user.login),
                    "repo" : repo,
                    "pull" : pull,
                    "pulls" : openpulls,
                    "client" : client,
                    "org" : org,
                    "members" : memberlist,
                    "status" : result
                    }
                infodict.update(params)                         # Includes the original initialization parameters in that
                message = check(commentlist(pull), memberlist, infodict)        # Calls the check middleware function
                if message:                                     # If the middleware function gives the okay,
                    printdebug(params, "        Merging pull request with comment '"+message+"'...")
                    pull.create_issue_comment(message)          # Create a comment with the middleware function's result and
                    pull.merge(message)                         # Merge using the middleware function's result as the description
                    printdebug(params, "        Pull request merged.")

    # Cleaning Up:

    printdebug(params, "Finished.")
    return client, org, memberlist, openpulls
