from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re

#%%funcs
# find numbers in text and convert to float 
def findDigit(stringInput):
    emp_str = ""
    for m in stringInput:
        if m.isdigit():
            emp_str = emp_str+m
    return float(emp_str)


#%% build-up
parariUrl = 'https://www.pararius.com/apartments/amsterdam'
pariLink = 'https://www.pararius.com'
parari = requests.get(parariUrl)
parariSoup = BeautifulSoup(parari.text,'html.parser')

#get total house number in order to get page count
parariPageCount = parariSoup.find_all("div",{'class':'search-list-header__title'})[0].get_text().split()[0]
parariPageCount = int(parariPageCount)
pageMaxCount = 30 # max 30 advertisement in 1 page
totalPage = int((parariPageCount/pageMaxCount)+1)
#derive links based on pageCpunt
linkList = []
for i in range(totalPage):
    pageLink=parariUrl+'/page-'+str(i+1)
    linkList.append(pageLink)

#%%
parariDf = pd.DataFrame()

for pageLink in linkList:
    
    linkReq = requests.get(pageLink)
    linkSoup = BeautifulSoup(linkReq.text,'html.parser')
    parariList = linkSoup.find_all("ul",{'class':'search-list'})
    
    #list to fill
    priceList = []
    po1List = []
    po2List = []
    neighbourhoodList = []
    areaList=[]
    roomsList=[]
    interiorList=[]
    realEstateAgentList = []
    titleList=[]
    linkList = []
    idList = []
    homeStatusList = []
    statusList = []
    availabiltyList = []
    offeredSinceList = []
    energyList = []
    
    for p in parariList:
        
        items = p.find_all("li",{'class':'search-list__item search-list__item--listing'})
        
        for i in items:
    
            itemLabel = i.find_all("div",{'class':'listing-search-item__label'})
            if len(itemLabel) !=0:
                homeStatus = i.find_all("div",{'class':'listing-search-item__label'})[0].get_text().strip()
            else:
                homeStatus = 'NA'
    
            interior = i.find_all("li",{'class':'illustrated-features__item illustrated-features__item--interior'})
            if len(interior) != 0:
                interior = interior[0].get_text()
            else:
                interior = 'NA'            
    
            price = i.find_all("div",{'class':'listing-search-item__price'})
            price = price[0].get_text().strip()
            price = findDigit(price)
            
            po1 = i.find_all("div",{'class':'listing-search-item__sub-title'})[0].get_text().strip().split()[0]
            po2 = i.find_all("div",{'class':'listing-search-item__sub-title'})[0].get_text().strip().split()[1]
            
            neighbourhood = i.find_all("div",{'class':'listing-search-item__sub-title'})[0].get_text().strip().split('(')[1].replace(")","")
            
            area = i.find_all("li",{'class':'illustrated-features__item illustrated-features__item--surface-area'})[0].get_text()
            area = int(area.split()[0])
            
            rooms = i.find_all("li",{'class':'illustrated-features__item illustrated-features__item--number-of-rooms'})[0].get_text()
            rooms = int(rooms.split()[0])
     
            realEstate = i.find_all("div",{'class':'listing-search-item__info'})[0].get_text().strip()
            title = i.find_all("a",{'class':'listing-search-item__link listing-search-item__link--title'})[0].get_text().strip()
            link = i.find_all("a",{'class':'listing-search-item__link listing-search-item__link--title'})[0].get('href')
            hid = link.split('/')[3]
            link = pariLink+link
            
            houseReq = requests.get(link)
            houseSoup = BeautifulSoup(houseReq.text,'html.parser')
            
            features = houseSoup.find_all("div",{'class':'listing-features'})
            
            available= features[0].find_all("dd",{'listing-features__description listing-features__description--acceptance'})[0].get_text()
            
            #TODO
            #availableReg = re.compile(r'\d\d-\d\d-\d\d\d\d')
            #availablex = availableReg.search(available).group()

            offered_since= features[0].find_all("dd",{'listing-features__description listing-features__description--offered_since'})[0].get_text()
            status = features[0].find_all("dd",{'listing-features__description listing-features__description--status'})[0].get_text()
            
            try:    
                energy = features[5].find_all("dd",{'class': re.compile(r'energy')})[0].get_text().strip()
            except:
                energy = 'Not Available'
            
            
            #storage
            idList.append(hid)
            titleList.append(title)
            homeStatusList.append(homeStatus)
            priceList.append(price)
            po1List.append(po1)
            po2List.append(po2)
            neighbourhoodList.append(neighbourhood)
            areaList.append(area)
            roomsList.append(rooms)
            interiorList.append(interior)
            realEstateAgentList.append(realEstate)
            linkList.append(link)
            offeredSinceList.append(offered_since)
            availabiltyList.append(available)
            statusList.append(status)
            energyList.append(energy)
    
            #check length for every list
            
        houseDict = {'id':idList,
                     'header':titleList,
                     'offeredSince':offeredSinceList,
                     'availabilty':availabiltyList,
                     'status':homeStatusList,
                     'statusNew':statusList,
                     'price':priceList,
                     'postCode1':po1List,
                     'postCode2':po2List,
                     'neighbourhood':neighbourhoodList,
                     'areaM2':areaList,
                     'rooms':roomsList,
                     'interior':interiorList,
                     'energy':energyList,
                     'agent':realEstateAgentList,
                     'link':linkList}
    
        houseDf = pd.DataFrame(houseDict)
        parariDf = parariDf.append(houseDf)
        

#%%
#highlighted houses duplicates in the list, since we have ids we can remove them
parariDf = parariDf.drop_duplicates()
parariDf['scrapDate'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
saveTag = str(datetime.now()).replace('-','_').replace(':','_').replace('.','_').replace(' ','__')
localPath = "D:/github/pariScrap/data/"
fileName = localPath+saveTag+".csv"
parariDf.to_csv(fileName)

#%%filter df
postCodeList = [1072,1073,1074,
                1071,1078,1091,
                1092,1093,
                1097,1098] 

priceFilter = 3000
roomFilter = 2
m2Filter = 70
dateFilter = datetime.today() - timedelta(days=7)
statusAvailabilityFilter = ['In consultation','Rented under option','Under offer','Under option']



parariDf['availabilty'] = parariDf['availabilty'].apply(lambda x: x.strip())
parariDf['status'] = parariDf['status'].apply(lambda x: x.strip())
parariDf["postCode1"] = parariDf["postCode1"].astype(int)
parariDf['offeredSince2'] = parariDf['offeredSince'].apply(lambda x: pd.to_datetime(x) if ('2022' in x or '2023' in x) else np.nan)



fParariDf = parariDf[parariDf["postCode1"].isin(postCodeList)]
fParariDf = fParariDf[fParariDf["price"]<=priceFilter]
fParariDf = fParariDf[fParariDf["rooms"]>roomFilter]
fParariDf = fParariDf[fParariDf["areaM2"]>m2Filter]
fParariDf = fParariDf[fParariDf['offeredSince2']>dateFilter]
fParariDf = fParariDf[~fParariDf['availabilty'].isin(statusAvailabilityFilter)]
fParariDf = fParariDf[~fParariDf['status'].isin(statusAvailabilityFilter)]

#%%


