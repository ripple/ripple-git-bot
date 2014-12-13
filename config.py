#!/usr/bin/python

# Imported Modules:

from __future__ import print_function
import os

# Utility Functions:

def clean(haystack, needle=""):
    """Cleans A Needle From A Haystack."""
    out = []
    for item in haystack:
        if item != needle:
            out.append(item)
    return out

# Initialization Parameters:

params = {
    "token" : "",                                                   # The login token for the bot (this should usually be passed as an environment variable)
    "orgname" : "",                                                 # The name of ripple's github organization
    "cibotnames" : [],                                              # The names of ripple's CI bots
    "hookurl" : "",                                                 # The url of the server file for hooking into
    "mergestring": "@ripplebot merge",                              # What string tells the bot to merge the pull request
    "votecount" : 2,                                                # The number of LGTM votes required to merge
    "recvotes" : 3,                                                 # How many of those have to be after the most recent commit
    "message" : "Ready to merge: Travis build checks out, most recent commit looks good to <recvoters>.",        # The message displayed by the bot on merge
    "lgtms" : ["lgtm"],                                             # What strings register as upvotes (no leading or trailing whitespace and all lowercase)
    "vetoes" : ["veto"],                                            # What strings register as veto votes ('')
    "downs" : [],                                                   # What strings register as downvotes ('')
    "hookname" : "web",                                             # The new name of the hooks into this file
    "hooknames" : ["web"],                                          # All the names of the hooks into this file
    "hookevents" : [                                                # The different events the hook is triggered on
                 "commit_comment",
                 "issue_comment",
                 "pull_request",
                 "member",
                 "status",
                 "create"
                 ],
    "tagparams" : {
        "fix" : {
            "recvotes" : 2
            },
        "bug" : {
            "recvotes" : 2
            },
        "test" : {
            "recvotes" : 2
            },
        "doc" : {
            "recvotes" : 2
            },
        "task" : {
            "recvotes" : 2
            },
        "chore" : {
            "recvotes" : 2
            }
        },
    "repoparams" : {                                                # Specific parameters for each repo
        "ripple-lib" : {
            "enabled" : True
            },
        "ripple-client" : {
            "enabled" : True
            },
        "gatewayd" : {
            "enabled" : True
            },
        "ripple-rest" : {
            "enabled" : True
            }
        },
    "travis" : True,                                                # Whether or not to check Travis for build status
    "orgvote" : False,                                              # Whether or not the votes of all organization members should count
    "enabled" : True,                                               # Whether or not the bot is enabled
    "merge" : True,                                                 # Whether or not the bot should actually merge, or just comment
    "debug" : True                                                  # Turns on and off verbose debug output
    }

for param in params:
    name = "BOT_"+param.upper()                                     # Proper formatting for environment variable overrides is BOT_VAR
    if name in os.environ:
        constr = type(params[param])
        params[param] = str(os.environ[name])
        if constr == list:                                          # Allow semicolon seperating in enviro vars for lists
            params[param] = clean(params[param].split(";"))
        elif constr == bool:                                        # Allow bool names in enviro vars for bools
            params[param] = params[param].lower()
            if params[param] == "false":
                params[param] = False
            elif params[param] == "true":
                params[param] = True
            else:
                raise ValueError("Invalid bool name "+params[param])
        else:
            params[param] = constr(params[param])                   # Make sure to convert to the proper type
