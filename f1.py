import pandas as pd
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
from io import StringIO
from scipy.constants.constants import minute


class Transaction:
    def __init__(self, cid, aid,
                 tdate, ttime,
                 terminal, tamount,
                 tremain, state, tcode):
        self.customer_id = cid
        self.account_id = aid
        self.transaction_date = tdate
        self.transaction_time = ttime
        self.terminal_id = terminal
        self.transaction_amount = (float(tamount[:-4]))
        self.transaction_remain = (float(tremain[:-4]))
        self.state = state
        self.transaction_code = tcode
        p = Point(tdate, ttime, self.transaction_remain)
        list_of_points[p.transaction_datetime.ctime()] = p
        a = None

        if aid not in list_of_accounts:
            a = Account(aid)
            list_of_accounts[aid] = a
        else:
            a = list_of_accounts[aid]

        a.points.append(p)

        if cid not in list_of_customers:
            c = Customer(cid)
            c.accounts.append(a)
            list_of_customers[cid] = c
        else:
            c = list_of_customers[cid]
            c.accounts.append(a)

    def __hash__(self):
        return hash(self.customer_id + self.account_id)


class Account:
    def __init__(self, aid):
        self.account_id = aid
        self.points = []
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
        self.accounts = []

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


filename = 'month_1.csv'
list_of_accounts = dict()
list_of_account_ids = dict()
list_of_customers = dict()
list_of_points = dict()

df = pd.read_csv(filename,
                 index_col=[0])

pp = 0
for index, row in df.iterrows():
    # print(index, row)
    pp += 1
    if pp % 1000 == 0:
        print(pp)
    t = Transaction(index,
                    row['accountId'],
                    row['transactionDate'],
                    row['transactionTime'],
                    row['terminalId'],
                    row['transactionAmount'],
                    row['transactionRemain'],
                    row['state'],
                    row['transactionCode'])


# x_data = []
# y_data = []
#
# for i in list_of_accounts:
#     if i.account_id == account_working_on:
#         i.points.sort(key=lambda x: x.transaction_datetime)
#         for p in i.points:
#             x_data.append(p.transaction_datetime)
#             y_data.append(p.remain)
#
# plt.xlabel('Date')
# plt.plot_date(x_data,
#               y_data,
#               fmt='-')
# plt.ylabel('Remain')
# plt.legend()
# plt.show()
