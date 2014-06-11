#!/usr/bin/python

# Imported Modules:

from __future__ import print_function
import os
from flask import Flask
from gitbot import printdebug, main
from config import params

app = Flask(__name__)

@app.route("/")
def run():
    printdebug(params, "Initializing...")
    members, openpulls, merges = main(params)
    printdebug(params, "Members: "+repr(memberlist)+"\nPull Requests: "+repr(openpulls)+"\nMerges: "+repr(merges))
    return "GitHub pull requests succesfully analyzed. Merged "+str(len(merges))+" pull requests."
