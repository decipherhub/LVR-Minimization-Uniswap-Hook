"""
@author: The-CTra1n
"""
import pandas as pd
import math
import random
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv

load_dotenv()

def vaultFuturesStrategy(r0,r1,price,netVault0,netVault1,block,kStart,activeFuturePositions,conversionFrequency,alpha):
    
    r0new=math.sqrt(price*r0*r1)
    r1new=r0new/price
    
    vault0,vault1=0,0
    """(r1-r1new)>0 means the token 1 has increased in value"""
    if (r1-r1new)>0:

        vault1=vault1+(r1-r1new)*(alpha)
        """repay the arbitrageur"""
        r0=r0new+(r0-r0new)*(alpha)
        """rebalance the pool"""
        r1=r0/price
        vault1=vault1+(r1new-r1)
    else:
        vault0=vault0+(r0-r0new)*(alpha)
        """repay the arbitrageur"""
        r1=r1new+(r1-r1new)*(alpha)
        r0=r1*price
        vault0=vault0+(r0new-r0)
    """settles (1/conversionFrequency) of the active futures contracts"""
    if block % conversionFrequency==0:
        for i in range(0,conversionFrequency):
            valueToBeAdded=activeFuturePositions[i][0]*(price-activeFuturePositions[i][1])
            r0ValueAdd=(valueToBeAdded/2)
            r1ValueAdd=(valueToBeAdded/2)/price
            r0=r0+r0ValueAdd
            r1=r1+r1ValueAdd
        kStart=r0*r1
    if vault0<vault1*price:
        """ this implies price has gone up """
        """apply rebalancing fee to the amount needed to be rebalance, in token1 s"""
        vault1Additional=(vault1-(vault0/price))
        """creates a buy futures contract against the block producer"""
        activeFuturePositions[sim%conversionFrequency]=[vault1Additional/2,price]
        vault0=vault0+(vault1Additional/2)*price
        vault1=(vault1-vault1Additional/2)
        r0=r0+(vault0)
        r1=r1+(vault1)
        newK=r0*r1
        kOverNewK=math.sqrt(kStart/newK)
        netVault0=netVault0+r0*(1-kOverNewK)
        netVault1=netVault1+r1*(1-kOverNewK)
        """Keep the constant constant between blocks"""
        r0=r0*kOverNewK
        r1=r1*kOverNewK
        vault0=0
        vault1=0
    else:
        """ this implies price has gone down """
        """apply rebalancing fee to the amount needed to be rebalance"""
        vault0Additional=(vault0-vault1*price)
        """creates a sell futures contract against the block producer (minus sign) """
        activeFuturePositions[sim%conversionFrequency]=[-(vault0Additional/2)/price,price]
        vault1=vault1+(vault0Additional/2)/price
        vault0=(vault0-vault0Additional/2)
        r0=r0+(vault0)
        r1=r1+(vault1)
        newK=r0*r1
        kOverNewK=math.sqrt(kStart/newK)
        netVault0=netVault0+r0*(1-kOverNewK)
        netVault1=netVault1+r1*(1-kOverNewK)
        """Keep the constant constant between blocks"""
        r0=r0*kOverNewK
        r1=r1*kOverNewK
    return r0,r1,netVault0,netVault1,kStart,activeFuturePositions

def vaultLazyConversionStrategy(r0,r1,price,vault0,vault1,block,conversionFrequency,alpha):
    r0new=math.sqrt(price*r0*r1)
    r1new=r0new/price
    """"(r1-r1new)>0 means the token 1 has increased in value"""
    if (r1-r1new)>0:
        vault1=vault1+(r1-r1new)*(alpha)
        """"repay the arbitrageur"""
        r0=r0new+(r0-r0new)*(alpha)
        """"rebalance the pool"""
        r1=r0/price
        vault1=vault1+(r1new-r1)
        
    else:
        vault0=vault0+(r0-r0new)*(alpha)

        """"repay the arbitrageur"""
        r1=r1new+(r1-r1new)*(alpha)
        r0=r1*price
        vault0=vault0+(r0new-r0)
        
        
    """performs the conversion every conversionFrequency"""
    if block % conversionFrequency==0:
        if vault0<vault1*price:
            
            """ this implies price has gone up """
            vault1Additional=(vault1-(vault0/price))
            vault0=vault0+(vault1Additional/2)*price
            vault1=(vault1-vault1Additional/2)
            r0=r0+(vault0)
            r1=r1+(vault1)
            vault0=0
            vault1=0
        else:
            """ this implies price has gone down """
            """apply rebalancing fee to the amount needed to be rebalance"""
            vault0Additional=(vault0-vault1*price)
            vault1=vault1+(vault0Additional/2)/price
            vault0=(vault0-vault0Additional/2)
            r0=r0+(vault0)
            r1=r1+(vault1)
            vault0=0
            vault1=0
    return r0,r1,vault0,vault1

