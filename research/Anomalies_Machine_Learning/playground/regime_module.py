#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 30 12:34:11 2020

@author: janko
"""


#import libraries for analysis
#pandas for dataframes
import pandas as pd
#datetime for converting numerics to datetime format
import datetime as dt
#yahoo finance dividend adjusted closes for prototyping
import yfinance as yf
#statsmodels for ols regressions
import statsmodels.api as sm
#convert dataframes to numpy format because sklearn does not take dataframes well
import numpy as np
from finance_byu.fama_macbeth import fama_macbeth, fama_macbeth_parallel, fm_summary, fama_macbeth_numba
import scipy.stats
import sys

#this is the list of classifiers from sklearn that are available for analysis. "kitchen sink" approach
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, VotingClassifier


#this is a base class which we use put our parameters. All the other classes inherit from this
class BacktestParameters:
    
    def __init__(self, stk_symbols, start, end, lookback_alpha, lev):
        #the stock symbols
        self.stk_symbols = stk_symbols
        #start of the data series
        self.start = start
        #end of the data series
        self.end = end
        #index security
        #the lookback period for calculating alpha and idiosyncratic volatility
        self.lookback = lookback_alpha
        #leverage to apply to the strategy
        self.lev = lev

#class for pulling the yahoo finance data and cleaning so we have monthly data
class Data(BacktestParameters):
    
    def __init__(self, bp):
        #inherit from the base class
        self.stk_symbols = bp.stk_symbols
        self.start = bp.start
        self.end = bp.end
        self.lookback = bp.lookback
        
    #method for get getting the adjusted closes from yahoo
    def get_data(self):
        close = pd.DataFrame()

        for i in self.stk_symbols:

            df = yf.download(i, start=self.start, end=self.end, progress=False)
            df = pd.DataFrame(df['Adj Close'])
            df.columns = [i]
            if close.empty:
                close = df.copy()
            else:
                close = pd.concat([close, df], axis = 1)

        #get the daily returns
        returns = close.pct_change()[1:]

        print(returns.head())
        
        return returns
    
    #converts the daily returns to a geometric return for the month
    def convert_monthly(self, returns):
        returns = returns.resample('M').agg(lambda x: (x + 1).prod(skipna = True) - 1)
        
        #the geometric returns convert null values at the beginning of the time series to zeros.
        #this converts the data back to null values so we dont allocate to data that does not exist 
        for i in returns.columns:
            found = False
            for date, row in returns.loc[:,i].iteritems():
                if row == 0.0 and ~found:
                    returns.loc[date, i] = np.nan
                else:
                    found = True
        print(returns)
        return returns
    
    
    #this method takes a dataframe and converts to a binary output based off the center variable
    def get_binary(self, df_input, center = 0.0):
        
        binary_alpha = df_input.astype(float)
        #greater than the center var is a 1
        binary_alpha[binary_alpha >= center] = 1.0
        #less than the center var is a 0.0
        binary_alpha[binary_alpha < center] = 0.0
        
        return binary_alpha
    
    def get_probability(self, returns, factor_model, rf):
        #initialize the alpha dataframe
        df_probability = returns[self.lookback:].copy()
        binary_returns = self.get_binary(returns)
    
        count = 0
        #iterate through the monthly data. At each point in time we find the insample alpha and idiosyncratic vol
        for ix, row in binary_returns.iterrows(): 
            #check to make sure we have at least the lookback for analysis
            if count >= self.lookback:
                """
                note that python will not return the last part of the index. We want to by inclusive of this
                since this is an insample measure
                """
                analysis = binary_returns[count-self.lookback:count]
    
                for ticker in returns.columns:
                        #the dependent variable is our security and index var is the independent var
                    try:
                        y = analysis[ticker][1:]
                        y = pd.DataFrame(y, columns = [ticker])
                        # the index is your independent variable
                        x = factor_model.shift(1).loc[y.index,:]
                        #add a constant so we can get the alpha
                        clf = LogisticRegression(solver='lbfgs')
                        clf.fit(x, y.values.ravel())
                        #make a prediction on the input features 
                        predict = clf.predict_proba(x.loc[analysis[ticker].tail(1).index])
                        df_probability.loc[ix, ticker] = predict[0,1]
                    except:
                        #if we have missing data we populate our analysis dataframe with null values 
                        df_probability.loc[ix, ticker] = np.nan
            #iterate to the next point in our data
            count = count + 1
    
        #notice that I populated the alpha and idiosyncratic volatility with the full returns dataframe. 
        #these two lines remove the lookback period for clean reading
        df_probability = df_probability.dropna(axis = 0, how = 'all')

    
        return df_probability
    
    def get_alpha(self, returns, factor_model, rf):
        #initialize the alpha dataframe
        df_alpha = returns[self.lookback:].copy()
        #initialize the idiosyncratic volatility as well
        idiosyncratic_vol = returns[self.lookback:].copy()
    
        count = 0
        #iterate through the monthly data. At each point in time we find the insample alpha and idiosyncratic vol
        for ix, row in returns.iterrows(): 
            #check to make sure we have at least the lookback for analysis
            if count >= self.lookback:
                """
                note that python will not return the last part of the index. We want to by inclusive of this
                since this is an insample measure
                """
                analysis = returns[count-self.lookback:count]
    
                for ticker in returns.columns:
                        #the dependent variable is our security and index var is the independent var
                    try:
                        y = pd.concat([analysis[ticker], rf.loc[analysis.index]], axis = 1)
                        y = pd.DataFrame(y[ticker] - y[rf.columns[0]], columns = [ticker])
                        # the index is your independent variable
                        if ticker in factor_model.columns:
                            x = factor_model.loc[analysis.index,:].drop(ticker, axis = 1)
                        else:
                            x = factor_model.loc[analysis.index,:]
                        #add a constant so we can get the alpha
                        x = sm.add_constant(x)
                        #x = x.shift(1)
    
                        #use simple ols
                        mod = sm.OLS(y, x, missing='drop')
                        res = mod.fit()
                        #get the alpha
                        alpha = res.params['const']
                        #add the results to the alpha dataframe for analysis later
                        df_alpha.loc[ix, ticker] = alpha
                        #the line below is in case I want to analyze a simple difference 
                        #df_alpha.loc[ix, ticker] = (analysis[ticker] - analysis[index_security ]).mean()
                        #find the idiosyncratic volatility. Simply the residual squared. Note this is monthly
                        idiosyncratic_vol.loc[ix, ticker] = res.resid.std()
                    except:
                        #if we have missing data we populate our analysis dataframe with null values 
                        df_alpha.loc[ix, ticker] = np.nan
                        idiosyncratic_vol.loc[ix, ticker] = np.nan
            #iterate to the next point in our data
            count = count + 1
    
        #notice that I populated the alpha and idiosyncratic volatility with the full returns dataframe. 
        #these two lines remove the lookback period for clean reading
        df_alpha = df_alpha.dropna(axis = 0, how = 'all')
        df_alpha = df_alpha.shift(1)[1:]
        idiosyncratic_vol = idiosyncratic_vol.dropna(axis = 0, how = 'all')
        idiosyncratic_vol = idiosyncratic_vol.shift(1)[1:]
        binary_alpha = self.get_binary(df_alpha)
    
        print(df_alpha.head(5))
        print(idiosyncratic_vol.head(5))
        return df_alpha, idiosyncratic_vol, binary_alpha
    
    def get_rolling_features(self, returns, center):
        
        #the next few lines are a variety of feature to use
    
        #get the rolling means of returns as a momentum feature. Subtract the last month's return
        #12 month momentum factor
        rolling_mean_12 = ((returns.rolling(window = 12).mean() - returns.rolling(window = 1).mean()) )[12:]
        rolling_sum_12 = ((returns.rolling(window = 12).mean() - returns.rolling(window = 1).sum()) )[12:]
        #6 month momentum factor
        rolling_mean_6 = ((returns.rolling(window = 6).mean() - returns.rolling(window = 1).mean()) )[6:]
    
        rolling_std_12 = (returns.rolling(window = 12).std() )[12:]
    
        #convert the momentum factor a binary variable. The center is optimized to increase strategy sharpe
        #turns the momentum factor to a 1 if the mean average return over past 12 months is over 15%/12
        binary_mean_12 = self.get_binary(rolling_mean_12, center = center/12)
        binary_mean_6 = self.get_binary(rolling_mean_6, center = center/12)
        #convert the output feature to a binary variable for training the classifiers
        binary_returns = self.get_binary(returns, center = center/12)
        
        return rolling_mean_12, rolling_mean_6, rolling_std_12, binary_mean_12,binary_mean_6,binary_returns, rolling_sum_12
        
    def get_rolling_features_mt(self, returns, center):
        
        #the next few lines are a variety of feature to use
    
        #get the rolling means of returns as a momentum feature. Subtract the last month's return
        #12 month momentum factor
        rolling_mean_12 = ((returns.rolling(window = 12).mean() - returns.rolling(window = 1).mean()) )[12:]
        #6 month momentum factor
        rolling_mean_6 = ((returns.rolling(window = 6).mean() - returns.rolling(window = 1).mean()) )[6:]
    
        rolling_std_12 = (returns.rolling(window = 12).std() )[12:]
    
        #convert the momentum factor a binary variable. The center is optimized to increase strategy sharpe
        #turns the momentum factor to a 1 if the mean average return over past 12 months is over 15%/12
        binary_mean_12 = self.get_binary(rolling_mean_12, center = center/12)
        binary_mean_6 = self.get_binary(rolling_mean_6, center = center/12)
        #convert the output feature to a binary variable for training the classifiers
        binary_returns_pos = self.get_binary(returns, center = center/12)
        binary_returns_neg = self.get_binary(returns, center = -center/12)
        
        return rolling_mean_12, rolling_mean_6, rolling_std_12, binary_mean_12,binary_mean_6,binary_returns_pos, binary_returns_neg
        
    def get_features(self, feature_list):
        
        feature_set = {}
    
        for i in feature_list:
            i = i.shift(1).dropna(axis = 0, how = 'all')
            for j in i.columns:
                if j not in feature_set.keys():
                    i[j].rename('0', inplace = True)
                    feature_set[j] = pd.DataFrame(i[j].copy())
                else:
                    i[j].rename(str(len(feature_set[j].columns)), inplace = True)
                    feature_set[j] = pd.concat([feature_set[j], i[j].copy()], axis = 1).dropna(axis = 0, how = 'any')
                #remove rows where we do not have features for the whole portfolio.
                feature_set[j].dropna(axis = 0, how = 'any', inplace = True)
                
        return feature_set
        
#class for the backtesting of our classification
class Backtest():
    #instantiate with the backtest parameters with the returns data
    def __init__(self, bp, returns, mode):
        #the stock symbols
        self.stk_symbols = bp.stk_symbols
        #start of the data series
        self.start = bp.start
        #end of the data series
        self.end = bp.end
        #index security
        #the lookback period for calculating alpha
        self.lookback = bp.lookback
        self.returns = returns
        self.mode = mode
        
        
        
    def check_new_factor(self, backtest, factor_model, index_symbol):
        
        new_factor = pd.DataFrame(backtest.mean(axis = 1))
        new_factor.columns = ['portfolio']

        Y = factor_model.loc[new_factor.index, index_symbol]
        Y = pd.DataFrame(Y)
        X = factor_model.loc[new_factor.index,:]
        X = pd.concat([new_factor, X], axis = 1)
        X['intercept'] = 1.0
        X = X.shift(1).dropna(axis = 0)
        Y = Y.iloc[1:]
        model = sm.OLS(Y,X, missing = 'drop')
        results = model.fit()
        print(results.summary())  
        betas = results.params

        #2nd step. regress all asset returns for a fixed time period against the estimated betas to determine the risk premium for each factor.

        prems = {}
        for count, row in X.iterrows():
            y = Y.loc[count]
            y = pd.DataFrame(y).T
            x = pd.DataFrame(row).T
            model = sm.OLS(y,x, missing = 'drop')
            results = model.fit()
            prems[count] = results.params

        print("Factor Loadings")
        prems = pd.DataFrame(prems).T
        print(prems.head(20))
        expected_prems = prems.mean()
        t_stats = expected_prems / (prems.std()/ np.sqrt(len(prems.index)))
        print("expected premiums for each risk factor")
        print(expected_prems)
        print("t-stats for each risk factor")
        print(t_stats)
  
            
    """
    this method gets the equal weight portfolio of our strategy and compares to the factor model of choice. 
    Takes the backtest dataframe which is the actual returns of the strategy.
    """
    def treynor_mazuy(self, backtest, factor_model):
        
        port= pd.DataFrame(backtest.mean(axis = 1))
        port.columns = ['portfolio']

        #1st step. run the regression of factors on the portfolio
        Y = pd.DataFrame(port)
        X = pd.DataFrame(factor_model.loc[port.index,'Mkt-RF'])
        X.loc[:,'market_squared'] = X['Mkt-RF']**2
        X['intercept'] = 1.0        
        model = sm.OLS(Y,X,missing = 'drop')
        #robust covariance results
        results = model.fit(cov_type='HAC',cov_kwds={'maxlags':1})
        #results.params['intercept'] = round(results.params['intercept'] * 12.*100.0, 2)
        
        print(results.summary())
                    
        return results
    
    def henriksson_merton(self, backtest, factor_model):
        
        port= pd.DataFrame(backtest.mean(axis = 1))
        port.columns = ['portfolio']

        #1st step. run the regression of factors on the portfolio
        Y = pd.DataFrame(port)
        X = pd.DataFrame(factor_model.loc[port.index,'Mkt-RF'])
        X.loc[:,'market_dummy'] = X['Mkt-RF'].copy()
        X.loc[X['market_dummy'] <= 0.0, 'market_dummy'] = 0.0
        X['intercept'] = 1.0        
        model = sm.OLS(Y,X,missing = 'drop')
        #robust covariance results
        results = model.fit(cov_type='HAC',cov_kwds={'maxlags':1})
        #results.params['intercept'] = round(results.params['intercept'] * 12.*100.0, 2)
        
        print(results.summary())
                    
        return results
        
    
    def factor_results(self, backtest, factor_model, mode = 'time_series'):
        
        port= pd.DataFrame(backtest.mean(axis = 1))
        port.columns = ['portfolio']

        Y = pd.DataFrame(port)
        try:
            X  = factor_model.loc[port.index,factor_model.columns]
        except:
            X = factor_model.copy()
       
            
        df = pd.concat([Y,X], axis = 1)
        df = df.dropna()
        Y = pd.DataFrame(df.loc[:,'portfolio'])
        X = df.loc[:,X.columns]
        
        X['intercept'] = 1.0
        
        
        if mode == 'famma-macbeth':
            model = sm.OLS(Y,X,missing = 'drop')
            results = model.fit()
            #results.params['intercept'] = round(results.params['intercept'] * 12.*100.0, 2)
            
            res = results
            print("First Step")
            print(results.summary())  
    
            #2nd step. regress all asset returns for a fixed time period against the estimated betas to determine the risk premium for each factor.
    
            df= pd.concat([Y,X], axis = 1)
            df.loc[:,'period'] = df.index
            df = df.dropna(axis = 0, how = 'any')
    
            try:
                result = fama_macbeth(df,'period','portfolio',['Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA'],intercept=True)
                fm_sum = fm_summary(result)
                print("Second Stage Fama Macbeth")
                print(fm_sum)
                
                for i in results.tvalues.index:
                    results.tvalues.loc[i] = fm_sum.loc[i, 'tstat']
                    results.pvalues.loc[i] = 2*(1.-scipy.stats.norm.cdf(abs(results.tvalues.loc[i])))
                    results.bse.loc[i] = fm_sum.loc[i, 'std_error']
                
            except:
                fm_sum = ''
                print('error fama macbeth')
                print(sys.exc_info()[0])
            return res, fm_sum
        else:
            model = sm.OLS(Y,X,missing = 'drop')
            #robust covariance results
            results = model.fit(cov_type='HAC',cov_kwds={'maxlags':1})
            #results.params['intercept'] = round(results.params['intercept'] * 12.*100.0, 2)
            
            res = results
            print(results.summary())
            
            return results, 0.0
        
    def factor_results_umd(self, backtest, factor_model, mode = 'time_series'):
        
        port= pd.DataFrame(backtest.mean(axis = 1))
        port.columns = ['portfolio']

        Y = pd.DataFrame(port)
        try:
            X  = factor_model.loc[port.index,factor_model.columns]
        except:
            X = factor_model.copy()
       
            
        df = pd.concat([Y,X], axis = 1)
        df = df.dropna()
        Y = pd.DataFrame(df.loc[:,'portfolio'])
        X = df.loc[:,X.columns]
        
        X['intercept'] = 1.0
        
        if mode == 'famma-macbeth':
            model = sm.OLS(Y,X,missing = 'drop')
            results = model.fit()
            #results.params['intercept'] = round(results.params['intercept'] * 12.*100.0, 2)
            
            res = results
            print("First Step")
            print(results.summary())  
    
            #2nd step. regress all asset returns for a fixed time period against the estimated betas to determine the risk premium for each factor.
    
            df= pd.concat([Y,X], axis = 1)
            df.loc[:,'period'] = df.index
            df = df.dropna(axis = 0, how = 'any')
    
            try:
                result = fama_macbeth(df,'period','portfolio',['Mkt-RF', 'SMB', 'HML', 'Mom'],intercept=True)
                fm_sum = fm_summary(result)
                print("Second Stage Fama Macbeth")
                print(fm_sum)
                
                for i in results.tvalues.index:
                    results.tvalues.loc[i] = fm_sum.loc[i, 'tstat']
                    results.pvalues.loc[i] = 2*(1.-scipy.stats.norm.cdf(abs(results.tvalues.loc[i])))
                    results.bse.loc[i] = fm_sum.loc[i, 'std_error']
                
            except:
                fm_sum = ''
                print('error fama macbeth')
                print(sys.exc_info()[0])
            return res, fm_sum
        else:
            model = sm.OLS(Y,X,missing = 'drop')
            #robust covariance results
            results = model.fit(cov_type='HAC',cov_kwds={'maxlags':1})
            #results.params['intercept'] = round(results.params['intercept'] * 12.*100.0, 2)
            
            res = results
            print(results.summary())
            
        return results, 0.0
    
    def factor_results_qfactor(self, backtest, factor_model, mode = 'time_series'):
        
        port= pd.DataFrame(backtest.mean(axis = 1))
        port.columns = ['portfolio']

        #1st step. run the regression of factors on the portfolio
        Y = pd.DataFrame(port)
        try:
            X  = factor_model.loc[port.index,factor_model.columns]
        except:
            X = factor_model.copy()
       
            
        df = pd.concat([Y,X], axis = 1)
        df = df.dropna()
        Y = pd.DataFrame(df.loc[:,'portfolio'])
        X = df.loc[:,X.columns]
        
        X['intercept'] = 1.0
        
        
        if mode == 'famma-macbeth':
            model = sm.OLS(Y,X,missing = 'drop')
            results = model.fit()
            #results.params['intercept'] = round(results.params['intercept'] * 12.*100.0, 2)
            
            res = results
            print("First Step")
            print(results.summary())  
    
            #2nd step. regress all asset returns for a fixed time period against the estimated betas to determine the risk premium for each factor.
    
            df= pd.concat([Y,X], axis = 1)
            df.loc[:,'period'] = df.index
            df = df.dropna(axis = 0, how = 'any')
    
            try:
                result = fama_macbeth(df,'period','portfolio',['R_MKT', 'R_ME', 'R_IA', 'R_ROE', 'R_EG'],intercept=True)
                fm_sum = fm_summary(result)
                print("Second Stage Fama Macbeth")
                print(fm_sum)
                
                for i in results.tvalues.index:
                    results.tvalues.loc[i] = fm_sum.loc[i, 'tstat']
                    results.pvalues.loc[i] = 2*(1.-scipy.stats.norm.cdf(abs(results.tvalues.loc[i])))
                    results.bse.loc[i] = fm_sum.loc[i, 'std_error']
                
            except:
                fm_sum = ''
                print('error fama macbeth')
                print(sys.exc_info()[0])
            return res, fm_sum
        else:
            model = sm.OLS(Y,X,missing = 'drop')
            #robust covariance results
            results = model.fit(cov_type='HAC',cov_kwds={'maxlags':1})
            #results.params['intercept'] = round(results.params['intercept'] * 12.*100.0, 2)
            
            res = results
            print(results.summary())
            
        return results, 0.0
    
    def factor_results_stambaugh_yuan(self, backtest, factor_model, mode = 'time_series'):
        
        port= pd.DataFrame(backtest.mean(axis = 1))
        port.columns = ['portfolio']

        #1st step. run the regression of factors on the portfolio
        Y = pd.DataFrame(port)
        try:
            X  = factor_model.loc[port.index,factor_model.columns]
        except:
            X = factor_model.copy()
       
            
        df = pd.concat([Y,X], axis = 1)
        df = df.dropna()
        Y = pd.DataFrame(df.loc[:,'portfolio'])
        X = df.loc[:,X.columns]
        
        X['intercept'] = 1.0
        
        
        if mode == 'famma-macbeth':
            model = sm.OLS(Y,X,missing = 'drop')
            results = model.fit()
            #results.params['intercept'] = round(results.params['intercept'] * 12.*100.0, 2)
            
            res = results
            print("First Step")
            print(results.summary())  
    
            #2nd step. regress all asset returns for a fixed time period against the estimated betas to determine the risk premium for each factor.
    
            df= pd.concat([Y,X], axis = 1)
            df.loc[:,'period'] = df.index
            df = df.dropna(axis = 0, how = 'any')
    
            try:
                result = fama_macbeth(df,'period','portfolio',['MKTRF','SMB','MGMT','PERF'],intercept=True)
                fm_sum = fm_summary(result)
                print("Second Stage Fama Macbeth")
                print(fm_sum)
                
                for i in results.tvalues.index:
                    results.tvalues.loc[i] = fm_sum.loc[i, 'tstat']
                    results.pvalues.loc[i] = 2*(1.-scipy.stats.norm.cdf(abs(results.tvalues.loc[i])))
                    results.bse.loc[i] = fm_sum.loc[i, 'std_error']
                
            except:
                fm_sum = ''
                print('error fama macbeth')
                print(sys.exc_info()[0])
            return res, fm_sum
        else:
            model = sm.OLS(Y,X,missing = 'drop')
            #robust covariance results
            results = model.fit(cov_type='HAC',cov_kwds={'maxlags':1})
            #results.params['intercept'] = round(results.params['intercept'] * 12.*100.0, 2)
            
            res = results
            print(results.summary())
            
        return results, 0.0
            
    
    def factor_results_capm(self, backtest, factor_model, mode = 'time_series'):
        
        port= pd.DataFrame(backtest.mean(axis = 1))
        port.columns = ['portfolio']

        #1st step. run the regression of factors on the portfolio
        Y = pd.DataFrame(port)
        X  = factor_model.loc[port.index,factor_model.columns]

        
        Y = pd.DataFrame(port)
        try:
            X  = factor_model.loc[port.index,factor_model.columns]
        except:
            X = factor_model.copy()
       
            
        df = pd.concat([Y,X], axis = 1)
        df = df.dropna()
        Y = pd.DataFrame(df.loc[:,'portfolio'])
        X = df.loc[:,X.columns]
        
        X['intercept'] = 1.0
        X= X[['Mkt-RF', 'intercept']]
        
        if mode == 'famma-macbeth':
            model = sm.OLS(Y,X,missing = 'drop')
            results = model.fit()
            #results.params['intercept'] = round(results.params['intercept'] * 12.*100.0, 2)
            
            res = results
            print("First Step")
            print(results.summary())  
    
            #2nd step. regress all asset returns for a fixed time period against the estimated betas to determine the risk premium for each factor.
    
            df= pd.concat([Y,X], axis = 1)
            df.loc[:,'period'] = df.index
            df = df.dropna(axis = 0, how = 'any')
    
            try:
                result = fama_macbeth(df,'period','portfolio',['Mkt-RF'],intercept=True)
                fm_sum = fm_summary(result)
                print("Second Stage Fama Macbeth")
                print(fm_sum)
                
                for i in results.tvalues.index:
                    results.tvalues.loc[i] = fm_sum.loc[i, 'tstat']
                    results.pvalues.loc[i] = 2*(1.-scipy.stats.norm.cdf(abs(results.tvalues.loc[i])))
                    results.bse.loc[i] = fm_sum.loc[i, 'std_error']
                
            except:
                fm_sum = ''
                print('error fama macbeth')
                print(sys.exc_info()[0])
            return res, fm_sum
        else:
            model = sm.OLS(Y,X,missing = 'drop')
            #robust covariance results
            results = model.fit(cov_type='HAC',cov_kwds={'maxlags':1})
            #results.params['intercept'] = round(results.params['intercept'] * 12.*100.0, 2)
            
            res = results
            print(results.summary())
            
            return results, 0.0

 
    
    #this method is for actually running the backtest and getting the portfolios returns and allocations
    def run_backtest(self, returns, lookback_backtest_input, input_classifiers, inputs, outputs,  ensemble = 'no', trade_type = 'both'):
        """
        the input_classifiers is a string of which classifier to use. This can be an array for multiple classifiers
        lookback_test is an integer for the time length to use for the feature set to use for the analysis
        inputs is a dataframe of the feature set
        output is a dataframe of the output variable to train our feature set on. This is returns across the assets
        for analysis
        ensemble is a yes or not string for whether to take an array of classifiers and a voting method to get 
        asset returns
        trade_type: this determines if the portfolio is long only, short only, or both
        """
        
        #gets the lowercase sting of the ensemble input.
        ensemble = ensemble.lower()
        
        #if we input multiple classifiers this converts the system to an ensemble output. You can only input one
        #classifier at a time or an ensemble system
        if ensemble == 'no' and len(input_classifiers) > 1:
            print("For non emsemble systems the amount of input classifiers are restricted to one. The following backtest will be changed to a ensemble system")
            ensemble = 'yes'
        
        #dictionary to convert the classifiers string inputs to actual sklearn classifiers
        classifiers = {"Logistic": LogisticRegression(solver='lbfgs', dual=True), \
                        "Nearest Neighbors" : KNeighborsClassifier(3, weights = 'distance'), \
                       "Linear SVM" : SVC(),\
                        "RBF SVM": SVC(gamma=2, C=1), \
                        "Gaussian Process" : GaussianProcessClassifier(1.0 * RBF(1.0)), \
                        "Decision Tree" : DecisionTreeClassifier(max_depth=5), \
                        "Random Forest" : RandomForestClassifier(), \
                        "Neural Net": MLPClassifier(solver='adam', learning_rate = 'adaptive', alpha=1e-5, hidden_layer_sizes=(50,),max_iter= 10000, random_state=1), \
                        "AdaBoost": AdaBoostClassifier(n_estimators=25, random_state=0), \
                        "Naive Bayes": GaussianNB(), \
                        "QDA": QuadraticDiscriminantAnalysis(), \
                        "Voter": VotingClassifier(estimators=[('KNN', KNeighborsClassifier(3, weights = 'distance')), ('NN',  MLPClassifier(solver='adam', learning_rate = 'adaptive', alpha=1e-5, hidden_layer_sizes=(50,),max_iter= 10000, random_state=1)), ('rf', RandomForestClassifier(max_depth=5, n_estimators=3, max_features=1, random_state=1))], voting='hard')}
        # RandomForestClassifier(max_depth=5, n_estimators=3, max_features=1, random_state=1), \
        # MLPClassifier(solver='adam', learning_rate = 'adaptive', alpha=1e-3, hidden_layer_sizes=(50,),max_iter= 10000, random_state=1), \
        #create a blank dataframe for our backtest data
        ml_backtest = pd.DataFrame()
        ml_weights = pd.DataFrame()
        ml_backtest_scaled = pd.DataFrame()
        
        #iterate through each symbol and run the backtest on the symbol
        for ticker in inputs.keys():
        
            count = 0
        
            #instantiate a dataframe for our backtest outputs for one ticker. we can only run the backtest on the index of 
            #the inputs. we remove the lookback period for analysis
        
            backtest = pd.DataFrame()
            weights = pd.DataFrame()
            scaled_backtest = pd.DataFrame()
        
            #iterate through the inputs
            for ix, row in inputs[ticker].iterrows(): 
                    #make sure the backctest is greater than the lookbak period for the machine learning model
                if count >= lookback_backtest_input:
                    #the analysis df does not include the current row, count will correspond with the ticker
                    analysis = inputs[ticker][count-lookback_backtest_input:count]
                    if input_classifiers[0] == 'Logistic':
                        analysis = analysis.loc[analysis.index,analysis.columns[0]]
                    analysis_returns = returns.loc[analysis.index]
                    #the y var is the binary returns of the ticker
                    y = outputs[ticker].loc[analysis.index][1:].copy()
                    scaled = .05 / pd.DataFrame(analysis_returns).std()
                    scaled = round(scaled.values[0],2)
                    if ~np.isfinite(scaled):
                        scaled = np.nan
                    #the x var is the returns for the ticker on the analysis index lagged by 1
                    x = inputs[ticker].loc[analysis.index].shift(1)[1:].copy()
                    x = x.dropna(axis = 1, how = 'any').copy()
                    #test x represents the yesterdays x value, this is for the outsample prediction on y
                    test_x = inputs[ticker].loc[analysis.index].tail(1)
                    test_x = test_x[x.columns]
                    if ensemble == 'no':
                        for name in input_classifiers:
                            #fit the classifier to the inputs
                            try:
                                clf = classifiers[name]
                                clf.fit(x.to_numpy(), y.values.ravel())
                                #make a prediction on the input features 
                                predict = clf.predict(x.to_numpy())
                                predict = pd.DataFrame(data = predict, index = y.index, columns = ['predict'])
                                #mse = np.sum((y.values - predict.values.T)**2)
                                #predict the last observation in the feature set to predict y tomorrow
                                outsample = clf.predict(test_x.to_numpy())[0]
                            except:
                                outsample = "error"
                        #if the classifier is one. we long the security times the leverage
                        if outsample != "error":
                            if trade_type == 'both':
                                if outsample == 1.0:
                                    backtest.loc[ix, ticker]  = returns.loc[ix, ticker] 
                                    scaled_backtest.loc[ix, ticker] = returns.loc[ix, ticker]* scaled
                                    weights.loc[ix, ticker] = 1.0
                                #if the classifier is 0 we can choose to short the security or be long only
                                else:
                                    backtest.loc[ix, ticker]  = -returns.loc[ix, ticker] 
                                
                                    scaled_backtest.loc[ix, ticker] = -returns.loc[ix, ticker]* scaled
                                    weights.loc[ix, ticker] = -1.0
        
                            elif trade_type == 'short':
                                if outsample == 1.0:
                                    backtest.loc[ix, ticker]  = 0.0
                                    scaled_backtest.loc[ix, ticker] = 0.0
                                    weights.loc[ix, ticker] = 0.0
                                #if the classifier is 0 we can choose to short the security or be long only
                                else:
                                    backtest.loc[ix, ticker]  = -returns.loc[ix, ticker] 
                                    scaled_backtest.loc[ix, ticker] = -returns.loc[ix, ticker] * scaled
                                    weights.loc[ix, ticker] = -1.0
        
                            elif trade_type == 'long':
                                if outsample == 1.0:
                                    backtest.loc[ix, ticker]  = returns.loc[ix, ticker] 
                                    scaled_backtest.loc[ix, ticker] = returns.loc[ix, ticker] * scaled
                                    weights.loc[ix, ticker] = 1.0
                                #if the classifier is 0 we can choose to short the security or be long only
                                else:
                                    backtest.loc[ix, ticker]  = 0.0
                                    scaled_backtest.loc[ix, ticker] = 0.0
                                    weights.loc[ix, ticker] = 0.0
                        else:
                            #if the machine learning does produce an input due to missing data, simply do not trade
                            backtest.loc[ix, ticker]  = np.nan
                            scaled_backtest.loc[ix, ticker] = np.nan
                            weights.loc[ix, ticker] = np.nan
        
                    #to do the voting method on all the classifiers
                    else:
                        all_outsample = []
                        for name in input_classifiers:
                            try:
                                clf = classifiers[name]
                                clf.fit(x.to_numpy(), y.values.ravel())
                                predict = clf.predict(x.to_numpy())
                                predict = pd.DataFrame(data = predict, index = y.index, columns = ['predict'])
                                #mse = np.sum((y.values - predict.values.T)**2)
                                outsample = clf.predict(test_x.to_numpy())[0]
                                all_outsample.append(outsample)
                            except:
                                all_outsample.append('error')
                        #handle errors if there 
                        if 'error' not in all_outsample:
                            #take the average of the classfier outputs 
                            avg = sum(all_outsample) / len(all_outsample)  
                            #if greater than .5, then go long the security. this paramber could be optimized
                            if avg >= 0.5:
                                backtest.loc[ix, ticker]  = returns.loc[ix, ticker] 
                                scaled_backtest.loc[ix, ticker] = returns.loc[ix, ticker] * scaled
                                weights.loc[ix, ticker] = 1.0
            
                            #if the classifier is 0 we can choose to short the security or be long only
                            else:
                                backtest.loc[ix, ticker]  = -returns.loc[ix, ticker]
                                scaled_backtest.loc[ix, ticker] = returns.loc[ix, ticker] * scaled
                                weights.loc[ix, ticker] = -1.0
                        else:
                            backtest.loc[ix, ticker]  = -returns.loc[ix, ticker]
                            scaled_backtest.loc[ix, ticker] = -returns.loc[ix, ticker] * scaled
                            weights.loc[ix, ticker] = -1.0
                            
                count = count + 1
                #keep a rolling count of the number of days in the backtest
        
            #concatentate the backtest for one ticker with the rest to give the portfolio. 
            if ml_backtest.empty:
                ml_backtest = backtest.copy()
                ml_backtest_scaled = scaled_backtest.copy()
                ml_weights = weights.copy()
            else:
                ml_backtest = pd.concat([ml_backtest, backtest], axis = 1)
                ml_backtest_scaled = pd.concat([ml_backtest_scaled, scaled_backtest], axis =1)
                ml_weights = pd.concat([ml_weights, weights], axis = 1)
                #return a dataframe of all the backtests on input tickers
                
        return ml_backtest, ml_weights, ml_backtest_scaled
    
    #this method is for actually running the backtest and getting the portfolios returns and allocations

    def run_backtest_mt_ens(self, returns, lookback_backtest_input, input_classifiers, inputs, outputs,  ensemble = 'no', trade_type = 'both'):
        """
        the input_classifiers is a string of which classifier to use. This can be an array for multiple classifiers
        lookback_test is an integer for the time length to use for the feature set to use for the analysis
        inputs is a dataframe of the feature set
        output is a dataframe of the output variable to train our feature set on. This is returns across the assets
        for analysis
        ensemble is a yes or not string for whether to take an array of classifiers and a voting method to get 
        asset returns
        trade_type: this determines if the portfolio is long only, short only, or both
        """
        
        #gets the lowercase sting of the ensemble input.
        ensemble = ensemble.lower()
        
        #if we input multiple classifiers this converts the system to an ensemble output. You can only input one
        #classifier at a time or an ensemble system
        if ensemble == 'no' and len(input_classifiers) > 1:
            print("For non emsemble systems the amount of input classifiers are restricted to one. The following backtest will be changed to a ensemble system")
            ensemble = 'yes'
        
        
        #dictionary to convert the classifiers string inputs to actual sklearn classifiers
        classifiers = {"Logistic": LogisticRegression(solver='lbfgs', dual=False), \
                        "Nearest Neighbors" : KNeighborsClassifier(3), \
                       "Linear SVM" : SVC(),\
                        "RBF SVM": SVC(gamma=2, C=1), \
                        "Gaussian Process" : GaussianProcessClassifier(1.0 * RBF(1.0)), \
                        "Decision Tree" : DecisionTreeClassifier(max_depth=5), \
                        "Random Forest" : RandomForestClassifier(max_depth=3, n_estimators=2, max_features=1, random_state=1), \
                        "Neural Net": MLPClassifier(solver='adam', learning_rate = 'adaptive', alpha=1e-3, hidden_layer_sizes=(5),max_iter= 10000, random_state=1), \
                        "AdaBoost": AdaBoostClassifier(n_estimators=5, random_state=0), \
                        "Naive Bayes": GaussianNB(), \
                        "QDA": QuadraticDiscriminantAnalysis()}
        
        #create a blank dataframe for our backtest data
        ml_backtest = pd.DataFrame()
        ml_weights = pd.DataFrame()
        
        #iterate through each symbol and run the backtest on the symbol
        for ticker in inputs.keys():
        
            count = 0
        
            #instantiate a dataframe for our backtest outputs for one ticker. we can only run the backtest on the index of 
            #the inputs. we remove the lookback period for analysis
        
            backtest = pd.DataFrame()
            weights = pd.DataFrame()
        
            #iterate through the inputs
            for ix, row in inputs[ticker].iterrows(): 
                    #make sure the backctest is greater than the lookbak period for the machine learning model
                if count >= lookback_backtest_input:
                    #the analysis df does not include the current row, count will correspond with the ticker
                    analysis = inputs[ticker][count-lookback_backtest_input:count]
        
                    #the y var is the binary returns of the ticker
                    y = outputs[ticker].loc[analysis.index][1:].copy()
                    #the x var is the returns for the ticker on the analysis index lagged by 1
                    x = inputs[ticker].loc[analysis.index].shift(1)[1:].copy()
                    
                    #test x represents the yesterdays x value, this is for the outsample prediction on y
                    test_x = inputs[ticker].loc[analysis.index].tail(1)
                    
                    #to run a single classifier
                    if ensemble == 'no':
                        for name in input_classifiers:
                            #fit the classifier to the inputs
                            predict_s = []
                            for fs in x.columns:
                                try:
                                    clf = classifiers[name]
                                    clf.fit(x.loc[:,fs].values.reshape(-1, 1), y.values.ravel())
                                    #make a prediction on the input features 
                                    predict = clf.predict(x.loc[:,fs].values.reshape(-1,1))
                                    predict = pd.DataFrame(data = predict, index = y.index, columns = ['predict'])
                                    #mse = np.sum((y.values - predict.values.T)**2)
                                    #predict the last observation in the feature set to predict y tomorrow
                                    outsample = clf.predict(test_x.loc[:,fs].values.reshape(-1,1))[0]
                                    predict_s.append(outsample)

                                except:
                                    predict_s.append("nan")

                        predict_s = list(filter(lambda a: a != "nan", predict_s))
                        #if the classifier is one. we long the security times the leverage
                        if len(predict_s) > 0:
                            avg = sum(predict_s) / len(predict_s)
                            if avg > .5:
                                outsample = 1.0
                            else:
                                outsample = 0.0
                        else:
                            outsample = "error"
                            
                        if outsample != "error":
                            if trade_type == 'both':
                                if outsample == 1.0:
                                    backtest.loc[ix, ticker]  = returns.loc[ix, ticker] 
                                    weights.loc[ix, ticker] = 1.0
                                #if the classifier is 0 we can choose to short the security or be long only
                                else:
                                    backtest.loc[ix, ticker]  = -returns.loc[ix, ticker] 
                                    weights.loc[ix, ticker] = -1.0
        
                            elif trade_type == 'short':
                                if outsample == 1.0:
                                    backtest.loc[ix, ticker]  = 0.0
                                    weights.loc[ix, ticker] = 1.0
                                #if the classifier is 0 we can choose to short the security or be long only
                                else:
                                    backtest.loc[ix, ticker]  = -returns.loc[ix, ticker] 
                                    weights.loc[ix, ticker] = -1.0
        
                            elif trade_type == 'long':
                                if outsample == 1.0:
                                    backtest.loc[ix, ticker]  = returns.loc[ix, ticker] 
                                    weights.loc[ix, ticker] = 1.0
                                #if the classifier is 0 we can choose to short the security or be long only
                                else:
                                    backtest.loc[ix, ticker]  = 0.0
                                    weights.loc[ix, ticker] = -1.0
                        else:
                            #if the machine learning does produce an input due to missing data, simply do not trade
                            backtest.loc[ix, ticker]  = np.nan
                            weights.loc[ix, ticker] = np.nan
        
                    #to do the voting method on all the classifiers
                    else:
                        all_outsample = []
                        for name in input_classifiers:
                            try:
                                clf = classifiers[name]
                                clf.fit(x.to_numpy(), y.values.ravel())
                                predict = clf.predict(x.to_numpy())
                                predict = pd.DataFrame(data = predict, index = y.index, columns = ['predict'])
                                #mse = np.sum((y.values - predict.values.T)**2)
                                outsample = clf.predict(test_x.to_numpy())[0]
                                all_outsample.append(outsample)
                            except:
                                all_outsample.append('error')
                        #handle errors if there 
                        if 'error' not in all_outsample:
                            #take the average of the classfier outputs 
                            avg = sum(all_outsample) / len(all_outsample)  
                            #if greater than .5, then go long the security. this paramber could be optimized
                            if avg >= 0.5:
                                backtest.loc[ix, ticker]  = returns.loc[ix, ticker] 
                                weights.loc[ix, ticker] = 1.0
            
                            #if the classifier is 0 we can choose to short the security or be long only
                            else:
                                backtest.loc[ix, ticker]  = -returns.loc[ix, ticker]
                                weights.loc[ix, ticker] = -1.0
                        else:
                            backtest.loc[ix, ticker]  = -returns.loc[ix, ticker]
                            weights.loc[ix, ticker] = -1.0
                            
                count = count + 1
                #keep a rolling count of the number of days in the backtest
        
            #concatentate the backtest for one ticker with the rest to give the portfolio. 
            if ml_backtest.empty:
                ml_backtest = backtest.copy()
                ml_weights = weights.copy()
            else:
                ml_backtest = pd.concat([ml_backtest, backtest], axis = 1)
                ml_weights = pd.concat([ml_weights, weights], axis = 1)
                #return a dataframe of all the backtests on input tickers
        return ml_backtest, ml_weights     
    
    def run_backtest_ens(self, returns, lookback_backtest_input, input_classifiers, inputs, outputs,  ensemble = 'no', trade_type = 'both'):
        """
        the input_classifiers is a string of which classifier to use. This can be an array for multiple classifiers
        lookback_test is an integer for the time length to use for the feature set to use for the analysis
        inputs is a dataframe of the feature set
        output is a dataframe of the output variable to train our feature set on. This is returns across the assets
        for analysis
        ensemble is a yes or not string for whether to take an array of classifiers and a voting method to get 
        asset returns
        trade_type: this determines if the portfolio is long only, short only, or both
        """
        
        #gets the lowercase sting of the ensemble input.
        ensemble = ensemble.lower()
        
        #if we input multiple classifiers this converts the system to an ensemble output. You can only input one
        #classifier at a time or an ensemble system
        if ensemble == 'no' and len(input_classifiers) > 1:
            print("For non emsemble systems the amount of input classifiers are restricted to one. The following backtest will be changed to a ensemble system")
            ensemble = 'yes'
        
        #dictionary to convert the classifiers string inputs to actual sklearn classifiers
        classifiers = {"Logistic": LogisticRegression(solver='lbfgs', dual=True), \
                        "Nearest Neighbors" : KNeighborsClassifier(3, weights = 'distance'), \
                       "Linear SVM" : SVC(),\
                        "RBF SVM": SVC(gamma=2, C=1), \
                        "Gaussian Process" : GaussianProcessClassifier(1.0 * RBF(1.0)), \
                        "Decision Tree" : DecisionTreeClassifier(max_depth=5), \
                        "Random Forest" : RandomForestClassifier(max_depth=5, n_estimators=3, max_features=1, random_state=1), \
                        "Neural Net": MLPClassifier(solver='adam', learning_rate = 'adaptive', alpha=1e-5, hidden_layer_sizes=(50,),max_iter= 10000, random_state=1), \
                        "AdaBoost": AdaBoostClassifier(n_estimators=100, random_state=0), \
                        "Naive Bayes": GaussianNB(), \
                        "QDA": QuadraticDiscriminantAnalysis(), \
                        "Voter": VotingClassifier(estimators=[('KNN', KNeighborsClassifier(3, weights = 'distance')), ('NN',  MLPClassifier(solver='adam', learning_rate = 'adaptive', alpha=1e-5, hidden_layer_sizes=(50,),max_iter= 10000, random_state=1)), ('rf', RandomForestClassifier(max_depth=5, n_estimators=3, max_features=1, random_state=1))], voting='hard')}
        # RandomForestClassifier(max_depth=5, n_estimators=3, max_features=1, random_state=1), \
        # MLPClassifier(solver='adam', learning_rate = 'adaptive', alpha=1e-3, hidden_layer_sizes=(50,),max_iter= 10000, random_state=1), \
        #create a blank dataframe for our backtest data
        ml_backtest = pd.DataFrame()
        ml_weights = pd.DataFrame()
        ml_backtest_scaled = pd.DataFrame()
        
        #iterate through each symbol and run the backtest on the symbol
        for ticker in inputs.keys():
        
            count = 0
        
            #instantiate a dataframe for our backtest outputs for one ticker. we can only run the backtest on the index of 
            #the inputs. we remove the lookback period for analysis
        
            backtest = pd.DataFrame()
            weights = pd.DataFrame()
            scaled_backtest = pd.DataFrame()
        
            #iterate through the inputs
            for ix, row in inputs[ticker].iterrows(): 
                    #make sure the backctest is greater than the lookbak period for the machine learning model
                if count >= lookback_backtest_input:
                    #the analysis df does not include the current row, count will correspond with the ticker
                    analysis = inputs[ticker][count-lookback_backtest_input:count]
                    if input_classifiers[0] == 'Logistic':
                        analysis = analysis.loc[analysis.index,analysis.columns[0]]
                    analysis_returns = returns.loc[analysis.index]
                    #the y var is the binary returns of the ticker
                    y = outputs[ticker].loc[analysis.index][1:].copy()
                    scaled = .05 / pd.DataFrame(analysis_returns).std()
                    scaled = round(scaled.values[0],2)
                    if ~np.isfinite(scaled):
                        scaled = np.nan
                    #the x var is the returns for the ticker on the analysis index lagged by 1
                    x = inputs[ticker].loc[analysis.index].shift(1)[1:].copy()
                    x = x.dropna(axis = 1, how = 'any').copy()
                    x = (x - x.mean()) / x.std()
                    #test x represents the yesterdays x value, this is for the outsample prediction on y
                    test_x = inputs[ticker].loc[analysis.index].tail(1)
                    test_x = test_x[x.columns]
                    if ensemble == 'no':
                        for name in input_classifiers:
                            #fit the classifier to the inputs
                            predict_s = []
                            for fs in x.columns:
                                try:
                                    clf = classifiers[name]
                                    clf.fit(x.loc[:,fs].values.reshape(-1, 1), y.values.ravel())
                                    #make a prediction on the input features 
                                    predict = clf.predict(x.loc[:,fs].values.reshape(-1,1))
                                    predict = pd.DataFrame(data = predict, index = y.index, columns = ['predict'])
                                    #mse = np.sum((y.values - predict.values.T)**2)
                                    #predict the last observation in the feature set to predict y tomorrow
                                    outsample = clf.predict(test_x.loc[:,fs].values.reshape(-1,1))[0]
                                    predict_s.append(outsample)

                                except:
                                    predict_s.append("nan")

                        predict_s = list(filter(lambda a: a != "nan", predict_s))
                        #if the classifier is one. we long the security times the leverage
                        if len(predict_s) > 0:
                            avg = sum(predict_s) / len(predict_s)
                            if avg > .5:
                                outsample = 1.0
                            else:
                                outsample = 0.0
                        else:
                            outsample = "error"
                        #if the classifier is one. we long the security times the leverage
                        if outsample != "error":
                            if trade_type == 'both':
                                if outsample == 1.0:
                                    backtest.loc[ix, ticker]  = returns.loc[ix, ticker] 
                                    scaled_backtest.loc[ix, ticker] = returns.loc[ix, ticker]* scaled
                                    weights.loc[ix, ticker] = 1.0
                                #if the classifier is 0 we can choose to short the security or be long only
                                else:
                                    backtest.loc[ix, ticker]  = -returns.loc[ix, ticker] 
                                
                                    scaled_backtest.loc[ix, ticker] = -returns.loc[ix, ticker]* scaled
                                    weights.loc[ix, ticker] = -1.0
        
                            elif trade_type == 'short':
                                if outsample == 1.0:
                                    backtest.loc[ix, ticker]  = 0.0
                                    scaled_backtest.loc[ix, ticker] = 0.0
                                    weights.loc[ix, ticker] = 0.0
                                #if the classifier is 0 we can choose to short the security or be long only
                                else:
                                    backtest.loc[ix, ticker]  = -returns.loc[ix, ticker] 
                                    scaled_backtest.loc[ix, ticker] = -returns.loc[ix, ticker] * scaled
                                    weights.loc[ix, ticker] = -1.0
        
                            elif trade_type == 'long':
                                if outsample == 1.0:
                                    backtest.loc[ix, ticker]  = returns.loc[ix, ticker] 
                                    scaled_backtest.loc[ix, ticker] = returns.loc[ix, ticker] * scaled
                                    weights.loc[ix, ticker] = 1.0
                                #if the classifier is 0 we can choose to short the security or be long only
                                else:
                                    backtest.loc[ix, ticker]  = 0.0
                                    scaled_backtest.loc[ix, ticker] = 0.0
                                    weights.loc[ix, ticker] = 0.0
                        else:
                            #if the machine learning does produce an input due to missing data, simply do not trade
                            backtest.loc[ix, ticker]  = np.nan
                            scaled_backtest.loc[ix, ticker] = np.nan
                            weights.loc[ix, ticker] = np.nan
        
                    #to do the voting method on all the classifiers
                    else:
                        all_outsample = []
                        for name in input_classifiers:
                            try:
                                clf = classifiers[name]
                                clf.fit(x.to_numpy(), y.values.ravel())
                                predict = clf.predict(x.to_numpy())
                                predict = pd.DataFrame(data = predict, index = y.index, columns = ['predict'])
                                #mse = np.sum((y.values - predict.values.T)**2)
                                outsample = clf.predict(test_x.to_numpy())[0]
                                all_outsample.append(outsample)
                            except:
                                all_outsample.append('error')
                        #handle errors if there 
                        if 'error' not in all_outsample:
                            #take the average of the classfier outputs 
                            avg = sum(all_outsample) / len(all_outsample)  
                            #if greater than .5, then go long the security. this paramber could be optimized
                            if avg >= 0.5:
                                backtest.loc[ix, ticker]  = returns.loc[ix, ticker] 
                                scaled_backtest.loc[ix, ticker] = returns.loc[ix, ticker] * scaled
                                weights.loc[ix, ticker] = 1.0
            
                            #if the classifier is 0 we can choose to short the security or be long only
                            else:
                                backtest.loc[ix, ticker]  = -returns.loc[ix, ticker]
                                scaled_backtest.loc[ix, ticker] = returns.loc[ix, ticker] * scaled
                                weights.loc[ix, ticker] = -1.0
                        else:
                            backtest.loc[ix, ticker]  = -returns.loc[ix, ticker]
                            scaled_backtest.loc[ix, ticker] = -returns.loc[ix, ticker] * scaled
                            weights.loc[ix, ticker] = -1.0
                            
                count = count + 1
                #keep a rolling count of the number of days in the backtest
        
            #concatentate the backtest for one ticker with the rest to give the portfolio. 
            if ml_backtest.empty:
                ml_backtest = backtest.copy()
                ml_backtest_scaled = scaled_backtest.copy()
                ml_weights = weights.copy()
            else:
                ml_backtest = pd.concat([ml_backtest, backtest], axis = 1)
                ml_backtest_scaled = pd.concat([ml_backtest_scaled, scaled_backtest], axis =1)
                ml_weights = pd.concat([ml_weights, weights], axis = 1)
                #return a dataframe of all the backtests on input tickers
                
        return ml_backtest, ml_weights, ml_backtest_scaled
        