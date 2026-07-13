import numpy as np
import pandas as pd
import portfolioopt as pfopt
import quandl
import datetime as dt
import urllib as u
from bs4 import BeautifulSoup as bs
from numpy import log,std,polyfit,mean,sqrt, subtract,random, float, array
from sklearn import cluster, covariance
import empyrical
import warnings
import pandas_datareader.data as web
import statsmodels.api as sm

warnings.filterwarnings("ignore")

import scipy

class StockFilter():
    
    def __init__(self, stockList):
        self.stockList = stockList
        self.mcapThreshold = 10.0
        self.salesQQThreshold = 0.0
        self.results = {}
    
    def getFundamentalData(self, ratio):
        self.results = {}
        for stock in self.stockList:
            try:
                url = r'http://finviz.com/quote.ashx?t={}'.format(stock.lower())
                html = u.request.urlopen(url).read()
                soup = bs(html, 'lxml')
                # Change the text below to get a diff metric
                ff =  soup.find(text = ratio)
                ff_ = ff.find_next(class_='snapshot-td2').text
                print( stock + ' fundamental factor: {} = {}'.format(ratio,ff_) )
                print(" ")
                self.results[stock] = ff_
            except Exception as e:
                print(e)
                
    def getFilterResults(self, mcap, salesQQ):
        
        filtered_stock_list = []
        
        for x in self.stockList:
            if float(mcap[x].replace('B','')) > self.mcapThreshold and float(salesQQ[x].replace('%','')) > self.salesQQThreshold:
                filtered_stock_list.append(x)  
        return filtered_stock_list
    
class Performance():
    
    def __init__(self, returns):
        self.returns = returns
    
    def FamaFrench5Factor(self):
        FamaFrench5Factor = web.DataReader('F-F_Research_Data_5_Factors_2x3_daily', 'famafrench')[0]
        
        data = pd.concat([self.returns, FamaFrench5Factor], axis = 1).dropna()
        y = data[data.columns[0]]
        x = data[data.columns[1:]]
        calc = HelperFunctions()
        result = calc.stepwise_regression(x, y)
        resultLag = calc.stepwise_regression(x.shift(1).dropna(), y[1:])
        
        
        model = sm.OLS(y, x).fit()
        print("Non Stepwise Results")
        print(model.summary())
        print("Fama French 5 Factor Stepwise Regression Results")
        print(result)
        print(" ")
        print("Fama French 5 Factor Stepwise Lagged Regression Results")
        print(resultLag)
    
    def BenchMarkIndicies(self, benchmark):
        calc = HelperFunctions()
        result = calc.stepwise_regression(benchmark, self.returns)
        print(result)
    
    def GetPerformanceMetrics(self):
        print("tail ratio:   {}".format(empyrical.tail_ratio(self.returns)))
        print("sortino ratio:   {}".format(empyrical.sortino_ratio(self.returns)))
        print("sharpe ratio:   {}".format(empyrical.sharpe_ratio(self.returns)))
        print("max drawdown:   {}".format(empyrical.max_drawdown(self.returns)))
        print("annual return:   {}".format(empyrical.annual_return(self.returns)))
        print("annual volatility:   {}".format(empyrical.annual_volatility(self.returns)))
        print("cum returns final:   {}".format(empyrical.cum_returns_final(self.returns)))
        print("calmar ratio:   {}".format(empyrical.calmar_ratio(self.returns)))

