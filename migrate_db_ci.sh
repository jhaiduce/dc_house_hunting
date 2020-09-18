#!/bin/bash

set -e

# Migrate database
sudo docker-compose -f docker-compose.yml -f docker-compose.test.yml -f docker-compose.migrate.yml -f docker-compose.migration.test.yml -p househunting_ci up --remove-orphans --force-recreate -d

result=$(sudo docker wait househunting_ci_migration_1)

if [ $result != 0 ]
then

    # Print migration logs
    sudo docker logs househunting_ci_migration_1

    exit $result
fi

