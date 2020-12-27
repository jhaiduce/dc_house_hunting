#!/bin/bash

set -e

source "deployment-includes.sh"

numworkers=2

DOTAGS=househunting

host_prefix=househunting

node_image=ubuntu-18-04-x64

node_size=s-1vcpu-1gb

sudo docker-compose -f docker-compose.yml -f docker-compose.production.yml push

if [ $(docker-machine ls -q|grep -c $host_prefix-master) -eq "0" ]; then
  docker-machine create --driver digitalocean \
		 --digitalocean-size=$node_size \
		 --digitalocean-image $node_image \
		 --digitalocean-access-token $DOTOKEN \
		 --digitalocean-tags=$DOTAGS \
		 $host_prefix-master
  master_ip=$(docker-machine ip $host_prefix-master)
  docker-machine ssh $host_prefix-master docker swarm init --advertise-addr $master_ip
else
  master_ip=$(docker-machine ip $host_prefix-master)
fi

for i in $(seq 1 $numworkers); do
    if [ $(docker-machine ls -q|grep -c $host_prefix-$i) -eq "0" ]; then
	docker-machine create --driver digitalocean \
		       --digitalocean-size $node_size \
		       --digitalocean-image $node_image \
		       --digitalocean-access-token $DOTOKEN \
		       --digitalocean-tags $DOTAGS \
		       $host_prefix-$i
    fi
done

docker-machine ssh $host_prefix-master docker node update --label-add db=true $host_prefix-master

join_token=$(docker-machine ssh $host_prefix-master docker swarm join-token -q worker)

# Upload configuration files and secrets
upload_files

function isSwarmNode(){
    host=$1
    if [ "$(docker-machine ssh $host docker info | grep Swarm | sed 's/ Swarm: //g')" == "active" ]; then
        swarm_node=1
    else
        swarm_node=0
    fi
}

for i in $(seq 1 $numworkers); do
    host=$host_prefix-$i
    isSwarmNode $host
    if [ $swarm_node == 1 ]; then
        echo "$host_prefix-$i is already a member of the swarm"
    fi
    if [ $swarm_node == 0 ]; then
    echo "Joining node $i to swarm"
	docker-machine ssh $host \
		       docker swarm join --token $join_token $master_ip:2377
    fi
done

# Deploy the stack
docker-machine ssh $host_prefix-master docker stack deploy -c docker-compose.yml -c docker-compose.production.yml househunting

# Update the database
docker-machine ssh $host_prefix-master docker stack deploy -c docker-compose.yml -c docker-compose.production.yml -c docker-compose.migrate.yml househunting

function wait_for_migration {

    while [ 1 ]; do
	desired_state=$( docker-machine ssh $host_prefix-master docker service ps --format '{{.DesiredState}}' househunting_migration )
	current_state=$( docker-machine ssh $host_prefix-master docker service ps --format '{{.CurrentState}}' househunting_migration )

	echo 'Migration' $desired_state $current_state

	if [ $desired_state = 'Shutdown' ]; then
	    migration_container=$(docker-machine ssh $host_prefix-master docker service ps --format '{{.ID}}' househunting_migration)
	    migration_status=$(docker-machine ssh $host_prefix-master docker inspect --format '{{.Status.ContainerStatus.ExitCode}}' $migration_container)
	    return
	fi

	sleep 1
    done
}

# Wait for it to complete
wait_for_migration

docker-machine ssh $host_prefix-master docker service logs househunting_migration

if [ $migration_status -ne 0 ]; then
    exit 1;
fi

# Delete the migration service
docker-machine ssh $host_prefix-master docker service rm househunting_migration

# Update images
update_images
