import json

import requests
import startBB
from flask import Flask, request
from requests import ConnectionError
from requests.auth import HTTPBasicAuth

try:
    from config import authorization, telstra_location_url, telstra_details_url
except ImportError:
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
    client_request = json.loads(request.data)
    success = do_telstra_service_lookup(client_request["locationId"],
                                        client_request)
    return success


@app.route('/address/search', methods=['POST'])
def search():
    try:
        client_request = json.loads(request.data)
        result = do_telstra_location_lookup(client_request)
        if result is False:
            return 'No Line Available', 437
        if result is None:
            return 'Bad Request', 400
        if len(result) > 1:
            print("Warning: Address filter failed")
        # return result, 501

<<<<<<< HEAD
        result = result[0]
        service = do_telstra_service_lookup(result["locationId"],
                                            client_request)
    except ConnectionError:
        return "No connection available", 500
    return service
=======
    result = result[0]
    service = do_telstra_service_lookup(result["locationId"], client_request)
    return service, 200
>>>>>>> origin/bens-magic


def do_telstra_location_lookup(args):
    data = json.dumps(args)
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
    configuredData = startBB.main(response)
    return configuredData

if __name__ == '__main__':
    app.run()

