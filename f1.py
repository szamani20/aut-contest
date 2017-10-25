import pandas as pd
import datetime as dt
import time
import numpy as np
import matplotlib.pyplot as plt
from sklearn import linear_model
from io import StringIO
from scipy.constants.constants import minute
from scipy.interpolate import InterpolatedUnivariateSpline


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
        # self.transaction_date = t.date()
        # self.transaction_time = t.time()
        self.transaction_datetime = t
        self.remain = remain

    def seconds_from_begin(self):
        return (self.transaction_datetime - dt.datetime.utcfromtimestamp(0)).total_seconds()

    def __hash__(self):
        return hash(self.transaction_datetime.ctime())


class Node:
    def __init__(self, aid, num):
        self.account_id = aid
        self.mnum = num
        self.points = dict()
        self.balance_avg = 1


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

    plt.xlabel('Date')
    plt.plot_date(x_data,
                  y_data,
                  fmt='-')
    plt.ylabel('Remain')
    plt.legend()
    plt.show()


def extract_points_from_aid(aid):
    x = []
    y = []
    min_x = int(1e20)
    max_x = -min_x

    # because unordered
    for point in sorted(list_of_accounts[aid].points.values(), key=lambda p: p.transaction_datetime):
        x_val = point.seconds_from_begin()
        y_val = point.remain
        max_x = max(x_val, max_x)
        min_x = min(x_val, min_x)
        x.append(x_val)
        y.append(y_val)

    return np.array(x), np.array(y), min_x, max_x


def std_func(aid, balance):
    x, y, min_x, max_x = extract_points_from_aid(aid)
    y2 = []
    for yy in y:
        y2.append((yy-balance) ** 2)

    f = InterpolatedUnivariateSpline(x, y2, k=1)
    return f.integral(min_x, max_x) / (max_x - min_x)


def integral_func(aid):
    x, y, min_x, max_x = extract_points_from_aid(aid)
    f = InterpolatedUnivariateSpline(x, y, k=1)
    return f.integral(min_x, max_x) / (max_x - min_x)


now = int(round(time.time()))
filename = 'month_1.csv'
list_of_accounts = dict()
list_of_customers = dict()

df = pd.read_csv(filename,
                 index_col=[0])
pp = 0
print(int(round(time.time())) - now)
for index, row in df.iterrows():
    pp += 1
    # if pp % 1000 == 0:
    #    print("pp: " + str(pp / 1000) + " time: " + str(int(round(time.time())) - now))
    transaction(index,
                row['accountId'],
                row['transactionDate'],
                row['transactionTime'],
                row['terminalId'],
                row['transactionAmount'],
                row['transactionRemain'],
                row['state'],
                row['transactionCode'])

print("pp: " + str(pp / 1000) + " time: " + str(int(round(time.time())) - now))

print(integral_func('zhanghu_51317'))
print(std_func(('zhanghu_51317')))
show_plot('zhanghu_51317')

print(integral_func('zhanghu_51318'))
print(std_func(('zhanghu_51318')))
show_plot('zhanghu_51318')

print(integral_func('zhanghu_51319'))
print(std_func(('zhanghu_51319')))
show_plot('zhanghu_51319')

# for x in range(0, 3595):
#    if len(list_of_customers['guke_' + str(x)].accounts) > 1:
#        print('guke_' + str(x) + str(len(list_of_customers['guke_' + str(x)].accounts)))

print("END time: " + str(int(round(time.time())) - now))