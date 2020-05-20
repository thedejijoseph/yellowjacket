import os
import logging
from datetime import datetime

from bs4 import BeautifulSoup
from selenium import webdriver


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

    snapshot = []
    for row in data_rows:
        variable, value = row.find_all('td')
        snapshot.append([variable.text.strip(), value.text])
    
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
    introduce env variables into webdriver creation
    introduce database saving into project
"""
def run():
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
            
            driver.get('http://www.nse.com.ng')
            try_count += 1
            continue
    
    logger.info('Fetched web page. Parsing.')
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    log_time = str(datetime.now())

    # quick hack for testing on heroku
    if not os.path.exists('data'):
        logger.debug('Creating new data directory.')
        os.mkdir('data')
        open('data/advancers.csv', 'w').close()
        open('data/decliners.csv', 'w').close()
        open('data/snapshots.csv', 'w').close()
        open('data/trades.csv', 'w').close()

    logger.debug('Saving Advancers data.')
    advancers = get_advancers(soup=soup)
    with open('data/advancers.csv', 'a') as f:
        for row in advancers:
            f.write(f'{log_time}; {row[0]}; {row[1]}; {row[2]}; {row[3]}; {row[4]}\n')
    
    logger.debug('Saving Decliners data.')
    decliners = get_decliners(soup=soup)
    with open('data/decliners.csv', 'a') as f:
        for row in decliners:
            f.write(f'{log_time}; {row[0]}; {row[1]}; {row[2]}; {row[3]}; {row[4]}\n')

    logger.debug('Saving Index Snapshot data.')
    snapshot = get_snapshot(soup=soup)
    with open('data/snapshots.csv', 'a') as f:
        for row in snapshot:
            f.write(f'{log_time}; {row[0]}; {row[1]}\n')
    
    logger.debug('Saving Trades data.')
    trades = get_trades(soup=soup)
    with open('data/trades.csv', 'a') as f:
        for row in trades:
            f.write(f'{log_time}; {row[0]}; {row[1]}; {row[2]}\n')
    
    logger.info('Finished saving data.')
    logger.debug('Closing web driver.')
    driver.quit()

if  __name__ == "__main__":
    run()
