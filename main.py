import json

import requests
from flask import Flask, request
from requests import ConnectionError
from requests.auth import HTTPBasicAuth

import startBB
# from config import authorization, telstra_location_url, telstra_details_url

import os

authorization = {
    "username": os.getenv("username"),
    "password": os.getenv("password"),
}
telstra_location_url = os.getenv("telstra_location_url")
telstra_details_url = os.getenv("telstra_details_url")
app = Flask(__name__)


@app.route("/")
def index():
    return 'success', 200


@app.route('/address/get', methods=['POST'])
def get():
    client_request = json.loads(request.data, encoding='utf8')
    success = do_telstra_service_lookup(client_request["locationId"],
                                        client_request)
    return success


@app.route('/address/search', methods=['POST'])
def search():
    try:
        client_request = json.loads(request.data)
        telstra_address = maps_to_telstra_address(client_request["address"])
        if not telstra_address:
            return 'Address is not valid', 400
        result = do_telstra_location_lookup(telstra_address)
        if result is False:
            return 'No Line Exists', 404
        if result is None or len(result) == 0:
            return 'Bad Request', 400
        if len(result) > 1:
            print("Warning: Address filter failed")
        # return result, 501

        result = result[0]
        service = do_telstra_service_lookup(result["locationId"],
                                            client_request)
    except ConnectionError:
        return "No connection available", 500
    return service


def do_telstra_location_lookup(args):
    data = json.dumps(args)
    print(data)
    header = {
        "Content-Type": "application/json",
    }
    response = requests.post(url=telstra_location_url, headers=header,
                             timeout=6000,
                             data=data,
                             auth=HTTPBasicAuth(authorization["username"],
                                                authorization["password"]))
    if response.status_code is 200:
        result = json.loads(response.content)
        for isp in result['serviceProviderLocationList']:
            if isp["serviceProvider"]["value"] == "Telstra":
                for location in isp["locationList"]:
                    if ((location["address"]["subAddressNumber"]) ==
                            args["address"]["unitNumber"]):
                        print "success"
                        return [location]
                return isp["locationList"]
    if response.status_code is 400:
        result = json.loads(response.content)
        if "error" in result:
            return False
    return None


def do_telstra_service_lookup(locationId, args):
    data = json.dumps({
        "qualifyNationalWholesaleBroadbandProductRequest": {
            "telstraLocationID": locationId,
            "standAloneQualification": "true"
        }
    })
    header = {
        "Content-Type": "application/json",
    }
    response = requests.post(telstra_details_url, headers=header, timeout=6000,
                             data=data,
                             auth=HTTPBasicAuth(authorization["username"],
                                                authorization["password"]))
    configured_data = startBB.main(response)
    return configured_data


def maps_to_telstra_address(maps_address):
    telstra = {"address": {
        "unitNumber": "",
        "streetNumber": "",
        "streetName": "",
        "streetType": "",
        "suburb": "",
        "state": "",
        "postcode": ""
    }}
    for field in maps_address["address_components"]:
        type = field["types"]
        value = field["long_name"].encode('utf-8')
        if "subpremise" in type:
            telstra["address"]["unitNumber"] = value
        if "street_number" in type:
            telstra["address"]["streetNumber"] = value
        if "route" in type:
            telstra["address"]["streetName"], telstra["address"][
                "streetType"] = value.rsplit(" ", 2)
        if "locality" in type:
            telstra["address"]["suburb"] = value
        if "administrative_area_level_1" in type:
            telstra["address"]["state"] = field["short_name"].encode('utf-8')
        if "postal_code" in type:
            telstra["address"]["postcode"] = value

    return telstra

if __name__ == '__main__':
    app.run()
