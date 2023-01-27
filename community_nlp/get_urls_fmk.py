#!/usr/bin/env python
# coding: utf-8

# In[2]:


import requests
from bs4 import BeautifulSoup
import datetime
import os
import pymysql
from tqdm import tqdm
import numpy as np
import time
from dotenv import load_dotenv


# In[3]:


IS_ROOT_DIR = 0
def env_set():
    global IS_ROOT_DIR
    if not IS_ROOT_DIR:
        load_dotenv(verbose=True)
        IS_ROOT_DIR = 1


# In[8]:


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
BASE_URL = 'https://www.fmkorea.com'


# In[12]:


def get_url_date(li):
#     url = BASE_URL + li.find('h3').find('a')['href']
    url = li.find('h3').find('a')['href']
    date = li.find('span', {'class': 'regdate'}).text.strip()
    date = date.replace('.', '-')
    return [url, date]


# In[13]:


def get_urls(i):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    params = {'mid': 'best', 'page': i}
    result = requests.get(BASE_URL + '/index.php', params = params, headers = headers)
    soup = BeautifulSoup(result.text, 'lxml')
    table = soup.find('div', {'class': 'fm_best_widget _bd_pc'})
    lists = table.find_all('li')
    return [get_url_date(li) for li in lists]


# In[14]:


def commit_sql(data):
    with  con.cursor() as cursor:
        cursor.executemany("insert into urls_fmk(url, date) values (%s, %s)", data )
        con.commit()


# https://www.fmkorea.com/index.php?mid=best&page=100<br>
# - CREATE TABLE community.urls_fmk (id INTEGER PRIMARY KEY AUTO_INCREMENT, url TEXT, date TEXT);

# In[26]:


# 220601 ~ 221231
if __name__ == '__main__':
    start = 7273
    end = 761

    for i in tqdm(range(start, end, -1)):
        data = get_urls(i)
        commit_sql(data)
        time.sleep((np.random.random()+1)*5)

