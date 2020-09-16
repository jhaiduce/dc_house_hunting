export VENV=`pwd`/../venv

# Kill running containers
sudo docker kill househunting_web
sudo docker kill househunting_ci_integration_test_1
sudo docker kill househunting_ci_migration_1

set -e

# Run unit tests
#$VENV/bin/pytest -q

# Run migration tests
#$VENV/bin/pytest -q dc_house_hunting/migration_tests.py

# Build images
sudo docker-compose -f docker-compose.test_secrets.yml -f docker-compose.web.yml -f docker-compose.test.yml -f docker-compose.db.yml -f docker-compose.migrate.yml -f docker-compose.test.yml build

# Generate integration test secrets
python generate_secrets.py --ini-template integration_test.ini.tpl --ini-filename integration_test.ini --secretsdir integration_test_secrets

# Run database migration
./migrate_db_ci.sh

# Run tests
sudo docker-compose -f docker-compose.test_secrets.yml -f docker-compose.web.yml -f docker-compose.db.yml -f docker-compose.test.yml -p househunting_ci up --remove-orphans -d

# Print test logs
sudo docker logs -f househunting_ci_integration_test_1
