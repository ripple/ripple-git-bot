#!/usr/bin/python

# Imported Modules:

from __future__ import print_function
import os
from flask import Flask
from gitbot import main
from config import params

app = Flask(__name__)

@app.route("/")
def run():
    print("Initializing...")
    print("Result: "+repr(main(params)))
    return "GitHub pull requests succesfully analyzed."
