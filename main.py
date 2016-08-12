# -*- coding: utf-8 -*-
from scipy.stats.stats import pearsonr
 
import pandas as pd
 
import numpy as np
import Quandl
import pickle
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style
import datetime
import sys
style.use('fivethirtyeight')
 
 
df = pd.read_csv("UpdatedData.csv")
#print df
 
df = df.dropna()

values = []
std = []
mean = []

for x in range(5,1000):
    for y in range(5, 1000):
        df["RollingRatio"] = pd.rolling_mean(df["Gf1 Last"]/df["Sf1 Last"],x)
        df["RollingSTD"] = pd.rolling_std(df["Gf1 Last"]/df["Sf1 Last"],y)
        print "Mean Rolling days is " + str(x)
        print "Standard deviation Rolling days is " + str(y)
        ratio = 1
        returns = [0]
        lPg = 0
        lPs = 0
        pos = False # True when there is a trade
        Glong = False # True when the trade is long Gold
        Slong = False # True when the trade is long Silver
        money = 100000
        date = [datetime.date(1975,11,26)]
        for index, rows in df.iterrows():
            if pos == True and rows["Gold Expiry Days"] <= 1: # If there is a position and the expiry date is in less than 1 day --> Gold and Silver have same expiry date
                if Glong == True:
                    #print "GLong Rebalance Expiry"
                    #print pos            
                    #print rows["Date"]
                    date.append(rows["Date"])
                    #print "Gold price is " + str(rows["Gf1 Last"]) + " Silver price is " + str(rows["Sf1 Last"])
                    returns.append(  np.log( rows["Gf1 Last"] / lPg ) + np.log(ratio *( (lPs * ratio) /  (rows["Sf1 Last"] ) ) ) )
                    #print  "Log returns are " + str(np.log( rows["Gf1 Last"] / lPg ) + np.log(ratio *( (lPs * ratio) /  (rows["Sf1 Last"] * ratio) ) ))
                    #print "Total money made: " + str( (rows["Gf1 Last"] - lPg)  + 55 * (lPs - rows["Sf1 Last"]) )
                    #money = money + (money / 2)*(rows["Gf1 Last"] - lPg)  +  (money / 2)*(55 * (lPs - rows["Sf1 Last"]) )
                    #print "\n"
                elif Slong == True:
                    #print "SLong Rebalance Expiry"
                    #print rows["Date"]
                    #print "Gold price is " + str(rows["Gf1 Last"]) + " Silver price is " + str(rows["Sf1 Last"])
                    returns.append( np.log( lPg / rows["Gf1 Last"]) + np.log( ratio * (  rows["Sf1 Last"] / lPs  ) ) )
                    #print "Log returns are " + str((np.log( lPg / rows["Gf1 Last"])  + np.log( ratio * (  rows["Sf1 Last"] / lPs ) ) ))
                    date.append(rows["Date"])
                    #print "Total money made: " + str( (lPg - rows["Gf1 Last"])  + 55 * (rows["Sf1 Last"] - lPs) )
                    #money = money + (money / 2)*(lPg - rows["Gf1 Last"])  + (money / 2)*(55 * (rows["Sf1 Last"] - lPs))
                    #print "\n"
                pos = False
                Glong = False
                Slong = False
                #break;
            elif ( pos == True ) and ( rows["RollingRatio"] - ( rows["Gf1 Last"]/ rows["Sf1 Last"] ) ) > ( 0.5 * rows["RollingSTD"] ): # Sell signal
                if Glong == True:
                    #print "GLong Rebalance"
                    #print pos
                    #print rows["Date"]
                    #print "Gold price is " + str(rows["Gf1 Last"]) + " Silver price is " + str(rows["Sf1 Last"])
                    returns.append(  np.log( rows["Gf1 Last"] / lPg ) + np.log(ratio *( (lPs * ratio) /  (rows["Sf1 Last"] ) ) ) )
                    #print "Log Returns are " + str(np.log( rows["Gf1 Last"] / lPg ) + np.log(ratio *( (lPs * ratio) /  (rows["Sf1 Last"] ) ) ))
                    #print "Total money made: " + str( (rows["Gf1 Last"] - lPg)  + 55 * (lPs - rows["Sf1 Last"]) )
                    date.append(rows["Date"])
                    #money = money + (money / 2)*(rows["Gf1 Last"] - lPg)  + (money / 2)*((lPs - rows["Sf1 Last"]))
                    #print "\n"
                    pos = False
                elif Slong == True:
                    #print "SLong Rebalance"
                    #print rows["Date"]
                    #print "Gold price is " + str(rows["Gf1 Last"]) + " Silver price is " + str(rows["Sf1 Last"])
                    returns.append( np.log( lPg / rows["Gf1 Last"]) + np.log((  rows["Sf1 Last"] / lPs  ) ) )
                    #print  "Log returns are " + str(( ( (lPg - rows["Gf1 Last"] ) / rows["Gf1 Last"])))
                    #print "Total money made: " + str( (lPg - rows["Gf1 Last"])  + 55 * (rows["Sf1 Last"] - lPs) )
                    #money = money + (money / 2)*(lPg - rows["Gf1 Last"])  + (money / 2)*((rows["Sf1 Last"] - lPs)) 
                    date.append(rows["Date"])
                    #print "\n"
                    pos = False
                #break;
            # buy signals are below
            if ( rows["Gf1 Last"] / rows["Sf1 Last"] > rows["RollingRatio"] + ( 1.5 * rows["RollingSTD"] ) ) and ( pos == False ) and ( rows["Gold Expiry Days"] ) >= 5:
                #print "Going Long Silver"
                #print rows["Date"]
                #print "Contract expires in  " + str(rows["Gold Expiry Days"])
                #print "Gold Price at Short is " + str(rows["Gf1 Last"]) + " Silver Price at Long is " + str(rows["Sf1 Last"])
                pos = True
                Slong = True
                lPg = rows["Gf1 Last"]
                lPs = rows["Sf1 Last"]
            elif ( rows["Gf1 Last"] / rows["Sf1 Last"] < rows["RollingRatio"] - ( 1.5 * rows["RollingSTD"] ) ) and ( pos == False ) and ( rows["Gold Expiry Days"] ) >= 5:
                #print "Going Long Gold"
                #print rows["Date"]
                #print "Contract expires in  " + str(rows["Gold Expiry Days"])
                #print "Gold Price at Long is " + str(rows["Gf1 Last"]) + " Silver Price at Short is " + str(rows["Sf1 Last"])
                pos = True
                Glong = True
                lPg = rows["Gf1 Last"]
                lPs = rows["Sf1 Last"]
        s = pd.DataFrame(returns)
        k = 0
        for i in returns:
            k = k + i
        values.append(k)
        std.append()
        mean.append()
        print "Total log returns are " + str(k)
        print "\n"
        #s["Date"] = date
        #print ratio
        #print money
        #s.plot("Date", 0)
        #df["RollingRatio"].plot()
        #plt.interactive(True)
        #plt.show()