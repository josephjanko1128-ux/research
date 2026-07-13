# -*- coding: utf-8 -*-
"""
Created on Sat Feb 15 14:48:13 2020

@author: jjanko
"""
from math import exp, sqrt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import quandl
import statsmodels.api as sm

class Binomial_Constant_R():
    
    def __init__(self):
        self.underlying = []
        self.optval = []
    
    def binomial(self, N, S0, K, r, sigma, T):
        
        
        dt = T/N
        u = exp(sigma*np.sqrt(dt))
        d = u**-1
        p_u = exp(-r*dt) * ((exp(r*dt)-d) / (u-d))
        p_d = exp(-r*dt) * (1-((exp(r*dt)-d) / (u-d)))

        self.underlying = np.zeros((N+1,N+1))
        self.underlying[0,0] = S0
        
        for i in range(N+1):
            if i >= 1:
                self.underlying[i,0] = self.underlying[i-1,0]*u
                for j in range(i+1):
                    if j>=1:
                        self.underlying[i,j] = self.underlying[i-1,j-1]*d

        self.optval = np.zeros((N+1,N+1))
        for j in range(N+1):
            self.optval[N,j] = max(0, self.underlying[N,j]-K)
 
        for i in range(N-1,-1,-1):
            for j in range(i+1):
                self.optval[i,j] = max(0, self.underlying[i,j]-K, (p_u* self.optval[i+1,j]+p_d* self.optval[i+1,j+1]))
                
        return round(self.optval[0,0],2)
    
    

class project():
    
    def __init__(self, inputlist):
        
        self.S0 = inputlist[0]
        self.K=inputlist[1]
        self.mu=inputlist[2]
        self.Time = inputlist[3]
        self.sigma = inputlist[4]
        self.N=inputlist[5]
        self.Start = inputlist[6]
        self.defaultProbability = inputlist[7]
        self.beta = inputlist[8]
        self.Type = inputlist[9]
        self.underlying = []
        self.optval = []
    
    def vasicek(self, r0, kappa, theta, sigma, T, N=1000):    
        seed=777
        samp = 10000
        np.random.seed(seed)
        dt = T/float(N)  
        rates = np.zeros((N, samp))
        rates[0] = r0
        for i in range(1,N):
            Z = np.random.standard_normal(samp)
            rates[i] = rates[i-1] + kappa*(theta-rates[-1])*dt + sigma*Z
            
        return rates
    
    
    def get_p(self, r, dt, u, d):
        r = - self.beta + self.mu - r
        p_u = exp(-r*dt) * ((exp(r*dt)-d) / (u-d))
        p_d = exp(-r*dt) * (1-((exp(r*dt)-d) / (u-d)))
        return p_u, p_d
    
    def binomial(self, T, r):
        self.underlying = []
        self.optval = []
        dt = T/self.N
        u = exp(self.sigma*np.sqrt(dt))
        d = u**-1
        self.underlying = np.zeros((self.N+1,self.N+1))
        self.underlying[0,0] = self.S0

        for i in range(N+1):
            if i >= 1:
                self.underlying[i,0] = self.underlying[i-1,0]*u
                for j in range(i+1):
                    if j>=1:
                        self.underlying[i,j] = self.underlying[i-1,j-1]*d
     
        self.optval = np.zeros((self.N+1,self.N+1))
        for j in range(self.N+1):
            self.optval[self.N,j] = max(0, self.underlying[self.N,j]-self.K)
    
        for i in range(self.N-1,-1,-1):
            for j in range(i+1):
                p_u, p_d = self.get_p(r[i], dt, u, d)
                self.optval[i,j] = max(0, self.underlying[i,j]-self.K, (p_u*self.optval[i+1,j]+p_d*self.optval[i+1,j+1]))
        return round(self.optval[0,0],2)
                

    
    def get_value_bv(self,T, r):
        
        return self.binomial(T,r) * (1.0-self.defaultProbability) 

