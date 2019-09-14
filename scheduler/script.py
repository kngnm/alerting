import datetime
import time
import os

jobs = {}

f = open("jobs","r")
for i in f.readlines():
    i = i.strip()
    if i != "" and not i.startswith("#"):
        j,k = i.split("|")
        k = k.replace("ssh", "ssh -i /ssh/id_rsa -o \"StrictHostKeyChecking no\"")
        jobs[tuple([int(l) for l in j.strip().split(":")])] = k.strip()

while True:
    now = datetime.datetime.now()
    t = ((now.hour+24-7)%24, now.minute)
    if t in jobs:
        print ("Running",jobs[t])
        os.system(jobs[t])
    time.sleep(60)
