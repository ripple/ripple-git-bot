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

app = Flask(__name__)

# Running The Main Function:

@app.route("/")
def run():
    global working
    printdebug(params, "Initializing...")
    if working:
        printdebug(params, "    Failed due to concurrent boot.")
    else:
        working = True
        memberlist, openpulls, merges = main(params)
        printdebug(params, "Members: "+repr(memberlist)+"\nPull Requests: "+repr(openpulls)+"\nMerges: "+repr(merges))
        working = False
        return "GitHub pull requests succesfully analyzed. Merged "+str(len(merges))+" pull requests."
