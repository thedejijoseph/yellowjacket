from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--log-level=3')
driver = webdriver.Chrome('drivers/chromedriver81.exe', options=options)

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

def run():
    driver.get('http://www.nse.com.ng')
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    log_time = str(datetime.now())

    advancers = get_advancers(soup=soup)
    with open('data/advancers.csv', 'a') as f:
        for row in advancers:
            f.write(f'{log_time}; {row[0]}; {row[1]}; {row[2]}; {row[3]}; {row[4]}\n')
    
    decliners = get_decliners(soup=soup)
    with open('data/decliners.csv', 'a') as f:
        for row in decliners:
            f.write(f'{log_time}; {row[0]}; {row[1]}; {row[2]}; {row[3]}; {row[4]}\n')

    snapshot = get_snapshot(soup=soup)
    with open('data/snapshots.csv', 'a') as f:
        for row in snapshot:
            f.write(f'{log_time}; {row[0]}; {row[1]}\n')
    
    trades = get_trades(soup=soup)
    with open('data/trades.csv', 'a') as f:
        for row in trades:
            f.write(f'{log_time}; {row[0]}; {row[1]}; {row[2]}\n')

if  __name__ == "__main__":
    run()
    driver.close()
