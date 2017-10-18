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
        self.transaction_amount = int(float(tamount[:-4]))
        self.transaction_remain = int(float(tremain[:-4]))
        self.state = state
        self.transaction_code = tcode
        p = Point(tdate, ttime, self.transaction_remain)
        list_of_points.append(p)
        a = None

        if aid not in [i.account_id for i in list_of_accounts]:
            a = Account(aid)
            list_of_accounts.append(a)
        else:
            for ac in list_of_accounts:
                if ac.account_id == aid:
                    a = ac
                    break

        a.points.append(p)

        if cid not in [i.customer_id for i in list_of_customers]:
            c = Customer(cid)
            c.accounts.append(a)
            list_of_customers.append(c)
        else:
            for c in list_of_customers:
                if c.customer_id == cid:
                    if aid not in [j.account_id for j in c.accounts]:
                        c.accounts.append(a)
                    break


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


filename = 'month_1.csv'
account_working_on = 'zhanghu_51356'
list_of_transactions = []
list_of_accounts = []
list_of_customers = []
list_of_points = []

s = StringIO()
pp = 0
with open(filename) as f:
    for line in f:
        if pp == 0:
            s.write(line)
        pp += 1
        if account_working_on in line:
            s.write(line)
s.seek(0)
df = pd.read_csv(s,
                 index_col=[0])
# df = pd.read_csv(filename,
#                  nrows=100,
#                  index_col=[0])


# df = pd.read_csv(filename, usecols=[0, 2, 3], nrows=100,
#                  index_col=[1],
#                  date_parser=lambda x: pd.to_datetime(x, format='(%Y, %m, %d)'),
#                  parse_dates=['transactionDate'])
# df.set_index('transactionDate', inplace=True)
# print(df.index[2])
# print(df.loc[1]['customerId'])
# df.replace()
# df.to_csv('month11.csv')

for index, row in df.iterrows():
    # print(index, row)
    t = Transaction(index,
                    row['accountId'],
                    row['transactionDate'],
                    row['transactionTime'],
                    row['terminalId'],
                    row['transactionAmount'],
                    row['transactionRemain'],
                    row['state'],
                    row['transactionCode'])
    list_of_transactions.append(t)

x_data = []
y_data = []

for i in list_of_accounts:
    if i.account_id == account_working_on:
        for p in i.points:
            x_data.append(p.transaction_datetime)
            y_data.append(p.remain)

plt.xlabel('Date')
plt.plot_date(x_data,
              y_data,
              fmt='-')
plt.ylabel('Remain')
plt.legend()
plt.show()
