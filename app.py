#!/usr/bin/env python3
# Author: Shane Harrell

from signalwire.voice_response import *
import urllib.parse
import requests
import sqlite3
import os
from flask import Flask
from flask import request
from flask import render_template
amd = Flask(__name__)


@amd.route('/')
def my_form():
    return render_template('my-form.html')


@amd.route('/', methods=['POST'])
def my_form_post():
    from_num_ = os.environ.get('FROM_NUMBER', None)
    numbers = str.split(request.form['text'])
    for num in numbers:
        #TODO: validate that the number is a valid e164 number
        # Put each number in the Database
        db = sqlite3.connect("/app/storage/database.db")
        cursor = db.cursor()

        to_num_ = num
        cursor.execute(
            "INSERT INTO dialto (to_num, from_num) VALUES (?, ?)",
            (to_num_, from_num_,)
        )

        db.commit()
    return numbers

if __name__ == '__main__':
    amd.run()
