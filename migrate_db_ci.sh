#!/bin/bash

set -e

# Migrate database
sudo docker-compose -f docker-compose.test_secrets.yml -f docker-compose.db.yml -f docker-compose.migrate.yml -p househunting_ci up -d

result=$(sudo docker wait househunting_ci_migration_1)

if [ $result != 0 ]
then

    # Print migration logs
    sudo docker logs househunting_ci_migration_1

    exit $result
fi

