#!/usr/bin/python

# Imported Modules:

from __future__ import print_function
import github
import string

# Setting Up:

global count
count = 0

# Middleware Functions:

def status(pull, params):
    """Checks Whether Or Not pull Has Been Signed Off On By The CI Build Manager."""
    printdebug(params, "            Checking status...")
    if not params["travis"]:
        printdebug(params, "                Overriding status check.")
        return True
    else:
        commit = listify(pull.get_commits())[-1]                            # Only the last commit will have CI build statuses on it
        params.update({                                                     # Adds the most recent commit to the params
            "commit" : commit,
            "date" : commit.commit.author.date,
            "author" : formatting(commit.author.login)
            })
        printdebug(params, "                Found commit.")
        checked = False
        for status in commit.get_statuses():                                # Loops through each status on the commit
            name = formatting(status.creator.login)
            printdebug(params, "                    Found status from bot "+name+".")
            if name in params["cibotnames"]:                                # Checks if the status was made by the CI bot
                state = formatting(status.state)
                if state == "success":                                      # Checks if the status from the most recent comment by the CI bot is success
                    checked = True
                    printdebug(params, "                        CI bot reports commit passed tests.")
                    break
                elif state == "pending":
                    printdebug(params, "                        CI bot reports commit tests in progress.")
                    return False                                            # Pending doesn't mean success
                else:
                    printdebug(params, "                        CI bot reports commit failed tests.")
                    return False                                            # We only care about the most recent status from the CI bot, so if that isn't success, then end
        if not checked:
            printdebug(params, "                    CI bot not reporting for this commit.")
            return False
        if checked:
            printdebug(params, "                Status is success.")
            return True
        else:
            printdebug(params, "                Status is failure.")
            return False

def check(commentlist, params):
    """Checks That At Least votecount Members Have Commented LGTM And None Commented VETO."""
    printdebug(params, "            Checking comments...")
    votes = {}
    recvotes = {}
    if params["creator"] in params["members"]:
        votes[params["creator"]] = 1                        # If the creator is a member, give them a vote
        printdebug(params, "                Got LGTM vote from creator "+params["creator"]+".")
    if params["author"] in params["members"]:
        recvotes[params["author"]] = 1
        printdebug(params, "                Got recent LGTM vote from author "+params["author"]+".")
    for user, comment, date in commentlist:
        if user in params["members"]:
            voted = True
            if startswithany(comment, params["lgtms"]):     # If a member commented LGTM, give them a vote
                votes[user] = 1
                printdebug(params, "                Got LGTM vote from "+user+".")
            elif startswithany(comment, params["vetoes"]):  # If a member commented VETO, give them a veto
                votes[user] = float("-inf")
                printdebug(params, "                Got VETO vote from "+user+".")
            elif startswithany(comment, params["downs"]):   # If downs is set up, this will allow downvoting
                votes[user] = -1
                printdebug(params, "                Got DOWN vote from "+user+".")
            else:
                voted = False
            if date > params["date"]:
                params["comments"].append(comment)
                if voted:
                    recvotes[user] = votes[user]
                    printdebug(params, "                    Vote qualifies as recent.")
    if sum(votes.values()) >= params["votecount"] and sum(recvotes.values()) >= params["recvotes"]:
        printdebug(params, "                Found no VETO votes, at least "+str(params["votecount"])+" LGTM votes, and at least "+str(params["recvotes"])+" recent LGTM votes.")
        params["voters"] = ", ".join(votes.keys())
        params["recvoters"] = ", ".join(recvotes.keys())
        return messageproc(params, params["message"])
    else:
        printdebug(params, "                Found fewer than "+str(params["votecount"])+" LGTM votes, a VETO vote, or fewer than "+str(params["recvotes"])+" recent LGTM votes.")
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
        commentlist.append((formatting(comment.user.login), formatting(comment.body), comment.created_at))      # Makes a tuple of the name, the body, and the date
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
        global count
        for line in message.split("\n"):
            count += 1
            print(str(count)+". "+str(line))

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

