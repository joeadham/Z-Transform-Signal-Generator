from flask import Flask, jsonify, make_response, render_template, request,session
import os
from scipy import signal
import numpy as np
import pandas as pd
import json
import plotly
import plotly.express as px
import time
app = Flask(__name__)
app.secret_key = "s3cr3t"
app.debug = False
app._static_folder = os.path.abspath("templates/static/")


angles3 = np.zeros(512)
phases = []


@app.route("/", methods=["POST", "GET"])
def main():
    if 'i' not in session:
        session['i'] = 0
    session['i'] = 0
    if 'fileName' not in session:
        session['fileName'] = ''
    return render_template("/layouts/trial.html")

@app.route("/plotMagAndPhase", methods=["POST", "GET"])
def plotMagAndPhase():
    zeros = request.values.getlist('zeros')
    poles = request.values.getlist('poles')
    print(zeros)
    print(poles)
    return "h"

@app.route('/data', methods=["GET", "POST"])
def data():
    if request.method == 'POST':
        filename = request.values['filename']
        #reads the csv file
        df = pd.read_csv(filename)
        
        if session['fileName'] != filename:
            session['fileName'] = filename
            session['i'] = 0
            # return json.dumps({0:0})
            # time.sleep(2)
        
        #plots the signal
        index = session['i']
        session['i'] += 1

        print('-'*50)
        index %= len(df)
        print(index)
        print(len(df))

        time.sleep(0.1)
        return json.dumps({0: index,1:df.iloc[index][1]})
    

 
@app.route("/allpass", methods=["POST", "GET"])
def allpass():
    return render_template("/layouts/allpass.html")

@app.route("/main", methods=["POST", "GET"])
def trial():
    return render_template("/layouts/trial.html")


@app.route("/postmethod", methods=["POST"])
def post_javascript_data():
    global angles3
    jsdata1 = request.form["zeros_data"]
    jsdata2 = request.form["poles_data"]
    jsdata3 = request.form["lambdaP"]
    flag = request.form["flag"]
    k = 1
    z = json.loads(jsdata1)
    p = json.loads(jsdata2)
    lambdaa = json.loads(jsdata3)
    flag = json.loads(flag)

    for i in range(len(z)):
        z[i] = round(z[i][0], 2)+ 1j * round(z[i][1], 2)
    for i in range(len(p)):
        p[i] = round(p[i][0], 2) + 1j * round(p[i][1], 2)

    w, h = signal.freqz_zpk(z, p, k)
    w = np.round(w, 2)
    angles = np.unwrap(np.angle(h))
    angles2 = np.zeros(512)
    h = 20 * np.log10(np.abs(h))
    w = w.tolist()
    h = h.tolist()
    if lambdaa == 5:
        for phase in phases:
            _, h2 = signal.freqz([phase, 1.0], [1.0, np.conj(phase)])
            angles2 += np.unwrap(np.angle(h2))
        if not np.all(angles):
            angles3 = np.zeros(512)
        else:
            angles3 = np.add(angles, angles2)
            # print(type(angles3))
        if len(phases) == 0:
            angles2 = np.zeros(512)
            angles3 = angles
        else:
            _, h2 = signal.freqz([phases[-1], 1.0], [1.0, np.conj(phases[-1])])
            angles2 = np.unwrap(np.angle(h2))
    elif flag:
        lambdaa = complex(lambdaa)
        _, h2 = signal.freqz([lambdaa, 1.0], [1.0, np.conj(lambdaa)])
        angles2 = np.unwrap(np.angle(h2))
        angles3 = np.add(angles3, angles2)
        phases.append(lambdaa)
    else:
        lambdaa = complex(lambdaa)
        _, h2 = signal.freqz([lambdaa, 1.0], [1.0, np.conj(lambdaa)])
        angles2 = np.unwrap(np.angle(h2))
        if np.all(angles3):
            angles3 = np.subtract(angles3, angles2)
        phases.remove(lambdaa)
        if len(phases) == 0:
            angles2 = np.zeros(512)
    angles = angles.tolist()
    angles2 = angles2.tolist()
    angles4 = angles3.tolist()

    params = {
        "magnitudeX": w,
        "magnitudeY": h,
        "angles": angles,
        "angles2": angles2,
        "angles3": angles4,
    }
    return jsonify(params)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000,debug = True)
