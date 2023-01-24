#!/usr/bin/env python3

import logging
import os
import sqlite3
import time
from signalwire.relay.consumer import Consumer

class CustomConsumer(Consumer):
  def setup(self):
    self.project = os.environ.get('PROJECT', None)
    self.token = os.environ.get('TOKEN', None)
    self.contexts = ['dialer']

  async def ready(self):
    logging.info('Dialer App Consumer Ready')
    db = sqlite3.connect("database.db")
    cursor = db.cursor()

    # Create the dialto table if it doesn't exist
    dialto_table = """ CREATE TABLE if not exists dialto (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        to_num TEXT NOT NULL,
        from_num TEXT NOT NULL
        );"""

    cursor.execute(dialto_table)
    db.commit()

    while True:
        to_num = ""
        from_num = ""

        results = cursor.execute(
            "SELECT id, to_num, from_num from dialto limit 1"
        ).fetchall()

        # TODO: Turn this off to save disk/memory space
        if len(results) == 0:
            logging.info ('nothing to do')
            time.sleep(3)

        else:
            for i, t, f in results:
                id = i
                to_num = t
                from_num = f

            # "POP" record the database
            cursor.execute(
                "DELETE FROM dialto where id = ?",
                (id,)
            )
            db.commit()

            dial_result = await self.client.calling.dial(to_number=to_num, from_number=from_num)
            if dial_result.successful is False:
                logging.info('Outboud call failed.')

            amd = await dial_result.call.amd(wait_for_beep=True)
            logging.info(f'AMD Result: {amd.result}')

            if amd.successful and amd.result =='MACHINE':
                await dial_result.call.play_tts(text='Sorry we missed you.  We will call back later!')

            if amd.successful and amd.result == 'HUMAN':
                # If we detect a HUMAN, say hello and play an audio file.
                agent_dest = self.project = os.environ.get('AGENT_DEST', None)
                devices = [
                  { 'to_number': agent_dest, 'timeout': 15 }
                ]
                await dial_result.call.connect(device_list=devices)
                #await dial_result.call.play_tts(text='need something here for now')


            #await dial_result.call.hangup()
            #logging.info('The call has hung up')

  def teardown(self):
    logging.info('Consumer teardown..')

consumer = CustomConsumer()
consumer.run()
