import pandas as pd
import datetime as dt
import time
import numpy as np
import matplotlib.pyplot as plt
from io import StringIO
from scipy.constants.constants import minute


def transaction(cid, aid,
                tdate, ttime,
                terminal, tamount,
                tremain, state, tcode):
    # i_transaction_amount = float(tamount[:-4])
    i_transaction_remain = float(tremain[:-4])
    p = Point(tdate, ttime, i_transaction_remain)
    a = Account(aid)
    if aid not in list_of_accounts:
        list_of_accounts[aid] = a
    else:
        a = list_of_accounts[aid]
    a.points[p.transaction_datetime] = p
    c = Customer(cid)
    if cid not in list_of_customers:
        list_of_customers[cid] = c
    else:
        c = list_of_customers[cid]
    if aid not in c.accounts:
        c.accounts[aid] = a


class Account:
    def __init__(self, aid):
        self.account_id = aid
        self.points = dict()
        # self.customers = []

    def __eq__(self, other):
        if other is None:
            return False
        if other.account_id == self.account_id:
            return True
        return False

    def __hash__(self):
        return hash(self.account_id)


class Customer:
    def __init__(self, cid):
        self.customer_id = cid
        self.accounts = dict()

    def __eq__(self, other):
        if other is None:
            return False
        if other.customer_id == self.customer_id:
            return True
        return False

    def __hash__(self):
        return hash(self.customer_id)


class Point:
    def __init__(self, tdate, ttime, remain):
        t = dt.datetime.strptime(tdate, '(%Y, %m, %d)')
        try:
            t = t.replace(second=int(ttime) % 100,
                          minute=int((int(ttime) / 100) % 100),
                          hour=int((int(ttime) / 10000) % 100))
        except Exception as e:
            if not str(ttime).startswith('24'):
                print(ttime)
            t.replace(second=0,
                      minute=0,
                      hour=0)
        self.transaction_date = t.date()
        self.transaction_datetime = t
        self.transaction_time = t.time()
        self.remain = remain

    def __hash__(self):
        return hash(self.transaction_datetime.ctime())


def show_plot(account_id):
    x_data = []
    y_data = []

    if account_id not in list_of_accounts:
        print('Account ID invalid')
        return

    a = list_of_accounts[account_id]
    list_of_points = sorted(a.points.values(), key=lambda x: x.transaction_datetime)

    for p in list_of_points:
        x_data.append(p.transaction_datetime)
        y_data.append(p.remain)
        print(p.transaction_datetime, p.remain)

    plt.xlabel('Date')
    plt.plot_date(x_data,
                  y_data,
                  fmt='-')
    plt.ylabel('Remain')
    plt.legend()
    plt.show()


now = int(round(time.time()))
filename = 'month_1.csv'
list_of_accounts = dict()
list_of_customers = dict()

df = pd.read_csv(filename,
                 index_col=[0])
pp = 0
print(int(round(time.time())) - now)
for index, row in df.iterrows():
    # print(index, row)
    pp += 1
    if pp % 1000 == 0:
        print("pp: " + str(pp / 1000) + " time: " + str(int(round(time.time())) - now))
    transaction(index,
                row['accountId'],
                row['transactionDate'],
                row['transactionTime'],
                row['terminalId'],
                row['transactionAmount'],
                row['transactionRemain'],
                row['state'],
                row['transactionCode'])
