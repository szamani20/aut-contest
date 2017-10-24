from scipy.interpolate import InterpolatedUnivariateSpline
import numpy as np


def integrate_func(aid):
    x = np.array()


# x = np.array([0, 8, 9, 10, 11, 12, 16])
# y = np.array([6, 6, 0, 0, 0, 0, 0])

x = np.array([2, 3])
y = np.array([6, 6])

f = InterpolatedUnivariateSpline(x, y, k=1)
print(f.integral(2, 3))


# from datetime import datetime as dt
#
# now = dt.now()
# print((now -dt.utcfromtimestamp(0)).total_seconds())
