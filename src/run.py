from flask import Flask, jsonify
from flask import request, abort
import argparse
import sys, os
from run_lexical_analysis_service import RunLexicalAnalysisService
import logging, json
import re
import time
import datetime
import nltk
import nltk.data
import xml.dom.minidom
from datetime import datetime as dt
import csv, traceback
import logging, logging.config

logging.config.fileConfig(fname='conf/logging.ini', disable_existing_loggers=False)
logger = logging.getLogger('run')

app = Flask(__name__)

@app.before_request
def before_request():
    if True:
        logger.info("HEADERS: %s", request.headers)
        logger.info("REQ_path: %s", request.path)
        logger.info("ARGS: %s",request.args)
        logger.info("DATA: %s",request.data)
        logger.info("FORM: %s",request.form)

def parse_input(request):
    logger.debug('----------------------PARSE DATA----------------------')
    input = dict()
    env = None
    if request.method == 'GET':

        input[0] = request.args.get('text')

    else:
        if request.headers['Content-Type'] == 'text/plain':
            input[0] = str(request.data.decode('utf-8'))

        else:
            logger.warning("Bad type: %s", request.headers['Content-Type'])
    logger.debug('---------------------------------------------------')

    try:
        env = os.environ['LAS_CONFIG_ENV']
    except KeyError as kerr:
        logger.warning("Environment variable LAS_CONFIG_ENV not set: %s", sys.exc_info()[0])
        logger.error(traceback.print_exc())
        env = None
        abort(500, 'Problem with setup: internal server error')
    except Exception as err:
        logger.warning("Unexpected error:", sys.exc_info()[0])
        logger.error(traceback.print_exc())
        env = None
        abort(500, 'Unexpected Internal Server Error')

    return input, env

def tokenization(text):
    tokenizer = setup_tokenizer()
    return tokenizer.tokenize(text)

def setup_tokenizer():
    tokenizer = nltk.data.load('tokenizers/punkt/finnish.pickle')
    with open('language-resources/abbreviations.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:
            tokenizer._params.abbrev_types.add(row[0])
    return tokenizer

@app.route('/', methods=['POST', 'GET'])
def index():
    input_data, env = parse_input(request)
    if input_data != None:
        las = RunLexicalAnalysisService(input_data, env)
        las.run()
        code = las.parse(parallel=False)
        results = las.get_json()

        logger.info(results)

        if code == 1:
            data = {'status': 200, 'data': results, 'service':"LAS wrapper", 'date':dt.today().strftime('%Y-%m-%d')}
            return jsonify(data)
        else:
            data = {'status': -1, 'error': results.toprettyxml(), 'service':"LAS wrapper", 'date':dt.today().strftime('%Y-%m-%d')}
            return jsonify(json.dumps(data, ensure_ascii=False))
    
    data = {'status': -1, 'error': "415 Unsupported Media Type ;)", 'service':"LAS wrapper", 'date':dt.today().strftime('%Y-%m-%d')}
    return jsonify(data)