if __name__ == "__main__":
    
    N = 1000
    simulation_length = 3
    
    #this is for model validation purposes
    b = Binomial_Constant_R()
    
    print('Black Scholes Price')
    print(b.binomial(N, 50., 50., .05, .25, 1.))
    #test the binomial model vasicek 
    
    
    api_key ='cwAFdAtv1-nYDZUFyFeP'
    
    
    #calibration of the vasicek model
    interest_rates = quandl.get("FED/SVENY", authtoken="cwAFdAtv1-nYDZUFyFeP")
    one_year = interest_rates['SVENY01'] / 100.0
    one_year_mean = one_year.mean()
    one_year_vol = (np.log(one_year) - np.log(one_year.shift(1)))[-252:].std() * np.sqrt(252)
    one_year_last_value = one_year[-1]
    
    #to get parameters on annualized level
    #assume there is 252 trading days in the year
    dt = 1./252.
    Y = one_year[1:]
    X = one_year.shift(1)[1:]
    
    X = sm.add_constant(X)
    model = sm.OLS(Y,X)
    results = model.fit()
    
    
    kappa = -np.log(results.params[1]) / dt
    theta = results.params[0] / (1 - results.params[1])
    vol_r = results.resid.std()  * np.sqrt((-2. * np.log(results.params[1])) / (dt*(1 - results.params[1]**2))) 
    theta = theta + ((vol_r**2) / 2 * kappa)
    

    #since the growth of the cash flows are considered constant
    beta = -0.1
    
    shock = .05
    
    #format C,I,cash flow growth,T,sigma,N, Start, Default Probability, Beta
    project1 = [100.0,100.0,.2,1.0,.2,N,1.,.01, beta, 'growth']
    project2 = [102.0,102.0,.2,5.0,.2,N,0.,.25, beta, 'growth']
    project3 = [101.0,101.0,.2,5.0,.2,N,2.,.02, beta, 'growth']
    project4 = [100.0,100.0,.2,50.0,.2,N,0.,.02, beta, 'current']
    #assume the parameters of the vasicek model are constant
    
    projects = [project1, project2, project3, project4]
    projects_upper_bound = projects.copy()
    projects_lower_bound = projects.copy()
    
    
    for i in range(len(projects)):
        #get a list of objects
        
        projects[i] = project(projects[i])
        
        projects_upper_bound[i] = project(projects_upper_bound[i])
        projects_lower_bound[i] = project(projects_lower_bound[i])
        
        if projects[i].Type == 'growth':
            projects_upper_bound[i].mu = projects_upper_bound[i].mu + shock
            projects_lower_bound[i].mu = projects_lower_bound[i].mu - shock
    
    value = {}
    upper_value = {}
    lower_value = {}
    
    
    
    constant_r = [one_year.mean()] * N
    
    i = 0
    while i <= simulation_length :
        v = 0.0
        u_v = 0.0
        l_v = 0.0
        
        for j in projects:
            if j.Start - i <= 0.0 and j.Time + j.Start - i > 0.0:
                r = j.vasicek(one_year_last_value, kappa, theta, vol_r, j.Time + j.Start - i)
                r = pd.DataFrame(r).transpose().mean().transpose().to_numpy()
                v = v + j.get_value_bv(j.Time + j.Start - i, r)
                
        value[i] = round(v,2)
        
        for j in projects_upper_bound:
            if j.Start - i <= 0.0 and j.Time + j.Start - i > 0.0:
                r = j.vasicek(one_year_last_value, kappa, theta, vol_r, j.Time + j.Start - i)
                r = pd.DataFrame(r).transpose().mean().transpose().to_numpy()
                u_v = u_v + j.get_value_bv(j.Time + j.Start - i, r)
                
        
        upper_value[i] = round(u_v, 2)
        
        
        for j in projects_lower_bound:
            if j.Start - i <= 0.0 and j.Time + j.Start - i > 0.0:
                r = j.vasicek(one_year_last_value, kappa, theta, vol_r, j.Time + j.Start - i)
                r = pd.DataFrame(r).transpose().mean().transpose().to_numpy()
                l_v = l_v + j.get_value_bv(j.Time + j.Start - i, r)
        
        lower_value[i] = round(l_v, 2)
        
        i = i + .25
    
    val =pd.DataFrame.from_dict(value, orient = 'index')
    val.columns = ['value']
    print(val.transpose())
    plt.figure()
    
    x = pd.DataFrame.from_dict(value, orient = 'index')
    x.columns  = ['dynamic value of firm']
    
    plt.plot(x, label = 'value')
    plt.plot(pd.DataFrame.from_dict(upper_value, orient = 'index'), label = 'upper value')
    plt.plot(pd.DataFrame.from_dict(lower_value, orient = 'index'), label = 'lower value')
    
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.legend()
    plt.show()
    
    rates = projects[0].vasicek(one_year_last_value, kappa, theta, vol_r, j.Time + j.Start - i)
    sample_path = pd.DataFrame(rates[:,-2])
    sample_path.plot(legend = False)
   