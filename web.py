#!/usr/bin/python

# Imported Modules:

from __future__ import print_function
from flask import Flask
from gitbot import main

app = Flask(__name__)

@app.route("/")
def wrapper(*args, **kwargs):
    return main(*args, **kwargs)