def repoparams(params, name, search="repoparams"):
    """Sets The Repository-Specific Parameters."""
    newparams = dict(params)
    if name in params["repoparams"]:
        newparams.update(params["repoparams"][name])            # repoparams should be of the format { reponame : { newparam : value } }
        printdebug(params, "        "+"    "*(search=="tagparams")+"Updated parameters for "+str(name)+" to "+str(params["repoparams"][name]))
    return newparams

def repomembers(params, repo):
    """Adds Repository Collaborators To The Members."""
    params["members"] = params["members"][:]
    for user in repo.get_collaborators():
        name = formatting(user.login)
        if not name in params["members"]:
            printdebug(params, "        Found collaborator "+name+".")
            params["members"].append(name)
    return params

def pullparams(params, title):
    """Sets Pull-Request-Title-Specific Parameters."""
    if title.startswith("["):
        tag = formatting(title[1:].split("]", 1)[0])            # A tag is of the format [Tag]
        return repoparams(params, tag, search="tagparams")      # Uses repoparams for the actual checking, but with the tagparams variable
    else:
        return dict(params)

# The Main Function:

def main(params):

    # Connecting To Github:

    printdebug(params, "Connecting to GitHub as bot...")
    client = github.Github(params["token"])                     # Logs into the bot's account
    params["token"] = "*"*len(params["token"])                  # Obliterates the token after use

    printdebug(params, "Connecting to organization "+params["orgname"]+"...")
    org = client.get_organization(params["orgname"])            # Accesses ripple's github organization

    params.update({                                             # Adds the client and the org to the params
        "client" : client,
        "org" : org
        })

    # Creating The Necessary Objects:

    printdebug(params, "Scanning members...")
    memberlist = []
    if params["orgvote"]:
        members = org.get_members()                             # Gets a list of members
        for member in members:
            name = formatting(member.login)
            printdebug(params, "    Found member "+name+".")
            memberlist.append(name)                             # Makes a list of member names

    params.update({                                             # Adds the memberlist to the params
        "members" : memberlist
        })

    printdebug(params, "Scanning repositories...")
    openpulls = {}
    for repo in org.get_repos():                                # Loops through each repo in ripple's github
        name = formatting(repo.name)
        printdebug(params, "    Scanning repository "+name+"...")
        newparams = repoparams(params, name)
        if newparams["enabled"]:                                # Checks whether or not the bot is enabled for this repo
            printdebug(newparams, "    Entering repository "+name+"...")
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
        printdebug(params, "    Scanning repository "+name+"...")
        newparams = repomembers(repoparams(params, name), repo)
        if newparams["enabled"]:                                # Checks whether or not the bot is enabled for this repo
            printdebug(newparams, "    Entering repository "+name+"...")
            for pull in openpulls[repo]:
                printdebug(newparams, "        Found pull request.")
                newparams.update({                              # Adds parameters for use by status
                        "creator" : formatting(pull.user.login),
                        "repo" : repo,
                        "pull" : pull
                        })
                newparams = pullparams(newparams, formatting(pull.title))
                result = status(pull, newparams)                # Calls the status middleware function
                if result:                                      # If the status middleware function gives the okay, proceed
                    newparams.update({                          # Creates a dictionary of possibly relevant parameters to pass to the check middleware function
                        "status" : result,
                        "comments" : []
                        })
                    message = check(commentlist(pull), newparams)       # Calls the check middleware function
                    if message:                                 # If the middleware function gives the okay,
                        merges.append((pull, message))
                        printdebug(newparams, "        Merging pull request with comment '"+message+"'...")
                        if not formatting(message) in newparams["comments"]:
                            pull.create_issue_comment(message)  # Create a comment with the middleware function's result
                            printdebug(newparams, "            Pull request commented on.")
                        if newparams["merge"]:
                            pull.merge(message)                 # Merge using the middleware function's result as the description
                            printdebug(newparams, "            Pull request merged.")

    # Cleaning Up:

    printdebug(params, "Finished.")
    return openpulls, merges
