from re import template
import re
from flask import Flask, redirect, request, jsonify, render_template, url_for
from ws_Prediction import Load_Data, Results, Save

from time import sleep

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from datetime import datetime, date
import webbrowser
    

app = Flask(__name__)

scheduler = BackgroundScheduler()


@app.route('/')
def main():
    return render_template('index_ml.html', hasil=""" Class label adalah '{}' """.format(None))
    
 
@app.route('/hasil')
def hasil():
    data = Load_Data()
    idlist, dataset = data.get_db()
    
    res = Results()
    label = res.hasil_pengolahan(dataset)        

    save = Save()
    save.simpan_data(idlist, label)

    waktu = datetime.now()
    
    #webbrowser.open("http://127.0.0.1:5000/hasil")
    with app.app_context(), app.test_request_context():
        return render_template('index_ml.html', hasil=""" Class label adalah '{}' update terakhir {} """.format(label,waktu))


trigger = CronTrigger(year="*", month="*", day="*", hour="15", minute="7", second="0")


if __name__ == "__main__":
    scheduler.start()
    scheduler.add_job(hasil,trigger=trigger)
    webbrowser.open("http://127.0.0.1:5000/")
    app.run(debug=False)
    