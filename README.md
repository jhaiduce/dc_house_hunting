# DC House Hunting

This is a Pyramid web application to aid in a housing search

## Set up the development environment

1. Change directory into your newly created project.

  ```console
  cd dc_house_hunting
  ```

2. Create a Python virtual environment.

  ```console
  python3 -m venv env
  ```

3. Upgrade packaging tools.

```console
env/bin/pip install --upgrade pip setuptools
```

4. Install the project in editable mode with its testing requirements.

```console
env/bin/pip install -e ".[testing]"
```

5. Initialize and upgrade the database

```console
env/bin/initialize_dc_house_hunting_db development.ini
```

6. Run unit tests.

```console
env/bin/pytest
```

7. Start the application on a local test server

```console
env/bin/pserve development.ini
```

