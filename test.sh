#!/bin/bash

export VENV=`pwd`/../venv

set -e

# Run unit tests
$VENV/bin/pytest -q

# Run migration tests
$VENV/bin/pytest -q dc_house_hunting/migration_tests.py

# Generate integration test secrets
python generate_secrets.py --ini-template integration_test.ini.tpl --ini-filename integration_test.ini --secretsdir integration_test_secrets

secret_files=("integration_test_secrets/integration_test.ini" "integration_test_secrets/production.ini" "integration_test_secrets/db_root_pw" "integration_test_secrets/rabbitmq_password" "integration_test_secrets/server-cert.pem" "integration_test_secrets/server-key.pem" "integration_test_secrets/ca.pem" "integration_test_secrets/storage_key.keyfile" "integration_test_secrets/localhost.localdomain.key" "integration_test_secrets/localhost.localdomain.crt" "integration_test_secrets/dhparams.pem" "nginx/common.conf" "nginx/common_location.conf" "nginx/default.conf" "nginx/househunting.conf" "nginx/ssl.conf" "mysql-config-househunting.cnf" "secrets/production.ini" "secrets/dhparams.pem")

for file in "${secret_files[@]}"
do
    chcon -t svirt_sandbox_file_t "$file"
done

# Build images
sudo docker-compose -f docker-compose.yml -f docker-compose.test.yml -f docker-compose.migrate.yml -f docker-compose.integration_tests.yml build

# Run database migration
./migrate_db_ci.sh

# Run integration tests
sudo docker-compose -f docker-compose.yml -f docker-compose.test.yml -f docker-compose.integration_tests.yml -p househunting_ci up --force-recreate -d

# Print test logs
sudo docker logs -f househunting_ci_integration_test_1
