transfer_files="docker-compose.yml docker-compose.production.yml docker-compose.migrate.yml mysql-config-househunting.cnf secrets nginx"

function upload_files {
    rsync -avz -e "docker-machine ssh $host_prefix-master" $transfer_files :
}

function update_images {
    docker-machine ssh $host_prefix-master docker service update --image jhaiduce/househunting househunting_web
}
