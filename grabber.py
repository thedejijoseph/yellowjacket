import os
import time
import logging
from datetime import datetime

from bs4 import BeautifulSoup
from selenium import webdriver

import storage

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

stream = logging.StreamHandler()
stream_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream.setFormatter(stream_formatter)

logger.addHandler(stream)


def page_loaded(driver):
    try:
        if driver.find_element_by_id('advancers'):
            return True
        else:
            return False
    except:
        return False

def get_snapshot(soup=None):
    target_data = soup.find('div', attrs={'id': 'snapshot'})
    table_body = target_data.find('tbody')
    data_rows = table_body.find_all('tr')[:-1]

    snapshot = {}
    for row in data_rows:
        variable, value = row.find_all('td')
        
        indicator = variable.text.strip().lower().replace(' ', '_')
        value = value.text
        snapshot[indicator] = value
    
    return snapshot

def get_trades(soup=None):
    target_data = soup.find('div', attrs={'id': 'traders'})
    table_body = target_data.find('tbody')
    data_rows = table_body.find_all('tr')[:-1]

    trades = []
    for row in data_rows:
        symbol, volume, value = row.find_all('td')
        trades.append([symbol.text, volume.text, value.text])
    
    return trades

def get_advancers(soup=None):
    target_data = soup.find('div', attrs={'id': 'advancers'})
    table_body = target_data.find('tbody')
    data_rows = table_body.find_all('tr')[:-1]

    advancers = []
    for row in data_rows:
        symbol, last_close, current, change, pct = row.find_all('td')
        advancers.append([symbol.text, last_close.text, current.text, change.text, pct.text])
    
    return advancers

def get_decliners(soup=None):
    target_data = soup.find('div', attrs={'id': 'decliners'})
    table_body = target_data.find('tbody')
    data_rows = table_body.find_all('tr')[:-1]

    decliners = []
    for row in data_rows:
        symbol, last_close, current, change, pct = row.find_all('td')
        decliners.append([symbol.text, last_close.text, current.text, change.text, pct.text])
    
    return decliners

"""
todo:
    + code retry-on-failure feature into grabber block
    + introduce logging script-wide
    + introduce env variables into webdriver creation
    + introduce database saving into project
    introduce scheduling upon deployment
"""
def run(test=False):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--remote-debugging-port=9222')
    options.add_argument('--log-level=3')
    options.binary_location = os.getenv('CHROME_BIN_PATH')

    logger.debug('Opening web driver.')
    driver = webdriver.Chrome(executable_path=os.getenv('CHROME_EXEC_PATH'), options=options,)
    driver.get('http://www.nse.com.ng')

    number_of_retries = 12
    try_count = 0
    while try_count <= number_of_retries:
        if page_loaded(driver):
            break
        else:
            logger.warning(f'Could not reach the internet. Retrying. Count: {try_count}.')
            if try_count == number_of_retries:
                # log iinability to reach internet and terminate
                logger.critical('Could not reach the internet. Terminating.')
                return
            time.sleep(3)
            driver.get('http://www.nse.com.ng')
            try_count += 1
            continue
    
    logger.info('Fetched web page. Parsing.')
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    if test:
        logger.debug('Closing web driver.')
        driver.quit()
        return soup
    
    log_time = str(datetime.now())
    
    logger.debug('Saving Index Snapshot data.')
    snapshot = get_snapshot(soup=soup)
    storage.save_snapshot(snapshot, log_time=log_time)
      
    logger.debug('Saving Trades data.')
    trades = get_trades(soup=soup)
    storage.save_trades(trades, log_time=log_time)

    logger.debug('Saving Advancers data.')
    advancers = get_advancers(soup=soup)
    storage.save_advancers(advancers, log_time=log_time)
    
    logger.debug('Saving Decliners data.')
    decliners = get_decliners(soup=soup)
    storage.save_decliners(decliners, log_time=log_time)
    
    logger.info('Finished saving data.')
    logger.debug('Closing web driver.')
    driver.quit()

if  __name__ == "__main__":
    run()
