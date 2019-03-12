import folium
from geopy.geocoders import ArcGIS
from folium.plugins import MarkerCluster
import pandas as pd

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
#print(df2)
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

for i in range(len(houseLocation)):
    iframe = folium.IFrame(html=html % (titleList[i], priceList[i], roomNumber[i], hrefList[i]), width=300, height=270)
    folium.Marker(location=houseLocation[i], popup=folium.Popup(iframe),
                               icon=folium.Icon(color_selector(priceList[i]))).add_to(marker_cluster)

#map.add_child(folium.LayerControl())
map.save("Rental places in St.John's.html")
