#!/usr/bin/python

# Imported Modules:

from __future__ import print_function
import os

# Initialization Parameters:

params = {
    "token" : "",                                                   # The login token for the bot (this should usually be passed as an environment variable)
    "orgname" : "",                                                 # The name of ripple's github organization
    "cibotname" : "",                                               # The name of the ripple CI bot
    "hookurl" : "",                                                 # The url of the server file for hooking into
    "votecount" : 2,                                                # The number of LGTM votes required to merge
    "recvotes" : 1,                                                 # How many of those have to be after the most recent commit
    "message" : "Ready to merge: Travis build checks out, pull request looks good to <voters>, most recent commit looks good to <recvoters>.",        # The message displayed by the bot on merge
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
    "repoparams" : {                                                # Specific parameters for each repo
        },
    "enabled" : True,                                               # Whether or not the bot is enabled
    "merge" : False,                                                # Whether or not the bot should actually merge, or just comment
    "debug" : True                                                  # Turns on and off verbose debug output
    }

for param in params:
    name = "BOT_"+param.upper()                                     # Proper formatting for environment variable overrides is BOT_VAR
    if name in os.environ:
        params[param] = type(params[param])(os.environ[name])       # Make sure to convert to the proper type first