class Optimization():
    
    def __init__(self, mreturns, cov_mat, avg_rets, benchmark):
        self.returns = mreturns
        self.cov_mat = cov_mat
        self.avg_rets = avg_rets
        self.w = 0
        self.benchmark = benchmark
    
    def section(self, caption):
        print('\n\n' + str(caption))
        print('-' * len(caption))
    
    
    def print_portfolio_info(self, weights):
        """
        Print information on expected portfolio performance.
        """
        self.w = weights
        ret = (weights * self.avg_rets).sum()
        input_ret = (self.w * self.returns).sum(axis = 1)
        p = Performance(input_ret)
        std = (weights * self.returns).sum(1).std()
        print("Optimal weights:\n{}\n".format(weights))
        print("Expected return:   {}".format(ret))
        print("Expected variance: {}".format(std**2))
        v = VAR(30, 1, std, ret, 1.0)
        q_99 = v.getVar(99)
        q_10 = v.getVar(90)
        print("30 Day 99th Percentile VAR:   {}".format(q_99))
        print("30 Day 90th Percentile VAR:   {}".format(q_10))
        p.GetPerformanceMetrics()
        p.FamaFrench5Factor()
        
    
    def run(self):
        
        
        self.section("Example returns")
        print(self.returns.head(10))
        print("...")
    
        self.section("Average returns")
        print(self.avg_rets)
    
        self.section("Covariance matrix")
        print(self.cov_mat)
    
        self.section("Minimum variance portfolio (long only)")
        weights = pfopt.min_var_portfolio(cov_mat)
        self.print_portfolio_info(weights)
    
        self.section("Minimum variance portfolio (long/short)")
        weights = pfopt.min_var_portfolio(cov_mat, allow_short=True)
        self.print_portfolio_info(weights)
    
        # Define some target return, here the 70% quantile of the average returns
        target_ret = avg_rets.quantile(0.7)
    
        self.section("Markowitz portfolio (long only, target return: {:.5f})".format(target_ret))
        weights = pfopt.markowitz_portfolio(cov_mat, avg_rets, target_ret)
        self.print_portfolio_info(weights)
    
        self.section("Markowitz portfolio (long/short, target return: {:.5f})".format(target_ret))
        weights = pfopt.markowitz_portfolio(cov_mat, avg_rets, target_ret, allow_short=True)
        self.print_portfolio_info(weights)
    
        self.section("Markowitz portfolio (market neutral, target return: {:.5f})".format(target_ret))
        weights = pfopt.markowitz_portfolio(cov_mat, avg_rets, target_ret, allow_short=True,
                                                                           market_neutral=True)
        self.print_portfolio_info(weights)
    
        self.section("Tangency portfolio (long only)")
        weights = pfopt.tangency_portfolio(cov_mat, avg_rets)
        weights = pfopt.truncate_weights(weights)   # Truncate some tiny weights
        self.print_portfolio_info(weights)
    
        self.section("Tangency portfolio (long/short)")
        weights = pfopt.tangency_portfolio(cov_mat, avg_rets, allow_short=True)
        self.print_portfolio_info(weights)
        
class VAR():
    
    def __init__(self, days, dt, sigma, mu, startprice):
        self.days = days
        self.dt = 1/float(days)
        self.sigma = sigma
        self.mu = mu
        self.startprice  = startprice
        
    def random_walk(self):
        price = np.zeros(self.days)
        shock = np.zeros(self.days)
        price[0] = self.startprice
        for i in range(1, self.days):
            shock[i] = np.random.normal(loc=self.mu * self.dt, scale= self.sigma * np.sqrt(self.dt))
            price[i] = max(0, price[i-1] + shock[i] * price[i-1])
        return price
    
    def getVar(self, p):
        runs = 2000
        simulations = np.zeros(runs)
        for run in range(runs):
            simulations[run] = self.random_walk()[self.days-1]
        q = (1-np.percentile(simulations, p))
        return q
    
