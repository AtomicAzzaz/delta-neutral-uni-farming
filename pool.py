from tracemalloc import start
import numpy as np
import matplotlib.pyplot as plt

import time
from bot import *
import numpy as np
import matplotlib.pyplot as plt
import requests
def getPriceHistorical(start, end, interval):

    url =  "https://fapi.binance.com"
    prices = []
    start = start * 1000
    end = end * 1000
    start, end = str(start), str(end)

    payload = {'symbol': 'AVAXUSDT', 'interval': interval ,  'startTime': start, 'endTime' : end, 'limit': 1500}
    data = requests.get(url + "/fapi/v1/markPriceKlines", params=payload)
    json1 = data.json()
    for x in json1:
        prices.append(float(x[1]))


    return prices

class Portfolio:

    def __init__(self, prices, initPrice=35000, initBTCinPool=1, dailyVol=0.065, fundingRateStep=0.0001, makerFees=0.0002, APRstep=0.0008):

        # self.prices = prices         FOR BINANE HISTORICAL PRICE
        # self.ind = 0
        # self.price = self.prices[0]
        # initPrice = self.price

        self.price = initPrice     # FOR SIMULATION     

        self.dailyVol = dailyVol

        self.stepFundingRate = fundingRateStep
        self.makerFees = makerFees

        self.initialInvest = initBTCinPool * initPrice
        self.stepPoolReturn = APRstep
        self.k = initPrice * initBTCinPool * initBTCinPool
        self.BTCinPool = initBTCinPool

        self.totalOpenShortAmount = 0 #everything is relative +/-
        self.totalFundingFees = 0
        self.totalShortPNL = 0
        self.totalShortingFees = 0
        self.averageOpenPrice = 0
        self.totalPoolFees = 0

    def updateShortPosition(self):
        self.modifyShort(self.price, self.BTCinPool - self.totalOpenShortAmount)


    def modifyShort(self, price, amount):
        if amount > 0:
             self.openShort(price, amount)
        elif amount < 0:
             self.closeShort(price, amount)

    def openShort(self, openPrice, amount):
        amount = np.abs(amount)
        self.totalShortingFees +=  - openPrice * amount * self.makerFees
        self.averageOpenPrice = (self.totalOpenShortAmount * self.averageOpenPrice + openPrice * amount) / (self.totalOpenShortAmount + amount)
        self.totalOpenShortAmount = (self.totalOpenShortAmount + amount)

    def closeShort(self, closePrice, amount): 

        amount = np.abs(amount)
        assert amount <= self.totalOpenShortAmount
        self.totalShortPNL += -(closePrice - self.averageOpenPrice) * amount
        self.totalShortingFees +=  - closePrice * amount * self.makerFees
        self.totalOpenShortAmount -= amount


    def totalPoolAmount(self):
        return self.BTCinPool * self.price * 2
    
    def timeStep(self):
        self.newPrice()
        self.updatePoolPosition()
        self.earnStepFunding()
        self.earnPoolFees()


    def earnPoolFees(self):
        self.totalPoolFees += self.totalPoolAmount() * self.stepPoolReturn

    def earnStepFunding(self):
        #DEPENDS ON THE SPAN OF THE STEP. HERE IN DAYS
        self.totalFundingFees += self.totalOpenShortAmount * self.averageOpenPrice * self.stepFundingRate 


    def updatePoolPosition(self):
        self.BTCinPool = np.sqrt(self.k/self.price)
    
    def newPrice(self):

        # self.price = getPrice()
        # return self.price
        # self.ind += 1           FOR BINANCE SIMULATION
        # self.price = self.prices[self.ind]
        # return self.price

        newPrice = self.price * (1 + np.random.normal(0, self.dailyVol))  #  FOR SIMULATION
        self.price = newPrice
        return newPrice

    def simulation(self, nbStep, optimEach, plot=True):

        times = [i for i in range(nbStep)]
        prices = []
        shortPNL = []
        fundingFees = []
        shortingFees = []
        poolMoney = []
        poolFees = []
        impermanentLoss = []

        for i in times:

            if (i%optimEach == 0):
                # self.modifyShort(self.price, -self.totalOpenShortAmount)
                # self.modifyShort(self.price, self.BTCinPool)

                self.updateShortPosition()

            prices.append(self.price)
            shortPNL.append(self.totalShortPNL/(2*self.k))
            fundingFees.append(self.totalFundingFees/(2*self.k))
            shortingFees.append(self.totalShortingFees/(2*self.k))
            poolMoney.append(self.totalPoolAmount()/(2*self.k) - 1)
            poolFees.append(self.totalPoolFees/(2*self.k))
            impermanentLoss.append(self.totalPoolAmount()/((prices[0]+self.price) * self.k / prices[0]) - 1)


            self.timeStep()


        self.modifyShort(self.price, -self.totalOpenShortAmount)

        times.append(nbStep)
        poolMoney.append(self.totalPoolAmount()/(2*self.k) - 1)
        prices.append(self.price)
        shortPNL.append(self.totalShortPNL/(2*self.k))
        fundingFees.append(self.totalFundingFees/(2*self.k))
        shortingFees.append(self.totalShortingFees/(2*self.k))
        poolFees.append(self.totalPoolFees/(2*self.k))
        impermanentLoss.append(self.totalPoolAmount()/((prices[0]+self.price) * self.k / prices[0]) - 1)

        totalGain = [sum(x) for x in zip(shortPNL, fundingFees, shortingFees, poolMoney, poolFees)]

        if plot:
            self.plot(times, poolMoney, prices, shortPNL, fundingFees, shortingFees, poolFees, impermanentLoss, nbStep, totalGain)

        return totalGain

    def plot(self, times, poolMoney, prices, shortPNL, fundingFees, shortingFees, poolFees, impermanentLoss, nbStep, totalGain):
      
        fig, axs = plt.subplots(2, 2)

        axs[0, 0].plot(times, prices, color = 'black')
        axs[0, 0].set_title('Price of BTC')

        ax2 = axs[0, 0].twinx()
        ax2.plot(times, impermanentLoss, color = 'pink', label='IL')
        ax2.legend()
 

        if shortPNL[-1] < 0:
            colorPNL = "red"
        else:
            colorPNL = 'green'

        if poolMoney[-1] < 0:
            colorPool = "red"
        else:
            colorPool = 'green'

        if fundingFees[-1] < 0:
            colorFunding = "lightcoral"
        else:
            colorFunding = 'palegreen'

        axs[1, 0].plot(times, shortPNL, color = colorPNL, label='Short PNL')
        axs[1, 0].plot(times, poolMoney, color = colorPool, label = 'Pool money')
        axs[1, 0].plot(times, [sum(x) for x in zip(shortPNL, poolMoney,)], color = 'lightblue', label='Sum: '+ str(round((shortPNL[-1] + poolMoney[-1])*100, 1)) + '%')
        axs[1, 0].set_title('Major Gains / Losses')
        axs[1, 0].legend()

        axs[1, 1].plot(times, poolFees, color = 'gold', label='poolFees')
        axs[1, 1].plot(times, [self.stepPoolReturn*k for k in range(0, nbStep + 1)], color = 'black', label='nominalAPR')
        axs[1, 1].plot(times, fundingFees, color = colorFunding, label = 'fundingFees')
        axs[1, 1].plot(times, shortingFees, color = 'red', label = 'shortingFees')
        axs[1, 1].plot(times, [sum(x) for x in zip(shortingFees, fundingFees,poolFees)], color = 'lightblue', label='Sum: '+ str(round((shortingFees[-1] + fundingFees[-1] + poolFees[-1])*100, 1)) + '%')
        axs[1, 1].set_title('Fees')
        axs[1, 1].legend()
        
        axs[0, 1].plot(times, totalGain, color = 'gold')
        axs[0, 1].set_title('Total ROI: '+ str(round(totalGain[-1]*100, 1)) + '%')
        plt.tight_layout(pad=1)
        plt.show()

    def bot(self, optimEachInS=24*3600):
        
        times = []
        prices = []
        shortPNL = []
        fundingFees = []
        shortingFees = []
        poolMoney = []
        poolFees = []
        impermanentLoss = []

        while True:
            closeAllOpenOrders()
            self.price = getPrice()
            print(self.BTCinPool ,self.totalOpenShortAmount)
            self.updatePoolPosition()
            amount = self.BTCinPool - self.totalOpenShortAmount
            

            if amount > 3:
                myPrice = round(float(self.price )*1.001, 4)
                openShortLimit(myPrice, int(amount))
            elif amount < 3:
            
                myPrice = round(float(self.price)*0.999, 4)
                openShortLimit(myPrice, int(amount))
            time.sleep(200)

            while getOpenOrdersAmount() != 0:
                closeAllOpenOrders()
                self.price = getPrice()
                self.updatePoolPosition()
                amount = self.BTCinPool - self.totalOpenShortAmount
                rounded_amount = round(amount, 4)
                if amount > 3:
                    myPrice = round(float(self.price)*1.001, 4)
                    openShortLimit(myPrice, int(amount))
                elif amount < 3:
                    myPrice = round(float(self.price )*0.999, 4)
                    openShortLimit(myPrice, int(amount))
                time.sleep(200)

            self.price = myPrice
            self.updateShortPosition()

            prices.append(self.price)
            shortPNL.append(self.totalShortPNL/self.initialInvest)
            fundingFees.append(self.totalFundingFees/self.initialInvest)
            shortingFees.append(self.totalShortingFees/self.initialInvest)
            poolMoney.append(self.totalPoolAmount()/self.initialInvest - 1)
            poolFees.append(self.totalPoolFees/self.initialInvest)
            impermanentLoss.append(self.totalPoolAmount()/((prices[0]+self.price) * self.k / prices[0]) - 1)


            
            print("-------------UPDATED----------")
            print("ROI: ", shortPNL[-1] + fundingFees[-1] + shortingFees[-1], poolMoney[-1], poolFees[-1])
            print("shortPNL", shortPNL[-1])
            print("fundingFees", fundingFees[-1])
            print("shortingFees", shortingFees[-1])
            print("poolMoney", poolMoney[-1])
            print("poolFees", poolFees[-1])
            time.sleep(optimEachInS)
            self.earnStepFunding()
            self.earnPoolFees()





# start = 1641073359
# end = 1646170959
# prices = getPrice(start, end, "1d")


# n = len(prices) - 1
# k = 1
# pf = Portfolio(prices, fundingRateStep=0.036/(365*k), APRstep=0.3/(365*k))
# pf.simulation(n, 1)

pf = Portfolio([], fundingRateStep=0.036/(365), APRstep=0.3/(365))
pf.simulation(365, 1)


# initPrice = getPrice()
# pf = Portfolio([], initPrice, initBTCinPool=10, fundingRateStep=0.0002, APRstep = 0.0008)
# pf.bot()