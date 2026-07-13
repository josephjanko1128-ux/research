#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 19 13:18:04 2018

@author: jj
"""

import numpy as np
import scipy.stats as spy
import math

class OptPricing:
    
    #S is the underlying price
    #K is the strike price
    #T is the time till expiration in years
    #r is the risk free interest rate
    #sigma is the volatility
    
    def __init__(self,S,K,T,r,sigma):
        self.S = S
        self.K = K
        self.T = T
        self.r = r
        self.sigma = sigma
        
    def black_scholes(self):
        d = (np.log(self.S / self.K) + (self.r + .5 * self.sigma**2) * self.T) / (self.sigma * np.sqrt(self.T))
        call_bs = self.S * spy.norm.cdf(d) - self.K * (math.e**(-self.r * self.T)) * spy.norm.cdf(d - self.sigma * np.sqrt(self.T))
        put_bs = -((self.S - self.K * math.e**(-self.r * self.T)) - call_bs)
        return call_bs, put_bs

    def corrado_su(self, skew, kurt):
        d = (np.log(self.S / self.K) + (self.r + .5 * self.sigma**2) * self.T) / (self.sigma * np.sqrt(self.T))
        q3 = 1./math.factorial(3) * self.S * self.sigma * np.sqrt(self.T)  * (( 2. * self.sigma * np.sqrt(self.T) - d ) * spy.norm.pdf(d )  + (self.sigma**2) * self.T * spy.norm.cdf(d))           
        q4 = 1./math.factorial(4) * self.S * self.sigma * np.sqrt(self.T)  * (( (d**2) - 1. - 3. * self.sigma * np.sqrt(self.T) * (d - self.sigma * np.sqrt(self.T)   )) * spy.norm.pdf(d) + (self.sigma**3) * (self.T**1.5) * spy.norm.cdf(d))  
        call_bs = self.S * spy.norm.cdf(d) - self.K * (math.e**(-self.r * self.T)) * spy.norm.cdf(d - self.sigma * np.sqrt(self.T))
        #expand on the call price to account for the third and fourth order moments
        call_cs = call_bs + skew * q3 + (kurt - 3.) * q4
        #derive the put from the put-call parirty
        put_csv = -((self.S - self.K * math.e**(-self.r * self.T)) - call_cs)
        
        return call_cs, put_csv
    
if __name__ == '__main__':
    
    opt = OptPricing(100,95,.25,.1,.5)
    #gets the call and put price for black scholes equation
    bs_c_px, bs_p_px = opt.black_scholes()
    #gets the call and put price for corrado su pricing model
    c_px, p_px = opt.corrado_su(.15,3.)
    print(c_px)
    print(p_px)