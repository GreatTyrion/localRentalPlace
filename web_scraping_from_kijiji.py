import requests
from bs4 import BeautifulSoup
from datetime import datetime

def getURL(num):
    if num == 1:
        url = "https://www.kijiji.ca/b-real-estate/st-johns/rent/k0c34l1700113"
    else:
        url = "https://www.kijiji.ca/b-real-estate/st-johns/rent/page-" + str(num) + "/k0c34l1700113"
    return  url

addressList = []
priceList = []
hrefList = []
roomNumber = []
titleList = []

t1 = datetime.now()
for num in range(1, 48):
    print(num)
    realEstateWeb = requests.get(getURL(num))
    webContent = realEstateWeb.content
    soup = BeautifulSoup(webContent, "html.parser")

    rentHouses = soup.find_all("div", {"class": "search-item"})

    for item in rentHouses:
        itemURL = "https://www.kijiji.ca" + item.get("data-vip-url")
        itemWeb = requests.get(itemURL)
        itemContent = itemWeb.content
        itemSoup = BeautifulSoup(itemContent, "html.parser")

        try:
            addressList.append(itemSoup.find("span", {"class", "address-3617944557"}).text)
            hrefList.append(itemURL)
        except:
            continue

        try:

            information = itemSoup.find_all(("dd", {"class", "attributeValue-2574930263"}))
            label = itemSoup.find_all(("dt", {"class", "attributeLabel-240934283"}))
            info = ""
            for item1, item2 in zip(information, label):
                info = info + item2.text + ": " + item1.text + " *** "
            roomNumber.append(info)
        except:
            roomNumber.append("Not given")

        try:
            priceList.append(itemSoup.find("span", {"class", "currentPrice-441857624"}).text)
        except:
            priceList.append("Not available")

        try:
            titleList.append(itemSoup.find("h1", {"class", "title-2323565163"}).text)
        except:
            titleList.append("No title")

# print(addressList)
# print(hrefList)
print(len(priceList))
print(datetime.now() - t1)
# print(roomNumber)

with open("Rental place address.txt", "w") as CC:
    for house in addressList:
        CC.write(house + "\n")

with open("Rental place href.txt", "w") as CC:
    for href in hrefList:
        CC.write(href + "\n")

with open("Rental place price.txt", "w") as CC:
    for price in priceList:
        CC.write(price + "\n")

with open("Room numbers.txt", "w") as CC:
    for item in roomNumber:
        CC.write(item + "\n")

with open("Post title.txt", "w") as CC:
    for item in titleList:
        CC.write(item + "\n")
