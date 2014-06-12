#!/usr/bin/python

# Imported Modules:

from __future__ import print_function
from config import os, params
from flask import Flask
from gitbot import main, printdebug

# Setting Up:

global working
working = False

app = Flask(__name__)           # Creates the application

# Running The Main Function:

@app.route("/", methods=['GET', 'POST'])                                    # Registers the script to run on hook or visit
def run():
    global working
    printdebug(params, "Initializing...")
    if working:                                                             # Prevents two scripts running at the same time
        printdebug(params, "    Failed due to concurrent boot.")
    elif not params["token"]:
        printdebug(params, "    Failed due to abscence of login token. Set the BOT_TOKEN environment variable to the bot's login token.")
    elif not (params["orgname"] and params["cibotname"] and params["message"] and params["votecount"] and params["debug"]):
        printdebug(params, "    Failed due to abscence of requisite config variables. Check your config.py for errors.")
    else:
        working = True
        memberlist, openpulls, merges = main(params)                                                                    # Runs the script and extracts the parameters
        printdebug(params, "Members: "+repr(memberlist)+"\nPull Requests: "+repr(openpulls)+"\nMerges: "+repr(merges))  # Displays a message with the output parameters
        working = False
        return "GitHub pull requests succesfully analyzed. Merged "+str(len(merges))+" pull requests."                  # Returns a summary string for website visitors
    return "Failed to boot up pull request analyzer. Check logs for more information."
