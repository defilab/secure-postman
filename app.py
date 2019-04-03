import os
import sys
import json
import time
import base64
from flask import Flask, request, make_response

from points.entities import Entity
from points.ledgers import OntologyLedger, HyperLedger

import storage

app = Flask(__name__)


if os.getenv('REDIS_DB_HOST'):
    store = storage.RedisStore(os.getenv('REDIS_DB_HOST'))
else:
    store = storage.RamStore()

server_entity = Entity(
    os.getenv("ACCOUNT_NAME", ""), 
    ledger_class=OntologyLedger if os.getenv('LEDGER_TYPE', 'OntologyLedger') == 'OntologyLedger' else HyperLedger, 
    channel=os.getenv("CHANNEL_ENDPOINT", 'channel.test.defilab.com'),
    postman_endpoint=os.getenv("POSTMAN_ENDPOINT", 'https://postman.test.defilab.com'),
    registry_endpoint=os.getenv('REGISTRY_ENDPOINT', 'http://registry.test.defilab.com'),
    rpc_address=os.getenv('BLOCKCHAIN_RPC_ADDRESS', 'http://chain.test.defilab.com:20336'),
    channel_name=os.getenv('CHANNEL_NAME', 'pts-exchange'),
    chaincode=os.getenv("CHAINCODE", 'pts-exchange'),
)

@app.route('/upload', methods=['POST'])
def upload():
    offer = request.get_json()
    assert offer.get('offer_id'), "offer_id is required"
    assert offer.get('payload'), "payload is required"

    retrieve_code = store.put(offer)
    receipt = server_entity.sign(offer['offer_id'])
    res = make_response(json.dumps(dict(receipt=receipt, retrieve_code=retrieve_code)))
    res.headers['Content-Type'] = 'application/json'
    return res

@app.route('/download/<retrieve_code>/<transaction_id>', methods=['GET'])
def download(retrieve_code, transaction_id):
    offer = store.get(retrieve_code)
    if not offer:
        return "Not found", 404
    if os.getenv("NO_TX_VERIFICATION") not in ('1', 'true') and \
       not server_entity.ledger.verify_transaction_blocking(offer['offer_id'], transaction_id, 'AcceptOffer', timeout=10):
            return "Transaction is not verified", 400
    return offer['payload']

@app.route('/')
def health_check():
    return ""
