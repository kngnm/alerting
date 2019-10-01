#!/bin/bash

INFLUXDB_USER="grafana"
INFLUXDB_PASS="grafana"
INFLUXDB_DB="grafana"
NETWORK="monitoring-network"
GRAFANA_PORT="9000"

docker network create $NETWORK

docker build -t "influx" influxdb
docker build -t "link_connectivity" sensors/link_connectivity

docker kill "alerting_influxdb"
docker rm "alerting_influxdb"
docker run -d --name "alerting_influxdb" \
    -e "INFLUXDB_DB=$INFLUXDB_DB" \
    -e "INFLUXDB_USER=$INFLUXDB_USER" \
    -e "INFLUXDB_PASS=$INFLUXDB_PASS" \
    --net="$NETWORK" \
    "influx"

docker kill "alerting_grafana"
docker rm "alerting_grafana"
docker run -d --name "alerting_grafana" \
    -p $GRAFANA_PORT:3000 \
    -v "`pwd`/grafana:/var/lib/grafana" \
    --net="$NETWORK" \
    "grafana/grafana"

docker kill "alerting_router_connectivity"
docker rm "alerting_router_connectivity"
docker run -d --name "alerting_router_connectivity" \
    --net="$NETWORK" \
    -e "INFLUXDB_DB=$INFLUXDB_DB" \
    -e "INFLUXDB_USER=$INFLUXDB_USER" \
    -e "INFLUXDB_PASS=$INFLUXDB_PORT" \
    -e "INFLUXDB_HOST=alerting_influxdb" \
    -e "INFLUXDB_PORT=8086" \
    -e "LINK_TO=10.20.96.1" \
    "link_connectivity"
