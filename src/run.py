from flask import Flask, jsonify
from flask import request
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
import csv

app = Flask(__name__)


@app.before_request
def before_request():
    if True:
        print("HEADERS", request.headers)
        print("REQ_path", request.path)
        print("ARGS",request.args)
        print("DATA",request.data)
        print("FORM",request.form)

def parse_input(request):
    print('----------------------PARSE DATA----------------------')
    input = dict()
    env = None
    if request.method == 'GET':

        input[0] = request.args.get('text')

        opt_param = request.args.get("test")
        print('OPT PARAM', opt_param)
        if opt_param != None:
            env = "TEST"
        print('VALUE', env)
    else:
        if request.headers['Content-Type'] == 'text/plain':
            input[0] = str(request.data.decode('utf-8'))
            print("data", input)

            opt_param = request.args.get("test")
            print('OPT PARAM', opt_param)
            if opt_param != None:
                env = "TEST"
            print('VALUE', env)
        else:
            print("Bad type", request.headers['Content-Type'])
    print('---------------------------------------------------')
    return input, env

def tokenization(text):
    print('Tokenize this', text)
    tokenizer = setup_tokenizer()
    return tokenizer.tokenize(text)

def setup_tokenizer():
    tokenizer = nltk.data.load('tokenizers/punkt/finnish.pickle')
    with open('language-resources/abbreviations.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:
            print("Add abbreviation", row[0])
            tokenizer._params.abbrev_types.add(row[0])
    return tokenizer

@app.route('/', methods=['POST', 'GET'])
def index():
    input_data, env = parse_input(request)
    if input_data != None:
        depParser = RunLexicalAnalysisService(input_data, env)
        depParser.run()
        code = depParser.parse(parallel=False)
        results = depParser.get_json()

        if code == 1:
            data = {'status': 200, 'data': results, 'service':"Finnish-dep-parser wrapper", 'date':dt.today().strftime('%Y-%m-%d')}
            return jsonify(data)
        else:
            data = {'status': -1, 'error': results.toprettyxml(), 'service':"Finnish-dep-parser wrapper", 'date':dt.today().strftime('%Y-%m-%d')}
            return jsonify(json.dumps(data, ensure_ascii=False))
    
    data = {'status': -1, 'error': "415 Unsupported Media Type ;)", 'service':"Finnish-dep-parser wrapper", 'date':dt.today().strftime('%Y-%m-%d')}
    return jsonify(data)

