# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 11:00:49 2020

@author: jjanko
"""

from sklearn import linear_model
import pandas as pd
import numpy as np
import scipy


def cost_function(weights, X, y):
    return np.sum((y - np.sum(weights * X, axis = 1).reshape(-1,1))**2) + np.sum(np.abs(weights)) * alpha

df = pd.read_excel(r'data.xlsx')[['GRE','GPA']]
df['intercept'] = 1.0
X = df[['intercept', 'GPA']].values
y = df['GRE'].values.reshape(-1,1)
#alpha is equivalent to the lambda parameter for penalizing large coefficients. if lambda is zero then problem is equivalent to ols
alpha = .1
clf = linear_model.Lasso(alpha=0.1, fit_intercept = False)
clf.fit(X,y)
print('Scikit-Learn Params')
print(clf.coef_)


weights = np.array([690.0, .001])

lasso_params = scipy.optimize.minimize(fun=cost_function, x0 = weights, args = (X,y))
#lasso_params = scipy.optimize.minimize(fun=cost_function, x0 = weights, args = (X,y), bounds = [(0,1e8),(0,1e8)])
print('lasso parameters')
print(lasso_params.x)

print('difference between my method and sci-kit learn')
print(lasso_params.x - clf.coef_)