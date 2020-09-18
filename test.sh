export VENV=`pwd`/../venv

set -e

# Run unit tests
$VENV/bin/pytest -q

# Run migration tests
$VENV/bin/pytest -q dc_house_hunting/migration_tests.py

# Generate integration test secrets
python generate_secrets.py --ini-template integration_test.ini.tpl --ini-filename integration_test.ini --secretsdir integration_test_secrets

# Build images
sudo docker-compose -f docker-compose.yml -f docker-compose.test.yml -f docker-compose.migrate.yml -f docker-compose.integration_tests.yml build

# Run database migration
./migrate_db_ci.sh

# Run integration tests
sudo docker-compose -f docker-compose.yml -f docker-compose.test.yml -f docker-compose.integration_tests.yml -p househunting_ci up --force-recreate -d

# Print test logs
sudo docker logs -f househunting_ci_integration_test_1
