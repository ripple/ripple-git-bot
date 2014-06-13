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
    "lgtms" : ["lgtm"],                                             # What strings register as upvotes (no leading or trailing whitespace and all lowercase)
    "vetoes" : ["veto"],                                            # What strings register as veto votes ('')
    "downs" : [],                                                   # What strings register as downvotes ('')
    "message" : "Verified passes tests by <cibotname>. Verified looks good to <voters>.",        # The message displayed by the bot on merge
    "botname" : "ripplebot",                                        # The name of the ripple bot
    "orgname" : "ripple-git-test",                                  # The name of ripple's github organization
    "cibotname" : "evhub",                                          # The name of the ripple CI bot
    "hookurl" : "http://ripple-git-bot.herokuapp.com/",             # The url of the server file for hooking into
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
    "message" : "Verified passes tests by <cibotname>. Verified looks good to <voters>.",        # The message displayed by the bot on merge
    "lgtms" : ["lgtm"],                                             # What strings register as upvotes (no leading or trailing whitespace and all lowercase)
    "vetoes" : ["veto"],                                            # What strings register as veto votes ('')
    "downs" : [],                                                   # What strings register as downvotes ('')
    "votecount" : 3,                                                # The number of LGTM votes required to merge
    "repoparams" : {                                                # Specific parameters for each repo
        },
    "enabled" : True,                                               # Whether or not the bot is enabled
    "merge" : True,                                                 # Whether or not the bot should actually merge, or just comment
    "debug" : True                                                  # Turns on and off verbose debug output
    }

for param in params:
    name = "BOT_"+param.upper()                                     # Proper formatting for environment variable overrides is BOT_VAR
    if name in os.environ:
        params[param] = type(params[param])(os.environ[name])       # Make sure to convert to the proper type first