def vaultLowImpactReAdding(r0,r1,price,vault0,vault1,pctToReAdd,alpha):
    r0min=r0*pctToReAdd**2
    r1min=r1*pctToReAdd**2
    r0new=math.sqrt(price*r0*r1)
    r1new=r0new/price
    """"(r1-r1new)>0 means the token 1 has increased in value"""
    if (r1-r1new)>0:
        vault1=vault1+(r1-r1new)*(alpha)
        """"repay the arbitrageur"""
        r0=r0new+(r0-r0new)*(alpha)
        """"rebalance the pool"""
        r1=r0/price
        """now r1 is the amount supposed to be in the pool GIVEN the updated r0"""
        """r1new is the amount actually there, and >r1"""
        """This difference goes into the vault"""
        vault1=vault1+(r1new-r1)
        
    else:
        vault0=vault0+(r0-r0new)*(alpha)

        """"repay the arbitrageur"""
        r1=r1new+(r1-r1new)*(alpha)
        r0=r1*price
        vault0=vault0+(r0new-r0)
        
        
    """performs the conversion every conversionFrequency"""
    if True:
        if vault0<vault1*price:
            
            """ this implies price has gone up """
            vault1Additional=(vault1-(vault0/price))
            r0=r0+(vault0)
            r1=r1+(vault0/price)
            vault0=0
            
            """This max ensures the vault tends to 0. The min ensures the amount added is in the vault"""
            amountToReAdd=max(vault1Additional*pctToReAdd,min(vault1Additional,r1min))
            r1=r1+amountToReAdd
            vault1=(vault1Additional-amountToReAdd)
            
        else:
            """ this implies price has gone down """
            """apply rebalancing fee to the amount needed to be rebalance"""
            vault0Additional=(vault0-vault1*price)
            r1=r1+(vault1)
            r0=r0+vault1*price
            vault1=0

            amountToReAdd=max(vault0Additional*pctToReAdd,min(vault0Additional,r0min))
            r0=r0+amountToReAdd
            vault0=(vault0Additional-amountToReAdd)
    return r0,r1,vault0,vault1



def addTXFees(r0,r1,transactionFee):
    return r0*(1+transactionFee),r1*(1+transactionFee)



numBlocksPerDay=10
numberOfSimsPerCombination=500

r0start=150000000
r1start=81336
numDaysSimulation=180
alpha=0.95

blocksForSim=numBlocksPerDay*numDaysSimulation
conversionFrequency=numBlocksPerDay
conversionFrequencyFut=numBlocksPerDay

"""dailyFeesVsK=0.0003 is equiv to 10% TVL trading in a 0.3% fee pool"""
dailyFeesVsK=0



firstSet=[i for i in range(0,numberOfSimsPerCombination)]
secondSet=[i for i in range(numberOfSimsPerCombination,2*numberOfSimsPerCombination)]
thirdSet=[i for i in range(2*numberOfSimsPerCombination,3*numberOfSimsPerCombination)]
fourthSet=[i for i in range(3*numberOfSimsPerCombination,4*numberOfSimsPerCombination)]

results=pd.DataFrame(data={"dailyExpectedVol":[],
                           "alpha":[],
                           "vaultLazyConvert":[],
                           "vaultFutures":[],
                           "AMM":[],
                           "HODL":[],
                           "finalPrice":[]})





