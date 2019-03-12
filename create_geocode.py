from geopy.geocoders import ArcGIS

addressList = []
with open("Rental place address.txt", "r") as file:
    for line in file:
        addressList.append(line.replace("\n", ""))

nom = ArcGIS()
with open("Rental place coordinates.txt", "a") as file:
    for house in addressList[985:]:
        location = nom.geocode(house)
        file.write(str(location.latitude) + "," + str(location.longitude) + "\n")
        print([location.latitude, location.longitude])
        # sleep(random.randint(2, 4))