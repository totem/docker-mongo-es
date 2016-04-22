#!/bin/sh -e

export HOST_IP="${HOST_IP:-$(/sbin/ip route|awk '/default/ { print $3 }')}"
export ETCD_HOST="${ETCD_HOST:-$HOST_IP}"
export ETCD_PORT="${ETCD_PORT:-4001}"
export ETCD_URL="${ETCD_URL:-http://$ETCD_HOST:$ETCD_PORT}"
export ETCDCTL="${ETCDCTL:-etcdctl --peers $ETCD_URL}"
export ETCD_TOTEM_BASE="${ETCD_TOTEM_BASE:-/totem}"

if [ "$DISCOVER_MONGO" == "true" ]; then
  until $ETCDCTL cluster-health; do
    >&2 echo "Etcdctl cluster not healthy - sleeping"
    sleep 10
  done
  export MONGODB_SERVERS="$($ETCDCTL ls $ETCD_TOTEM_BASE/mongo/nodes | xargs -n 1  $ETCDCTL get | xargs echo -n | tr ' ' ',')"
  until [ ! -z "$MONGODB_SERVERS" ]; do
    >&2 echo "Mongo servers could not be discovered - sleeping"
    sleep 10
    export MONGODB_SERVERS="$($ETCDCTL ls $ETCD_TOTEM_BASE/mongo/nodes | xargs -n 1  $ETCDCTL get | xargs echo -n | tr ' ' ',')"
  done
fi

python3 run.py