for dailyExpectedVol in [1.05]:
    for pctToReAdd in [0.01,0.05,0.125]:
        blocksForSim=numBlocksPerDay*numDaysSimulation
        for sim in range(0,numberOfSimsPerCombination):
            price=r0start/r1start
            
            

            """Low Impact Strategy Variables"""
            r0Low=r0start
            r1Low=r1start
            vault0Low=0
            vault1Low=0  
            
            activeFuturePositions=[[0,0] for i in range(0,conversionFrequency)]
            for block in range(0,blocksForSim):
                """ **(2*random.random()) introduces a vol of vol"""
                perBlockVol=1+((1-dailyExpectedVol)/math.sqrt(numBlocksPerDay))
                if random.random()>0.5:
                    price=price*(perBlockVol)
                else:
                    price = price*(1-(perBlockVol-1)) 
                r0Low,r1Low,vault0Low,vault1Low=vaultLowImpactReAdding(r0Low,r1Low,price,vault0Low,vault1Low,pctToReAdd,alpha)
                r0Low,r1Low=addTXFees(r0Low,r1Low,dailyFeesVsK/numBlocksPerDay)
    
            
            vaultStrategyValueLow=(r1Low+vault1Low)*price + r0Low+vault0Low
            
            results=pd.concat([results,pd.DataFrame({"dailyExpectedVol":dailyExpectedVol,
                                       "alpha":alpha,
                                       "finalPrice": price,
                                       "vaultLowImpact":vaultStrategyValueLow,
                                       "vaultLazyConvert":0,
                                       "vaultFutures":0,
                                       "AMM":(math.sqrt(r0start*r1start*price)+math.sqrt(r0start*r1start/price)*price)*(1+dailyFeesVsK/numBlocksPerDay)**numberOfSimsPerCombination,
                                       "HODL":r0start+r1start*price},index=[0])],ignore_index=True)




results["vaultLowImpact"]=results["vaultLowImpact"]/results["AMM"]
plt.figure(0)
plt.scatter(x=results["finalPrice"].loc[firstSet].values.tolist(),y=results["vaultLowImpact"].loc[firstSet].values.tolist(),c="magenta",label="0.01")
plt.scatter(x=results["finalPrice"].loc[secondSet].values.tolist(),y=results["vaultLowImpact"].loc[secondSet].values.tolist(),c="orange",label=" 0.05")
plt.scatter(x=results["finalPrice"].loc[thirdSet].values.tolist(),y=results["vaultLowImpact"].loc[thirdSet].values.tolist(),c="green",label="0.125")
#plt.scatter(x=results["finalPrice"].loc[fourthSet].values.tolist(),y=results["vaultLowImpact"].loc[fourthSet].values.tolist(),c="blue",label="0.5")


plt.legend(loc="upper left")
plt.title("% ReAdd from Vault")
plt.ylabel("Low Impact ReAdd / CFMM")
plt.xlabel("final price")


path=os.getenv("PATH_TO_PNGS")
plt.savefig(path + 'ReAddPercentages.png',dpi=500)



print("0.01",results["vaultLowImpact"].loc[firstSet].describe())
print("0.05",results["vaultLowImpact"].loc[secondSet].describe())
print("0.125",results["vaultLowImpact"].loc[thirdSet].describe())
#print("0.5",results["vaultLowImpact"].loc[fourthSet].describe())

results=pd.DataFrame(data={"dailyExpectedVol":[],
                           "alpha":[],
                           "vaultLazyConvert":[],
                           "vaultFutures":[],
                           "AMM":[],
                           "HODL":[],
                           "finalPrice":[]})


