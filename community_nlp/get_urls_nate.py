#!/usr/bin/env python
# coding: utf-8

# In[18]:


import requests
from bs4 import BeautifulSoup
import datetime
import os
import pymysql
from tqdm import tqdm
from dotenv import load_dotenv


# In[2]:


IS_ROOT_DIR = 0
def env_set():
    global IS_ROOT_DIR
    if not IS_ROOT_DIR:
        load_dotenv(verbose=True)
        IS_ROOT_DIR = 1


# In[3]:


def sql_setting():
    SQL_IP = os.environ['IP_ADDRESS']
    SQL_PASSWORD = os.environ['MYSQL_PASSWORD']

    con = pymysql.connect(
        user='nlp', 
        passwd=SQL_PASSWORD,
        host=SQL_IP, 
        db='community', 
        charset='utf8'
    )
    return con


# In[4]:


env_set()
con = sql_setting()
BASE_URL = 'https://pann.nate.com'


# In[6]:


def continuos_dates(start, end, fm):
    dates = []
    dt = datetime.datetime.strptime(start, fm)
    while True:
        dt_string = dt.strftime(format=fm)
        dates.append(dt_string)
        if dt_string == end:
            break
        dt = dt + datetime.timedelta(days=1)
    return dates


# In[21]:


def get_urls(date):
    urls = []
    for page in range(1, 3):
        params = {'stdt': date, 'page': page}
        result = requests.get(BASE_URL + '/talk/ranking/d', params = params)
        soup = BeautifulSoup(result.text, 'lxml')
        lists = soup.find('ul', {'class':'post_wrap'}).find_all('li')
        urls.extend([[li.find('dt').find('a')['href'], date] for li in lists])
    return urls


# In[22]:


def commit_sql(data):
    with  con.cursor() as cursor:
        cursor.executemany("insert into urls_nate(url, date) values (%s, %s)", data )
        con.commit()


# CREATE TABLE community.urls_nate (id INTEGER PRIMARY KEY AUTO_INCREMENT, url TEXT, date TEXT);

# In[23]:


if __name__ == '__main__':
    start = '20220101'
    end = '20221231'
    dates = continuos_dates(start, end, '%Y%m%d')

    for date in tqdm(dates):
        urls = get_urls(date)
        commit_sql(urls)

