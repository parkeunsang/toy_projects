#!/usr/bin/env python
# coding: utf-8

# In[ ]:


'''
Get KBO Data

From 스탯티즈
http://www.statiz.co.kr/boxscore.php?opt=4&date=2020-09-20&stadium=%EC%9E%A0%EC%8B%A4&hour=14<br>
위 사이트의 데이터 table 수집
'''
import requests as rq
import pandas as pd
from bs4 import BeautifulSoup as bs
from urllib import parse
from tqdm import tqdm
import re

def makeDf(table, title):
    '''
    html table을 data frame 형태로 
    '''
    tbSources = []
    tbSources.append([x.text for x in table.findAll("tr")[0].findAll("th")])

    for i in table.findAll("tr")[1:]:
        tbSources.append([x.text for x in i.findAll("td")])

    df = pd.DataFrame(tbSources)

    df.columns = df.iloc[0,:]

    df = df[1:].reset_index(drop=True)
    
    df['title'] = title
    return df

def tatu(tables, i):
    '''
    타수, 투수데이터가 있으므로 두개다 수집
    i=0,2 / 타수, 투구
    '''
    title1 = tables[i+2].find("h3",{"class":"box-title"}).text
    title1 = title1[title1.index("(")+1:-1]

    
    title2 = tables[i+3].find("h3",{"class":"box-title"}).text
    title2 = title2[title2.index("(")+1:-1]
    df = makeDf(tables[i+2].find("div",{"class":"box-body no-padding table-responsive"}),title1).append(
        makeDf(tables[i+3].find("div",{"class":"box-body no-padding table-responsive"}), title2))
    return df


def getUrlByMonth(year,month):
    '''
    year년 month월의 경기데이터 일정을 모두 수집해 url 반환
    '''
    urlOrigin = f"http://www.statiz.co.kr/schedule.php?opt={month}&sy={year}"

    soup = bs(rq.get(urlOrigin).text,'lxml')

    temp = soup.findAll("div",{"class":"box"})[2]

    urls = []

    for i in temp.findAll("a"):
        if(("date" in i['href'])&("stadium" in i['href'])):
            urls.append(i['href'])

    baseUrl = "http://www.statiz.co.kr/"

    urls = list(set(urls))

    urls = [baseUrl + x + "&opt=4" for x in urls]
    return urls

def detailName(name,dic):
    if(name not in dic.keys()):
        return 0
    else:
        char = dic[name]
        if(char=='\n'):
            return 0
        return char.count(',')+1

def getDic(sr,r,tb):

    dic1 = {}
    tn1 = teamN[team1]
    tn2 = teamN[team2]
    dic1['G_ID'] = r['날짜'].replace('-','') + tn1+tn2 + '0'
    dic1['GDAY_DS'] = r['날짜'].replace('-','')
    if(tb=="T"):
        dic1['T_ID'] = tn1
        dic1['VS_T_ID'] = tn2
    else:
        dic1['T_ID'] = tn2
        dic1['VS_T_ID'] = tn1
        
    dic1['HEADER_NO'] = 0
    dic1['TB_SC'] = tb #초

    dic1['PA'] = sr['TPA']
    dic1['AB'] = sr['AB']
    dic1['RBI'] = sr['RBI']
    dic1['RUN'] = sr['R']
    dic1['HIT'] = sr['H']
    dic1['H2'] = detailName('2루타',r)
    dic1['H3'] = detailName('3루타',r)
    dic1['HR'] = sr['HR']
    dic1['SB'] = detailName('도루',r)
    dic1['CS'] = detailName("도실",r)
    dic1['SF'] = detailName("희플",r)
    dic1['BB'] = sr['BB']
    dic1['HP'] = sr['HBP']
    dic1['KK'] = sr['SO']
    dic1['GD'] = sr['GDP']
    dic1['LOB'] = sr['LOB']
    
    char = r['득점권 상황']
    if(len(re.findall(r'[0-9]+', char)) ==0):
        a=0;b=0;c=0;
    else:
        a=int(re.findall(r'[0-9]+', char)[1])
        b=int(re.findall(r'[0-9]+', char)[0])
        if(b!=0):
            c=a/b
        else:
            c=0
        
    
    dic1['P_HRA_RT'] =c
    dic1['P_AB_CN'] = b
    dic1['P_HIT_CN'] = a

    return dic1

teamN = {}
teamN['한화'] = 'HH'
teamN['KIA'] = 'HT'
teamN['KT'] = 'KT'
teamN['kt'] = 'KT'
teamN['LG'] = 'LG'
teamN['롯데'] = 'LT'
teamN['NC'] = 'NC'
teamN['두산'] = 'OB'
teamN['SK'] = 'SK'
teamN['삼성'] = 'SS'
teamN['키움'] = 'WO'
teamN['넥센'] = 'NE'

