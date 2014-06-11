#!/usr/bin/python

# Imported Modules:

from __future__ import print_function
import os
from flask import Flask
from gitbot import printdebug, main
from config import params

# Setting Up:

global working
working = False

app = Flask(__name__)           # Creates the application

# Running The Main Function:

@app.route("/", methods=['GET', 'POST'])                                                                                    # Registers the script to run on hook or visit
def run():
    global working
    printdebug(params, "Initializing...")
    if working:                                                                                                             # Prevents two scripts running at the same time
        printdebug(params, "    Failed due to concurrent boot.")
    elif not "BOT_TOKEN" in os.environ:
        printdebug(params, "    Failed due to abscence of login token. Set the BOT_TOKEN environment variable to the bot's login token.")
    else:
        working = True
        params["token"] = os.environ["BOT_TOKEN"]                                                                     # Fetch the password from an environment variable
        memberlist, openpulls, merges = main(params)                                                                        # Runs the script and extracts the parameters
        printdebug(params, "Members: "+repr(memberlist)+"\nPull Requests: "+repr(openpulls)+"\nMerges: "+repr(merges))      # Displays a message with the output parameters
        working = False
        return "GitHub pull requests succesfully analyzed. Merged "+str(len(merges))+" pull requests."                      # Returns a summary string for website visitors