for dailyExpectedVol in [1.05]:
    for pctToReAdd in [0.01]:
        blocksForSim=numBlocksPerDay*numDaysSimulation
        for sim in range(0,numberOfSimsPerCombination):
            price=r0start/r1start
            
            """Futures Strategy Variables"""
            netVault0Futs=0
            netVault1Futs=0
            slippageFut=0
            r0Futs=r0start
            r1Futs=r1start
            kStartFuts=r0Futs*r1Futs
            
            """Lazy Conversion Strategy Variables"""
            r0Lazy=r0start
            r1Lazy=r1start
            slippageLazy=0
            vault0Lazy=0
            vault1Lazy=0  

            """Low Impact Strategy Variables"""
            r0Low=r0start
            r1Low=r1start
            slippageLow=0
            vault0Low=0
            vault1Low=0  
            
            activeFuturePositions=[[0,0] for i in range(0,conversionFrequency)]
            activeFuturePositionsFut=[[0,0] for i in range(0,conversionFrequencyFut)]
            for block in range(0,blocksForSim):
                """ **(2*random.random()) introduces a vol of vol"""
                perBlockVol=1+((1-dailyExpectedVol)/math.sqrt(numBlocksPerDay))
                if random.random()>0.5:
                    price=price*(perBlockVol)
                else:
                    price = price*(1-(perBlockVol-1)) 
                r0Futs,r1Futs,netVault0Futs,netVault1Futs,kStartFuts,activeFuturePositions=vaultFuturesStrategy(r0Futs,r1Futs,price,netVault0Futs,netVault1Futs,block,kStartFuts,activeFuturePositionsFut,conversionFrequencyFut,alpha)
                r0Lazy,r1Lazy,vault0Lazy,vault1Lazy=vaultLazyConversionStrategy(r0Lazy,r1Lazy,price,vault0Lazy,vault1Lazy,block,conversionFrequency,alpha)
                r0Low,r1Low,vault0Low,vault1Low=vaultLowImpactReAdding(r0Low,r1Low,price,vault0Low,vault1Low,pctToReAdd,alpha)
                # r0Lazy,r1Lazy=addTXFees(r0Lazy,r1Lazy,dailyFeesVsK/numBlocksPerDay)
                r0Futs,r1Futs=addTXFees(r0Futs,r1Futs,dailyFeesVsK/numBlocksPerDay)
                r0Low,r1Low=addTXFees(r0Low,r1Low,dailyFeesVsK/numBlocksPerDay)

                """add TxFees"""
                # r0Lazy,r1Lazy=addTXFees(r0Lazy,r1Lazy,dailyFeesVsK/numBlocksPerDay)
                # r0Low,r1Low=addTXFees(r0Low,r1Low,dailyFeesVsK/numBlocksPerDay)
            
            vaultStrategyValueFuts=(r1Futs+netVault1Futs)*price + r0Futs+netVault0Futs
            vaultStrategyValueLazy=(r1Lazy+vault1Lazy)*price + r0Lazy+vault0Lazy
            vaultStrategyValueLow=(r1Low+vault1Low)*price + r0Low+vault0Low
            
            results=pd.concat([results,pd.DataFrame({"dailyExpectedVol":dailyExpectedVol,
                                       "alpha":alpha,
                                       "finalPrice": price,
                                       "vaultLowImpact":vaultStrategyValueLow,
                                    #    "vaultLazyConvert":vaultStrategyValueLazy,
                                       "vaultFutures":vaultStrategyValueFuts,
                                       "AMM":(math.sqrt(r0start*r1start*price)+math.sqrt(r0start*r1start/price)*price)*(1+dailyFeesVsK/numBlocksPerDay)**numberOfSimsPerCombination,
                                       "HODL":r0start+r1start*price},index=[0])],ignore_index=True)



# a=results["vaultLazyConvert"]/results["AMM"]
b=results["vaultFutures"]/results["AMM"]
c=results["HODL"]/results["AMM"]
d=results["vaultLowImpact"]/results["AMM"]



plt.figure(5)
plt.scatter(x=results["finalPrice"].loc[firstSet].values.tolist(),y=c.loc[firstSet].values.tolist(),c="orange",label="HODL")
plt.scatter(x=results["finalPrice"].loc[firstSet].values.tolist(),y=d.loc[firstSet].values.tolist(),c="blue",label="Low Impact ReAdd")
# plt.scatter(x=results["finalPrice"].loc[firstSet].values.tolist(),y=a.loc[firstSet].values.tolist(),c="magenta",label="Periodic Conversion w/ Auction")
plt.scatter(x=results["finalPrice"].loc[firstSet].values.tolist(),y=b.loc[firstSet].values.tolist(),c="magenta",label="Conversion vs. Futures")
plt.legend(loc="upper left")
plt.title("Theoretical vs. Low Impact Re-Add")
plt.ylabel("Strategy / CFMM")
plt.xlabel("final price")
 
plt.savefig(path + 'HODL.png',dpi=500)

# print("vaultLazyConvert",a.loc[firstSet].describe())
print("vaultFutures",b.loc[firstSet].describe())
print("HODL",c.loc[firstSet].describe())
print("vaultLowImpact",d.loc[firstSet].describe())