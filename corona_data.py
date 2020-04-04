# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 22:15:29 2020

@author: prata
"""

#!/usr/bin/env python
# coding: utf-8

# # importing libraries
import datetime
import json
import requests
import argparse
import logging
from bs4 import BeautifulSoup
from tabulate import tabulate
import warnings 
warnings.filterwarnings('ignore')
#from teleegramBot import telegram_bot_sendtext

import pandas as pd
# In[2]:


FORMAT = '[%(asctime)-15s] %(message)s'
logging.basicConfig(format=FORMAT, level=logging.DEBUG, filename='bot.log', filemode='a')


# In[3]:


URL='https://www.mohfw.gov.in/'
# shortHeader=['S.No','ST','IN','FR','CR','DT']
shortHeader=['S.No','State','Conf','Cured','Dead']
FILE_NAME='corona_india.json'
extract_contents=lambda row:[x.text.replace('\n','') for x in row]


# In[4]:
def save(x):
    with open(FILE_NAME,'w') as f:
        json.dump(x,f)


# In[5]:
def load():
    res={}
    with open(FILE_NAME,'r',encoding='utf-8', errors='ignore') as f:
        res=json.load(f,strict=False)
    return res


# In[16]:
def get_data_for_state(state):    
    try:
#        interested_state=['haryana','kerala']
        interested_state=[]

        if isinstance(state, str):
            # print('string')
            interested_state = [state]
        else:
            # print('list')
            interested_state = state
    
        current_time=datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
        info = [] 
        states=[]
        
        ### getting data from official site
        response=requests.get(URL).content # Read content from url
        soup=BeautifulSoup(response,'html.parser')
        header=extract_contents(soup.tr.find_all('th'))
    
        #gerting all the table rows from website
        all_rows=soup.find_all('tr')
        # print(interested_state, len(interested_state))
        # print(len(all_rows))
        last_index = len(all_rows)
        for row in all_rows:
            stat= extract_contents(row.find_all('td'))
            # print('stat len :', len(stat), stat)
            if stat:
                if len(stat) < 3:
                    # print('con')
                    continue
                      
                if len(stat)==4:
                    #last row
                    stat=['',*stat]
                    stat[1]='Total'
                    stat[0]=int(last_index) + 1
                    states.append(stat)
                    # print(len(states))
                elif any([ s.lower()  in  stat[1].lower() for s in interested_state]):
                    states.append(stat)
                    # print(len(states))
                    last_index = stat[0]
    
        # for state in states: {state[1]:{currenttime:[2:]}}#{statename:}
        cur_data ={x[1]:{current_time:x[2:]} for x in states} 
        # print(current_time)
        # print(cur_data)
        # print(len(states))
        # print(states) 
        
        past_data=load()
        
        #initilaising boolean to chechk wether data change or not 
        changed=False 
        
        for state in cur_data:
            if state not in past_data:
                #new state has emerged 
                info.append(f' NEW_STATE {state} got corona virus :{cur_data[state][current_time]}')
                past_data[state]={}
                changed=True
            else:
                past=past_data[state]['latest']
                cur=cur_data[state][current_time]
                if past!=cur:
                    changed=True
                    info.append(f'Change for {state}: {past}->{cur}')
    
        if changed:
            #override the latest one now                
            for state in cur_data:
                past_data[state]['latest']=cur_data[state][current_time]
                past_data[state][current_time]=cur_data[state][current_time]
            save(past_data)
            
            
        events_info=''               
        for event in info:
            logging.warning(event)
            telegram_bot_sendtext  ='\n-'+event.replace("'","")
        
        divideby = 1
        # shortHeader = ['ST', 'IN', 'FR', 'CR', 'DT']
        # print('headers : ', shortHeader)
        df = pd.DataFrame(states, columns=shortHeader) 
        df.set_index('S.No', inplace = True) 
        
        # print("len :", len(df))
        if int(len(df)) > int(10):
            divideby = 2
        
        events_info= '' #'\n IN -> Indian\n FR -> Foreigner\n CR -> Cured\n DT -> Deaths'
        report = []      
        length = len(df)//divideby 
        df1 = df.iloc[:length].copy()
        # print("divideby : ", divideby)
        # print(df1)

#        table = tabulate(states, headers=shortHeader, tablefmt='orgtbl')
        table = tabulate(df1, headers=shortHeader, tablefmt='orgtbl')
        slack_text = f'Please find CoronaVirus Summary for India below:{events_info}\n```{table}```'
        print(slack_text)        
        report.append(slack_text)
        
        # print("length : ", length)
        if int(divideby) > int(1):
            df2 = df.iloc[int(length):].copy()
            # print(df2)

            table1 = tabulate(df2, headers=shortHeader, tablefmt='orgtbl')
            slack_text1 = f'Please find CoronaVirus Summary for India below:{events_info}\n```{table1}```'
            print(slack_text1)
            report.append(slack_text1)
#        telegram_bot_sendtext(slack_text)
        return report
                
    except Exception as e:
        logging.exception('script failed',e)

states = ['Andhra Pradesh', 'Bihar', 'Chhattisgarh', 'Delhi', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Odisha', 'Puducherry', 'Punjab', 'Rajasthan', 'Tamil Nadu', 'Telengana', 'Chandigarh', 'Jammu and Kashmir', 'Ladakh', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal']                    
(get_data_for_state(states))