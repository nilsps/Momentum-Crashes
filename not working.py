

import wrds
import pandas as pd
import numpy as np
from pandas.tseries.offsets import *
from scipy import stats
import datetime as dt

import matplotlib.pyplot as plt



df = pd.read_csv("tot_df_db.csv")

# # Change variable format to int
# df[['adjusted','exchcd']]=\
#     df[['shrcd','exchcd']].astype(int)

# fill in missing return with 0
df['adjusted'] = df['adjusted'].fillna(0)

# create log return for future usage
df['logret'] = np.log(1+df['adjusted'])


J = 6 # Formation Period Length: J can be between 3 to 12 months

_tmp_df = df[['stock_id','date','adjusted','logret']].sort_values(['stock_id','date']).set_index('date')
tmp_df.tail()

umd = _tmp_df.groupby(['stock_id'])['logret'].rolling(J, min_periods=J).sum().reset_index()
umd = umd.rename(columns={'logret':'sumlogret'})

# Then exp the sum log return to get compound return (not necessary) 
umd['cumret']=np.exp(umd['sumlogret'])-1

umd.tail()

########################################
# Formation of 10 Momentum Portfolios  #
########################################

# For each date: assign ranking 1-10 based on cumret
# 1=lowest 10=highest cumret
umd=umd.dropna(axis=0, subset=['cumret'])
umd['momr']=umd.groupby('date')['cumret'].transform(lambda x: pd.qcut(x, 10, labels=False))

# shift momr from 0-9 to 1-10
umd.momr=1+umd.momr.astype(int)

umd.tail()

umd.groupby('momr')['cumret'].mean()



# First lineup date to month end date medate
# Then calculate hdate1 and hdate2 using medate

K = 6 # Holding Period Length: K can be between 3 to 12 months

umd['form_date'] = umd['date']
umd['medate'] = umd['date']+MonthEnd(0)
umd['hdate1']=umd['medate']+MonthBegin(1)
umd['hdate2']=umd['medate']+MonthEnd(K)
umd = umd[['stock_id', 'form_date','momr','hdate1','hdate2']]

umd.tail()

# join rank and return data together
# note: this step mimicks the following proc sql statement from SAS code and takes a while to run
'''
proc sql;
    create table umd2
    as select distinct a.momr, a.form_date, a.permno, b.date, b.ret
    from umd as a, crsp_m as b
    where a.permno=b.permno
    and a.HDATE1<=b.date<=a.HDATE2;
quit;
'''

 DATABASE SHENANIGENS!!!!

port = pd.merge(crsp_m[['permno','date','ret']], umd, on=['permno'], how='inner')
port = port[(port['hdate1']<=port['date']) & (port['date']<=port['hdate2'])]

# Rearrange the columns;
port = port[['permno','form_date', 'momr', 'hdate1','hdate2', 'date', 'ret']]


