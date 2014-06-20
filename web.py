#!/usr/bin/python

# Imported Modules:

from __future__ import print_function
from config import os, params
from flask import Flask
from copy import deepcopy
from gitbot import main, printdebug

# Setting Up:

global working
working = False

app = Flask(__name__)           # Creates the application

# Running The Main Function:

@app.route("/", methods=['GET', 'POST'])                                    # Registers the script to run on hook or visit
def run():
    printdebug(params, "Initializing...")
    newparams = deepcopy(params)
    printdebug(params, "Using parameters: "+repr(newparams))
    global working
    if working:                                                             # Prevents two scripts running at the same time
        printdebug(newparams, "    Failed due to concurrent boot.")
    elif not newparams["orgname"]:
        printdebug(newparams, "    Failed due to abscence of organization name. Set the BOT_ORGNAME environment variable to the name of the organization.")
    elif not newparams["token"]:
        printdebug(newparams, "    Failed due to abscence of login token. Set the BOT_TOKEN environment variable to the bot's login token.")
    else:
        working = True
        try:
            openpulls, merges = main(newparams)                                                                 # Runs the script and extracts the parameters
        finally:
            working = False
        printdebug(newparams, "Pull Requests: "+repr(openpulls)+"\nMerges: "+repr(merges))                      # Displays a message with the output parameters
        return "GitHub pull requests succesfully analyzed. Merged "+str(len(merges))+" pull requests."          # Returns a summary string for website visitors
    return "Failed to boot up pull request analyzer. Check logs for more information."