class HelperFunctions():
    
    def __init__(self):
        pass
    
    def hurst(self,ts):
    	lags = range(2, 100)
    	tau = [sqrt(std(subtract(ts[lag:], ts[:-lag]))) for lag in lags]
    	poly = polyfit(log(lags), log(tau), 1)
    	return poly[0]*2.0
     
    def chow(self,Y,X, breakpoint, alpha = 0.05):
        
        k = len(X.columns)
        n = len(X)
     
        # Split into two datasets.
        X1 = X[:breakpoint]
        Y1 = Y[:breakpoint]
     
        X2 = X[breakpoint:]
        Y2= Y[breakpoint:]
     
        # Perform separate three least squares.
        allfit   = pd.ols(y=Y,x=X)
        first_break = pd.ols(y=Y1, x=X1)
        second_break = pd.ols(y=Y2, x=X2)
     
        RSS  = ((allfit.y_predict - Y.mean()) ** 2).sum()
        RSS1 = ((first_break.y_predict - Y1.mean()) ** 2).sum()
        RSS2 = ((second_break.y_predict - Y2.mean()) ** 2).sum()
        df1 = k
        df2 = n - 2 *k
        num = (RSS - (RSS1 + RSS2)) /float(df1)
        den = (RSS1 + RSS2) / (df2)
        Ftest = num/den    
        Fcrit = scipy.stats.f.ppf(1 -0.05, df1, df2)
        return (Ftest, Fcrit)
        
    def calibrate_K(self,resid,delta):
        X= resid[:-1]
        Y = resid[1:]
        fit = pd.ols(y=Y,x=X)
        k = -log(fit.beta[0])/delta
        return k
            
    def OU_process(self,r0, K, theta, sigma, T, dt): 
        N = int(T / dt)    
        rates = [r0] 
        for i in range(N): 
            dr = K*(theta-rates[-1])*dt + sigma*random.normal() 
            rates.append(rates[-1] + dr) 
        return rates
    
    def affinity_propagation(self, stock_symbols,start,end, returns):
        try:
            symbols, names = array(list(stock_symbols.items())).T
            edge_model = covariance.GraphLassoCV()
            models = returns.copy()
            models /= models.std()
            edge_model.fit(models)
            
            cluster_dict = {}
            _, labels = cluster.affinity_propagation(edge_model.covariance_)
            n_labels = labels.max()
            for i in range(n_labels + 1):
                print('Cluster %i: %s' % ((i + 1), ', '.join(names[labels == i])))
                cluster_dict['Cluster '+ str((i+1))]=' '.join(symbols[labels == i]).split(' ')
                print(symbols[labels== i])
            return cluster_dict
        except Exception as e:
            print(e)
            
    def getReturnDf(self, stock_list, start, end):
        prices = pd.DataFrame()
        
        for stock in stock_list:
            data = quandl.get("WIKI/" + stock, start_date=str(start), end_date=str(end),column_index=4)    
            data = pd.DataFrame(data)
            data.columns = [stock]
            if prices.empty:
                prices = data.copy()
            else:
                prices = pd.concat([prices, data], axis  = 1)
                
        returns = prices.pct_change().dropna(axis = 0)
        
        return returns

    def stepwise_regression(self, X, y):
        
        initial_list = []
        threshold = .05
        included = list(initial_list)
        while True:
            changed=False
            # forward step
            excluded = list(set(X.columns)-set(included))
            new_pval = pd.Series(index=excluded)
            for new_column in excluded:
                model = sm.OLS(y, sm.add_constant(pd.DataFrame(X[included+[new_column]]))).fit()
                new_pval[new_column] = model.pvalues[new_column]
            best_pval = new_pval.min()
            if best_pval < threshold:
                best_feature = new_pval.argmin()
                included.append(best_feature)
                changed=True
    
            # backward step
            model = sm.OLS(y, sm.add_constant(pd.DataFrame(X[included]))).fit()
            # use all coefs except intercept
            pvalues = model.pvalues.iloc[1:]
            worst_pval = pvalues.max() # null if pvalues is empty
            if worst_pval > threshold:
                changed=True
                worst_feature = pvalues.argmax()
                included.remove(worst_feature)
            if not changed:
                break
        return model.summary()
    


if __name__ == '__main__':
    
    #import io
    #from contextlib import redirect_stdout

    #f = io.StringIO()
    #with redirect_stdout(f):
        quandl.ApiConfig.api_key = 'cwAFdAtv1-nYDZUFyFeP'
        
        helper = HelperFunctions()
        
        end = dt.date.today()
        start = end - dt.timedelta(days=252)  
        
        stock_symbols = {
            'AAPL': 'Apple',
            'FB': 'Facebook',
            'GOOG': 'Google',
            'DG': 'Dollar General',
            'MSFT': 'Microsoft',
            'PFE': 'Pfizer',
            'F': 'Ford',
            'GM': 'General Motors'}
        
        
        stock_list= stock_symbols.keys()
        
        
        stockFilter = StockFilter(stock_list)
        
        
        stockFilter.getFundamentalData('P/B')
        pb = stockFilter.results
        
        stockFilter.getFundamentalData('Market Cap')
        mcap = stockFilter.results
        
        stockFilter.getFundamentalData('Sales Q/Q')
        salesQQ = stockFilter.results
        
        
        filtered_stock_list = stockFilter.getFilterResults(mcap, salesQQ)
        
        
        returns = helper.getReturnDf(filtered_stock_list, start, end)
        cov_mat = returns.cov()
        avg_rets = returns.mean()
        
        """
        benchmark_indicies = ['SPY', 'IWM','TLT','USO', 'IAU','EEM', 'XLK', 'XLF', 'XLY', 'XLP', 'XLE', 'XLB', 'XLI', 'XLV', 'XLRE', 'XLU' ]
        benchmark_returns = helper.getReturnDf(benchmark_indicies, start, end)
        """
            
        
        optz = Optimization(returns, cov_mat, avg_rets, pd.DataFrame())
        optz.run()
        
        fiter_stock_symbol = {}
        for x in returns.columns:
            fiter_stock_symbol[x] = stock_symbols[x]
            
        print(" ")
        print("Affinity Propagation Clustering of Stocks in Portfolio")
        helper.affinity_propagation(fiter_stock_symbol, start, end, returns)
        print("")
        print('The correlation matrix is: \n')
        print(returns.corr(method = 'pearson'))
        print(" ")
        print("Descriptive Statistics")
        print(returns.describe())
    #out = f.getvalue()
    
    
    