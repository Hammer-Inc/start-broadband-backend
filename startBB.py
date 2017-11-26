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


class Connection(object):
    def __init__(self):
        self.connectionType = None
        body_dict = {"priceZone": None, "portsAvailability": None}
        self.body = body_dict

    def setConnectionType(self, connectionType):
        self.connectionType = connectionType

    def setPriceZone(self, priceZone):
        self.body["priceZone"] = priceZone

    def setPortsAvailability(self, portsAvailability):
        self.body["portsAvailability"] = portsAvailability

def find(jsonObject, connectionObject):
    global containingRow

    validation = 1
    count = 0
    jsonText = str(jsonObject.text)
    jsonData = json.loads(jsonText)

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
            # if current rows 2nd value is equal to input, print that row
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

def getType(jsonData, count):
    valueToGet = jsonData["accessQualificationList"][count]["accessType"]["value"]

    if valueToGet == "NFAS":
        return "Fibre To The Premises"
    elif valueToGet == "NWAS":
        return "Fixed Wireless"
    elif valueToGet == "NCAS":
        return "Fibre To The Node"
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
