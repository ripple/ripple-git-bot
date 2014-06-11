#!/usr/bin/python

# Imported Modules:

from __future__ import print_function

# Initialization Parameters:

params = {
    "message" : "Verified passes tests by <cibotname>. Verified looks good to <voters>.",        # The message displayed by the bot on merge
    "botname" : "ripplebot",                                        # The name of the ripple bot
    "password" : "ripplepass1",                                      # The password to the ripple bot's account
    "orgname" : "ripple-git-test",                                  # The name of ripple's github organization
    "cibotname" : "evhub",                                          # The name of the ripple CI bot
    "hookurl" : "http://ripple-git-bot.herokuapp.com/",             # The url of the server file for hooking into
    "hookname" : "web",                                              # The new name of the hooks into this file
    "hooknames" : ["web"],                                          # All the names of the hooks into this file
    "hookevents" : [                                                # The different events the hook is triggered on
                 "commit_comment",
                 "issue_comment",
                 "pull_request",
                 "member",
                 "deployment",
                 "deployment_status",
                 "status"
                 ],
    "votecount" : 2,                                                # The number of LGTM votes required to merge
    "debug" : True                                                  # Turns on and off the debug output
    }
