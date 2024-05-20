from flask import *
import json, os, logging, sys
import pn532.pn532 as nfc
from pn532 import *
from write_main import write_main
from read_main import reader
from threading import Thread
import threading

app = Flask(__name__)

isRunning = True

def init_nfc_module():
    # Initialisation du module NFC PN532
    # pn532 = PN532_SPI(debug=False, reset=20, cs=4)
    pn532 = PN532_I2C(debug=False, reset=20, req=16)
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

    thread = threading.Thread(target=reader, args=(isRunning,))

    try:
        json_file = os.listdir(JSON_DIRECTORY)

        logging.warning("Reading JSON file...")
        readerFile = open(JSON_DIRECTORY + json_file[0])
        # Store JSON file content in dictionnary
        data = json.load(readerFile)

        thread.start()
        return jsonify({'result' : data}), 200
    except:
        thread.start()
        return jsonify({"Message" : "An error has occured"}), 404    


"""
When called, write() gets body data from POST request
and write on NFC tag
"""
@app.route('/write', methods=['POST'])
def write():
    # Check if NFC Tag is present
    try:
        init = init_nfc_module()
        uid = init.get("uid")
        pn532 = init.get("pn532")
    # Returns error msg if no NFC tag is present
    except:
        return jsonify({"success": False, "error": "Request canceled : no NFC tag"}), 404
    
    # Check if body is present in request
    data = request.get_json()

    thread = threading.Thread(target=reader, args=(isRunning,))

    # Check if all mandatory data is given (check keys)
    if ("NFT_tokenID" in data):
        try:
            # Call method write_main() from write_main.py to write on NFC tag 
            write_main(pn532, uid, str(data.get("NFT_tokenID")))
            thread.start()
            return jsonify({"success": True, "success": "data written on NFC tag"}), 200
        except:
            thread.start()
            return jsonify({"success": False, "error": "An error has occured"}), 500
    else:
        thread.start()
        return jsonify({"success": False, "error": "Request not valid : JSON data not valid"}), 400

@app.route('/startReader', methods=['GET'])
def startReader():
    try:
        isRunning = True
        reader(isRunning)
    except:
        return jsonify({"success": False, "error": "An error has occured while trying to start reader"}), 500
    
@app.before_request
def exit():
    try:
        print(threading.enumerate())
        if (isRunning == True):
            isRunning = False
            reader(isRunning)
    except:
        return
    
if __name__ == '__main__':
    app.run(port=5000)

