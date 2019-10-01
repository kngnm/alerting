FROM influxdb

ADD init.sh init.sh
RUN chmod a+x init.sh

CMD bash init.sh & influxd
