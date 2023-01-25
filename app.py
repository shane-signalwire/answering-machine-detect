#!/usr/bin/env python3
# Author: Shane Harrell

from signalwire.voice_response import *
import urllib.parse
import requests
import sqlite3
import re
import os
import logging
from flask import Flask
from flask import request
from flask import render_template
amd = Flask(__name__)


@amd.route('/')
def my_form():
    return render_template('my-form.html')

@amd.route('/logs' methods=['POST'])
def my_form_post():
    response=""
    db = sqlite3.connect("/app/storage/database.db")
    cursor = db.cursor()

    rows = cursor.execute(
        "SELECT to_num, from_num, amd_response from dialto where amd_response is not null order by id desc limit 25"
    ).fetchall()

    response="    ID     |  Dialed Number  |  Calling Number |  AMD result<br>+++++++++++++++++++++++++++++++++++++++<br>"
    for i, d, c, a in rows:
        response=response + str(i) + "  |  " + str(d) + "  |  " + str(c) + "  |  " + str(a) + "<br>"

    return response

@amd.route('/', methods=['POST'])
def my_form_post():
    response = ""
    #from_num_ = os.environ.get('FROM_NUMBER', None)
    from_num_ = request.form.get("fnum")

    phone_num_regex = re.compile(r'^\+1\d{10}$')
    good_num = phone_num_regex.search(from_num_)

    if good_num is None:
        response = "The from number is not valid"
        return response


    numbers = str.split(request.form['dest_list'])

    # Put each number in the database for dialier pickup
    for num in numbers:
        db = sqlite3.connect("/app/storage/database.db")
        cursor = db.cursor()

        to_num_ = num

        phone_num_regex = re.compile(r'^\+1\d{10}$')
        good_num = phone_num_regex.search(to_num_)

        if good_num is not None:
            cursor.execute(
              "INSERT INTO dialto (to_num, from_num) VALUES (?, ?)",
              (to_num_, from_num_,)
            )

            db.commit()
            db.close()
            response = response + to_num_ + " added to queue\n<br>"
        else:
            logging.info(f'{to_num_} is not a valid number')
            response =  response + to_num_ + ": is not a valid number<br>"

    return response

if __name__ == '__main__':
    amd.run()
