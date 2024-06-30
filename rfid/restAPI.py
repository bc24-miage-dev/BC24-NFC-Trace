from flask import Flask, jsonify, request, Response, copy_current_request_context
import json, os, logging, sys
import pn532.pn532 as nfc
from pn532 import *
from write_main import write_main
import read_main
import threading

app = Flask(__name__)

class Response(Response):
    def call_on_close(self, func):
        self.call_on_close_func = func
        return self

    def close(self):
        if hasattr(self, 'call_on_close_func'):
            self.call_on_close_func()
        super().close()

def init_nfc_module():
    # Initialisation du module NFC PN532
    pn532 = PN532_SPI(debug=False, reset=20, cs=4)
    #pn532 = PN532_I2C(debug=False, reset=20, req=16)
    ic, ver, rev, support = pn532.get_firmware_version()
    print('Module NFC PN532 trouvé avec la version de firmware : {0}.{1}'.format(ver, rev))
    # Configuration pour communiquer avec les cartes MiFare
    pn532.SAM_configuration()

    print('En attente de la carte RFID/NFC à écrire...')
    # Vérifier si une carte est disponible à la lecture
    uid = pn532.read_passive_target(timeout=0.5)
    print('.', end="")

    init = {
        "uid" : uid,
        "pn532" : pn532
    }

    return init

"""
When called, read_json() returns the JSON file's content
located in directory "json/"
"""
@app.route('/read', methods=['GET'])
def read_json():

    # JSON file path
    JSON_DIRECTORY = "json/"

    # Read all files in given path JSON_DIRECTORY
    logging.warning("Fetching all files in " + JSON_DIRECTORY + " ...")

    try:
        json_file = os.listdir(JSON_DIRECTORY)

        logging.warning("Reading JSON file...")
        readerFile = open(JSON_DIRECTORY + json_file[0])
        # Store JSON file content in dictionnary
        data = json.load(readerFile)
        print(data)
        
        return jsonify({'result' : data}), 200
    except:
        
        return jsonify({"Message" : "An error has occured"}), 404    


"""
When called, write() gets body data from POST request
and write on NFC tag
"""
@app.route('/write', methods=['POST'])
def write():
    for thread in threading.enumerate(): 
        print(thread.name)

    try:
        read_main.stop()
    except:
        pass
    
    # Check if NFC Tag is present
    init = init_nfc_module()
    uid = init.get("uid")
    pn532 = init.get("pn532")
    
    # get data in request
    data = request.get_json()

    # Check if all mandatory data is given (check keys)
    if ("NFT_tokenID" in data):
        # Call method write_main() from write_main.py to write on NFC tag 
        # Try again until write_main() returns True
        hasSucceeded = False
        while not hasSucceeded:
            hasSucceeded = write_main(pn532, uid, str(data.get("NFT_tokenID")))
        
        response = Response()
        json_data = {"success": True, "message": "Data saved !"}
        json_response = jsonify(json_data)
        response = Response(response=json_response.response,
                        status=202,
                        content_type="application/json")

        """ @response.call_on_close
        @copy_current_request_context
        def restart():
            print("restarting reader...")
            startReader() """

        return response
    else:
        response = Response()
        json_data = {"success": False, "error": "Make sure you have a NFT_tokenID in your request json!"}
        json_response = jsonify(json_data)
        response = Response(response=json_response.response,
                        status=400,
                        content_type="application/json")

        """  @response.call_on_close
        @copy_current_request_context
        def restart():
            print("restarting reader...")
            startReader() """

        return response



@app.route('/stopReader', methods=['GET'])
def stopReader():
    try:
        read_main.stop()
        return jsonify({'success' : True, "message": "Reader has stopped"}), 200
    except:
        return jsonify({'success' : False, "error": "Reader cannot be stopped"}), 500
    
@app.route('/startReader', methods=['GET'])
def startReader():
    try:
        result = read_main.start()
        return jsonify(result), 200
        return jsonify({'success' : True, "message": "Reader has started"}), 200
    except:
        return jsonify({'success' : False, "error": "Reader cannot start"}), 500      
    
if __name__ == '__main__':
    app.run(port=5000)

