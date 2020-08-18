# -*- coding: utf-8 -*-
import os
import sys
sys.path.append('../XM')
sys.path.append('../common')
sys.path.append('../private')

import json
from flask import render_template
from flask import Flask, request, render_template, jsonify
from MT5Bind import MT5Bind

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config["JSON_SORT_KEYS"] = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/xmdata', methods=['GET', 'POST'])
def xmdata():
    print("xmdata!")
    #market = "US30Cash"
    market = request.form.get('market')
    #timeframe = "M5"
    timeframe = request.form.get('timeframe')
    dic = downloadData(market, timeframe, 150)
    return render_template('index.html', response=json.dumps(dic))

def downloadData(market, timeframe, length):
    server = MT5Bind(market)
    dic = server.scrapeWithDic(timeframe, length)
    print(dic)
    return dic

if __name__ == '__main__':
    app.run(port=5500, debug=True)