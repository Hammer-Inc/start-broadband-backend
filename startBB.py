# 1. Check if NBN is available
#       Search for a PASS on method NBN type NCAS (FTTN)
#       Search for a PASS on method NBN type NFAS (FTTP)
#       Search for a PASS on method NBN type NHAS (HFC)
#       Search for a PASS on method NBN type NWAS (Fixed Wireless)
# 2. If no NBN, Check for ADSL
#       Search for a PASS on method ADSL type SSS
# 3. If ADSL
#       Check for available ports
# 4. If ports
#       Check price zone
# 5. Else
#       No connections available


# [0] = ADSL
# [5] = NFAS
# [6] = NWAS
# [7] = NCAS
# [8] = NHAS
# [9] = NSAS (Not needed???)
import json
import csv
import numpy

class Connection(object):
    def __init__(self):
        self.connectionType = None
        body_dict = {"priceZone": None, "portsAvailability": None, "distanceToExchange": None, "expectedDate": None, "expectedDownSpeed": None}
        self.body = body_dict

    def setConnectionType(self, connectionType):
        self.connectionType = connectionType

    def setPriceZone(self, priceZone):
        self.body["priceZone"] = priceZone

    def setPortsAvailability(self, portsAvailability):
        self.body["portsAvailability"] = portsAvailability

    def setDistanceToExchange(self, distanceToExchange):
        self.body["distanceToExchange"] = distanceToExchange

    def setExpectedDate(self, expectedDate):
        self.body["expectedDate"] = expectedDate

    def setExpectedDownSpeed(self, expectedDownSpeed):
        self.body["expectedDownSpeed"] = expectedDownSpeed

    def setExpectedUpSpeed(self, expectedUpSpeed):
        self.body["expectedUpSpeed"] = expectedUpSpeed

def find(jsonObject, connectionObject):
    global containingRow

    validation = 1
    jsonText = str(jsonObject.text)
    jsonData = json.loads(jsonText)

    # nbnJsonText = str(nbnJsonObject.text)
    # nbnJsonData = json.loads(nbnJsonText)

    count = 0

    while validation:
        if jsonData["accessQualificationList"][count]["qualificationResult"]["value"] == "PASS":
            validation = 0
        else:
            count = count + 1

    connectionObject.connectionType = getType(jsonData, count)

    if connectionObject.connectionType == "ADSL2":
        exchangeCode = jsonData["siteDetails"]["exchangeCode"]
        portsCSV = csv.reader(open('ports.csv', "rb"), delimiter=",")
        for row in portsCSV:
            if exchangeCode == row[2]:
                containingRow = row

        if containingRow[4] != 0 or containingRow[5]:
            portsAvailability = True
            connectionObject.setPortsAvailability(portsAvailability)
            if portsAvailability:
                priceZone = jsonData["accessQualificationList"][count]["priceZone"]["value"]
            else:
                priceZone = "None"
            connectionObject.setPriceZone(priceZone)

        connectionObject.setDistanceToExchange(jsonData["siteDetails"]["distanceToExchange"])
        # connectionObject.setExpectedDate(nbnJsonData["servingArea"]["rfsMessage"])

        distanceCSV = csv.reader(open('distance.csv', "rb"), delimiter=",")
        xList = []
        yList = []

        for row in distanceCSV:
            xList.append(row[0])
            yList.append(row[1])
        xList.pop(0)
        yList.pop(0)
        xValue = jsonData["siteDetails"]["distanceToExchange"]
        float(xValue)

        countx = 0
        county = 0
        for value in xList:
            xList[countx] = float(value)
            countx = countx + 1
        for value in yList:
            yList[county] = float(value)
            county = county + 1
        connectionObject.setExpectedDownSpeed(str(int(round(numpy.interp(xValue, xList, yList), 0))))
        connectionObject.setExpectedUpSpeed("1")


def getType(jsonData, count):
    valueToGet = jsonData["accessQualificationList"][count]["accessType"]["value"]

    if valueToGet == "NFAS":
        return "FTTP"
    elif valueToGet == "NWAS":
        return "Fixed Wireless"
    elif valueToGet == "NCAS":
        return "FTTN"
    elif valueToGet == "NHAS":
        return "HFC"
    elif valueToGet == "SSS" or valueToGet == "DSL-L2":
        return "ADSL2"


def read_csv(csv_file):
    data = []
    with open(csv_file, 'r') as f:
        # create a list of rows in the CSV file
        rows = f.readlines()

        # strip white-space and newlines
        rows = list(map(lambda x: x.strip(), rows))

        for row in rows:
            # further split each row into columns assuming delimiter is comma
            row = row.split(',')

            # append to data-frame our new row-object with columns
            data.append(row)

    return data


#########################

def main(jsonObject):
    connectionFinal = Connection()
    find(jsonObject, connectionFinal)
    return json.dumps(connectionFinal.__dict__)
