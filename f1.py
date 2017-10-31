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

    if aid not in list_of_accounts:
        list_of_accounts[aid] = Account(aid)

    list_of_accounts[aid].points[p.transaction_datetime] = p
    c = Customer(cid)
    if cid not in list_of_customers:
        list_of_customers[cid] = c
    else:
        c = list_of_customers[cid]
    if aid not in c.accounts:
        c.accounts[aid] = list_of_accounts[aid]


class Account:
    def __init__(self, aid):
        self.account_id = aid
        self.points = dict()
        self.allpoints = dict()
        self.nodes = []
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
        self.balance_avg = 0
        self.balance_std = 0

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
        return (self.transaction_datetime - dt.datetime.utcfromtimestamp(1284286794)).total_seconds()

    def __hash__(self):
        return hash(self.transaction_datetime.ctime())


class Node:
    def __init__(self, aid, num):
        self.account_id = aid
        self.mnum = num
        # self.points = dict()
        # self.balance_std = std_func(aid, self.balance_avg)
        if num == 6:
            bavg = []
            bstd = []
            for nn in list_of_accounts[aid].nodes:
                bavg.append(nn.balance_avg)
                bstd.append(nn.balance_std)

            self.balance_avg = sum(bavg) / float(len(bavg))
            self.balance_std = sum(bstd) / float(len(bstd))

        else:
            if len(list_of_accounts[aid].points) == 0:
                self.balance_avg = list_of_accounts[aid].nodes[0].balance_avg
                self.balance_std = list_of_accounts[aid].nodes[0].balance_std
            else:
                self.balance_avg = integral_func(aid)
                self.balance_std = std_func(aid, self.balance_avg)


def show_plot(account_id):
    x_data = []
    y_data = []

    if account_id not in list_of_accounts:
        print('Account ID invalid')
        return

    list_of_points = sorted(list_of_accounts[account_id].allpoints.values(), key=lambda x: x.transaction_datetime)

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


def integral_func(aid):
    x, y, min_x, max_x = extract_points_from_aid(aid)
    if len(x) == 1 or len(y) == 1:
        return y
    f = InterpolatedUnivariateSpline(x, y, k=1)
    return f.integral(min_x, max_x) / (max_x - min_x)


def std_func(aid, balance):
    x, y, min_x, max_x = extract_points_from_aid(aid)
    if len(x) == 1 or len(y) == 1:
        return 0
    y2 = []
    for yy in y:
        y2.append((yy - balance) ** 2)

    f = InterpolatedUnivariateSpline(x, y2, k=1)
    return f.integral(min_x, max_x) / (max_x - min_x)


def std_func_discrete(aid):
    x, y, min_x, max_x = extract_points_from_aid(aid)
    return np.std(y)


def read_month(month_number):
    filename = 'month_' + str(month_number) + '.csv'
    df = pd.read_csv(filename,
                     #nrows=10000,
                     index_col=[0])
    for index, row in df.iterrows():
        transaction(index,
                    row['accountId'],
                    row['transactionDate'],
                    row['transactionTime'],
                    row['terminalId'],
                    row['transactionAmount'],
                    row['transactionRemain'],
                    row['state'],
                    row['transactionCode'])

    for aa in list_of_accounts.values():
        nnode = Node(aa.account_id, month_number)
        aa.nodes.append(nnode)
        aa.allpoints.update(aa.points)
        aa.points = dict()


def write_to_csv():
    raw_data = {'customerId':[], 'balanceAvg':[], 'balanceStd':[]}
    for cc in list_of_customers.values():
        bavg, bstd = [], []
        for aa in cc.accounts.values():
            bavg.append(aa.nodes[len(aa.nodes) - 1].balance_avg)
            bstd.append(aa.nodes[len(aa.nodes) - 1].balance_std)
        cc.balance_avg = sum(bavg)
        cc.balance_std = sum(bstd) / float(len(bstd))
        if isinstance(cc.balance_avg, np.ndarray):
            cc.balance_avg = cc.balance_avg[0]
        raw_data['customerId'].append(cc.customer_id)
        raw_data['balanceAvg'].append(cc.balance_avg)
        raw_data['balanceStd'].append(cc.balance_std)

    dff = pd.DataFrame(raw_data,
                       columns=['customerId', 'balanceAvg', 'balanceStd'])
    dff.to_csv('Output2.csv', index=False)


now = int(round(time.time()))
list_of_accounts = dict()
list_of_customers = dict()

for i in range(1, 6):
    print(i)
    read_month(i)
    print("read_month : " + str(int(round(time.time())) - now))

for aa in list_of_accounts.values():
    aa.nodes.append(Node(aa.account_id, 6))

write_to_csv()

sample_accounts = ['zhanghu_51320',
                   # 'zhanghu_51318',
                   # 'zhanghu_51319'
                   ]

for a in sample_accounts:
    show_plot(a)

print("END time: " + str(int(round(time.time())) - now))
