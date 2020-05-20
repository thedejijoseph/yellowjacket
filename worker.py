
import time
import os

import schedule

import grabber

schedule.every(5).minutes.do(grabber.run)

while True:
    schedule.run_pending()
    time.sleep(1)
