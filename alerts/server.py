import flask
from flask import Flask
from flask import request, render_template, redirect
import _thread
import requests
import time
import smtplib
import sqlite3
import random
import math
import datetime
import os

smtpserver = smtplib.SMTP("smtp.gmail.com", 587)
smtpserver.ehlo()
smtpserver.starttls()
smtpserver.ehlo()
smtpserver.login(os.environ["SEND_ADDRESS"], os.environ["SEND_ADDRESS_PASSWORD"])

conn = sqlite3.connect("db/alerts.db")
conn.execute("create table if not exists alerts (id integer, type int, time_fired long, time_acked long, time_resolved long, message text, status int)")
conn.commit()

app = Flask(__name__)

alerts = {}

@app.route("/")
def index():
    conn = sqlite3.connect("db/alerts.db")
    status = {"open": 0, "acked": 1, "closed": 2}
    int_to_status = {0: "open", 1: "acknowledged", 2: "closed"}
    if request.args.get("c") is not None:
        rows = conn.execute("select * from alerts where status = {0} order by time_fired desc".format(status[request.args.get("c")]))
    elif request.args.get("s") is not None:
        rows = conn.execute("select * from alerts where message like '%{0}%' order by time_fired desc".format(request.args.get("s")))
    else:
        rows = conn.execute("select * from alerts order by time_fired desc")
    tbody = ""
    for i in rows:
          tbody += '<tr><th scope="row">{0}</th><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td></tr>'.format(
            i[0],
            datetime.datetime.fromtimestamp(math.floor(i[2])),
            i[-2],
            int_to_status[i[-1]],
            """
            <div class="dropdown">
  <a class="btn btn-secondary dropdown-toggle" href="#" role="button" id="dropdownMenuLink" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
    Actions
  </a>

  <div class="dropdown-menu" aria-labelledby="dropdownMenuLink">
    <a class="dropdown-item" href="/acknowledge?id={0}">Acknowledge</a>
    <a class="dropdown-item" href="/resolve?id={0}">Resolve</a>
  </div>
</div>
            """.format(i[0])
          )
    return render_template(
        "index.html",
        all="active" if request.args.get("c") is None else "inactive",
        open="active" if request.args.get("c") == "open" else "inactive",
        closed="active" if request.args.get("c") == "closed" else "inactive",
        acked="active" if request.args.get("c") == "acked"else "inactive",
        tbody=tbody
    )

@app.route("/resolve")
def resolve():
    conn = sqlite3.connect("db/alerts.db")
    for i in conn.execute("select type from alerts where id = {0}".format(int(request.args.get("id")))):
        t = i[0]
    alerts[t] = "inactive"
    conn.execute("update alerts set status = 2, time_resolved = {1} where id = {0}".format(int(request.args.get("id")), time.time()))
    conn.commit()
    return redirect("/?c=open")

@app.route("/acknowledge")
def acknowledge():
    conn = sqlite3.connect("db/alerts.db")
    for i in conn.execute("select type from alerts where id = {0}".format(int(request.args.get("id")))):
        t = i[0]
    alerts[t] = "acknowledged"
    conn.execute("update alerts set status = 1, time_acked = {1} where id = {0}".format(int(request.args.get("id")), time.time()))
    conn.commit()
    return redirect("/?c=open")

def check_alerts():
    conn = sqlite3.connect("db/alerts.db")
    while True:
        alert = []
        for line in open("definitions", "r").readlines():
            alert.append([i.strip() for i in line.split("|")])
        i = 0
        for query, predicate, msg in alert:
            res = requests.post("http://10.0.0.10:8086/query?db=grafana&q={0}".format(query)).json()
            res = res["results"][0]["series"][0]["values"][-1][1]
            try:
                if (eval(predicate.replace("value", str(res)))):
                    if i not in alerts or alerts[i] == "inactive":
                        alerts[i] = "active"
                        id = random.randint(0,10000000)
                        conn.execute("insert into alerts values ({0}, {1}, {2}, {3}, {4}, {5}, {6})".format(
                            id,
                            i,
                            time.time(),
                            0,
                            0,
                            "'"+msg+"'",
                            0
                        ))
                        conn.commit()
                        smtpserver.sendmail(
                            os.environ["SEND_ADDRESS"],
                            os.environ["RECV_ADDRESS"],
                            """Subject: Alert Fired

{0}
Acknowlege: http://{2}:{3}/acknowledge?id={1}
Resolve:    http://{2}:{3}/resolve?id={1}
                        """.format(msg, id, os.environ["SERVER_DOMAIN"], os.environ["SERVER_PORT"]),
                    )
                i += 1
            except:
                pass
        time.sleep(5)

_thread.start_new(check_alerts, ())

if __name__ == "__main__":
    app.run(port=9450, host="0.0.0.0")