def main():
    for year in range(2015,2021):
        '''
        2015~2020 데이터 수집
        '''
        urls = []
        for mon in range(3,11): #3월~10월
            urls.extend(getUrlByMonth(year,mon))

        urls = sorted(urls)

        result = []
        print("Gathering "+str(year) +" data")
        for url in tqdm(urls):


            date = url[url.find("date=")+5:url.find("date")+15]
            source = rq.get(url)

            soup = bs(source.text,'lxml')
            tables = soup.findAll("div",{"class":"box"})
            ###팀명
            title1 = tables[2].find("h3",{"class":"box-title"}).text
            try:
                tn1 = title1[title1.index("(")+1:-1]
            except ValueError:
                print("우천")
                continue
            title2 = tables[2].find("h3",{"class":"box-title"}).text
            tn2 = title1[title1.index("(")+1:-1]


            team1 = {}
            try:
                temp = soup.findAll("td",{"bgcolor":"white"})[0]
            except IndexError:
                print("우천")
                continue

            for idx,x in enumerate(temp.findAll("b")):
                team1[x.text] = temp.contents[2::3][idx]

            team1['팀명'] = tn1

            team2 = {}
            temp = soup.findAll("td",{"bgcolor":"white"})[1]
            for idx,x in enumerate(temp.findAll("b")):
                team2[x.text] = temp.contents[2::3][idx]

            team2['팀명'] = tn1

            gujang = parse.unquote([x for x in url.split("&") if 'stadium' in x][0][8:])
            sil1=tables[6].find("table",{"width":"100%"}).contents[1].text
            sil2=tables[7].find("table",{"width":"100%"}).contents[1].text

            team1['날짜'] =  date
            team1['구장'] = gujang
            team1['실책'] = sil1

            team2['날짜'] =  date
            team2['구장'] = gujang
            team2['실책'] = sil2
            result.append([tatu(tables,0),tatu(tables,2),team1,team2])


        
        fin = []
        for idx,r in enumerate(result):

            team1 = r[0]['title'].iloc[0]
            team2 = r[0]['title'].iloc[-1]
            if(team1==''):
                print("error1")
                continue
            df = r[0][r[0].iloc[:,0] !='팀 합계']

            df1 = df[df['title'] == team1].iloc[:,3:-6]
            df2 = df[df['title'] == team2].iloc[:,3:-6]

            try:
                df1 = df1.astype(float)
                df2 = df2.astype(float)
            except ValueError:
                print("error2")
                continue

            sr1 = df1.sum()
            sr2 = df2.sum()
            if((team1 in teamN.keys())&(team2 in teamN.keys())):
                fin.append(getDic(sr1,r[2],'T'))
                fin.append(getDic(sr2,r[3],'B'))
        
        df = pd.DataFrame(fin)
        df.drop_duplicates().to_csv(f"baseball_{year}.csv",index=False) #export

    #새로운 변수 생성 및 기본적인 전처리
    fileNames=['baseball_' + str(x) + '.csv' for x in list(range(2015,2021))]

	for fileName in tqdm(fileNames):
	    temp = pd.read_csv(fileName)
	    temp['win'] = 0.5

	    gameIds = temp['G_ID'].unique()
	    for gi in gameIds:

	        fidx = temp[temp['G_ID'] == gi].index[0]
	        sidx = temp[temp['G_ID'] == gi].index[1]


	        if(temp.loc[fidx,'RUN'] > temp.loc[sidx,'RUN']):
	            temp.loc[fidx,'win'] = 1
	            temp.loc[sidx,'win'] = 0
	        elif(temp.loc[fidx,'RUN'] < temp.loc[sidx,'RUN']):
	            temp.loc[fidx,'win'] = 0
	            temp.loc[sidx,'win'] = 1
	    y = temp['win']
	    temp = temp.iloc[:,:-1]

	    temp['OBP'] = (temp['HIT']+temp['BB']+temp['HP'])/(temp['AB']+temp['BB']+temp['HP']+temp['SF'])

	    temp['OOO'] = temp['HIT']/temp['AB']

	    temp['win'] = y
	    temp = temp.sort_values(["G_ID","TB_SC"],ascending = [True,False])
	    temp = temp[temp.loc[:,'PA':'P_HIT_CN'].sum(axis=1)!=0].reset_index(drop=True)
	    temp.to_csv(f"../{fileName}",index=False)

	    
if(__name__ == "__main__"):
    main()
    
# #투수관련데이터
# fin_=[]
# for r in result:

#     team1 = r[0]['title'].iloc[0]
#     team2 = r[0]['title'].iloc[-1]

#     t1 = r[1][r[1]['이름']=='팀 합계'].iloc[0]
#     t2 = r[1][r[1]['이름']=='팀 합계'].iloc[-1]



#     dic1 = {}
#     tn1 = teamN[team1]
#     tn2 = teamN[team2]
#     dic1['G_ID'] = r[2]['날짜'].replace('-','') + tn1+tn2 + '0'
#     dic1['GDAY_DS'] = r[2]['날짜'].replace('-','')
#     dic1['T_ID'] = tn1
#     dic1['VS_T_ID'] = tn2
#     dic1['TB_SC'] = 'T'
#     dic1['R'] = t1['R']
#     dic1['ER'] = t1['ER']
#     fin_.append(dic1)

#     dic1 = {}

#     dic1['G_ID'] = r[2]['날짜'].replace('-','') + tn1+tn2 + '0'
#     dic1['GDAY_DS'] = r[2]['날짜'].replace('-','')
#     dic1['T_ID'] = tn2
#     dic1['VS_T_ID'] = tn1
#     dic1['TB_SC'] = 'T'
#     dic1['R'] = t2['R']
#     dic1['ER'] = t2['ER']
#     fin_.append(dic1)



# df_ = pd.DataFrame(fin_)

# df_ = df_.drop_duplicates()

