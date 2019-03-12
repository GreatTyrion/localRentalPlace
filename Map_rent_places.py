import folium
from geopy.geocoders import ArcGIS
from folium.plugins import MarkerCluster
import pandas as pd
from time import sleep
import random

houseLocation = []
priceList = []
hrefList = []
roomNumber = []
titleList = []

with open("Rental place coordinates.txt", "r") as file:
    for line in file:
        string = line.replace("\n", "")
        houseLocation.append([float(string.split(",")[0]), float(string.split(",")[1])])

with open("Rental place href.txt", "r") as file:
    for line in file:
        hrefList.append(line.replace("\n", ""))

with open("Rental place price.txt", "r") as file:
    for line in file:
        priceList.append(line.replace("\n", ""))

with open("Room numbers.txt", "r") as file:
    for line in file:
        roomNumber.append(line.replace("\n", ""))

with open("Post title.txt", "r") as file:
    for line in file:
        titleList.append(line.replace("\n", ""))

df = pd.DataFrame({
    "houseLocation": houseLocation,
    "priceList": priceList,
    "hrefList": hrefList,
    "roomNumber": roomNumber,
    "titleList": titleList
})

df2 = df.drop_duplicates("hrefList")
print(df2)
houseLocation = list(df2.houseLocation)
priceList = list(df2.priceList)
hrefList = list(df2.hrefList)
roomNumber = list(df2.roomNumber)
titleList = list(df2.titleList)

html = """
%s<br>
######################<br>
Price: %s<br>
######################<br>
%s<br>
######################<br>
<a href="%s" target="_blank">Link to Kijiji</a>
"""

def color_selector(price):
    try:
        price = float(price.replace("$", "").replace(",", ""))
        if price < 600:
            return "green"
        elif 600 <= price < 1000:
            return "orange"
        else:
            return "red"
    except:
        return "blue"

map = folium.Map(location=[47.5669, -52.7067], zoom_start=13)

marker_cluster = MarkerCluster().add_to(map)

fg1 = folium.FeatureGroup(name="Rental places from KiJiJi updated on 3/7/2019")
for i in range(len(houseLocation)):
    iframe = folium.IFrame(html=html % (titleList[i], priceList[i], roomNumber[i], hrefList[i]), width=300, height=270)
    folium.Marker(location=houseLocation[i], popup=folium.Popup(iframe),
                               icon=folium.Icon(color_selector(priceList[i]))).add_to(marker_cluster)



html2 = """
Price: %s<br>
Available room: %s<br>
Information: %s<br>
Contact: %s
"""

fromPeople = [["28 penney cres, a1a 5h2", "$400.00", "1 bedroom", "Parking space available, short-term rent available", "(709)743-6256"],
              ["23 Guy St, St. John's, NL A1B 1P7", "$450.00", "2 bedrooms", "Each is 450 POU", "(709)237-8118, (WeChat)Candy_wen1368"]]
nom = ArcGIS()
houseLocation2 = []

for house in fromPeople:
    location = nom.geocode(house[0])
    houseLocation2.append([location.latitude, location.longitude])
    print([location.latitude, location.longitude])

fg2 = folium.FeatureGroup(name="Updated by Hongyuan on 3/12/2019")
for i in range(len(fromPeople)):
    iframe = folium.IFrame(html=html2 % (fromPeople[i][1], fromPeople[i][2], fromPeople[i][3], fromPeople[i][4]), width=300, height=150)
    folium.Marker(location=houseLocation2[i], popup=folium.Popup(iframe),
                               icon=folium.Icon(color_selector(fromPeople[i][1]))).add_to(marker_cluster)
# map.add_child(fg1)
map.add_child(fg2)
map.add_child(folium.LayerControl())
map.save("Rental places in St.John's.html")
