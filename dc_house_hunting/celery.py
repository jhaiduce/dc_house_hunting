from celery import Celery
from celery.signals import worker_process_init, worker_process_shutdown
from celery.utils.log import get_task_logger
from . import models
import configparser

logger = get_task_logger(__name__)

session_factory=None

config=configparser.ConfigParser()
config.read('/run/secrets/production.ini')

@worker_process_init.connect
def bootstrap_pyramid(signal, sender, **kwargs):

    global session_factory
    
    import os
    from pyramid.paster import bootstrap

    settings = bootstrap('/run/secrets/production.ini')['registry'].settings

    engine=models.get_engine(settings,prefix='sqlalchemy.')
    
    while True:

        # Here we try to connect to database server until connection succeeds.
        # This is needed because the database server may take longer
        # to start than the application
        
        import sqlalchemy.exc

        try:
            print("Checking database connection")
            conn=engine.connect()
            conn.execute("select 'OK'")

        except sqlalchemy.exc.OperationalError:
            import time
            print("Connection failed. Sleeping.")
            time.sleep(2)
            continue
        
        # If we get to this line, connection has succeeded so we break
        # out of the loop
        conn.close()
        break
    
    session_factory=models.get_session_factory(engine)

def get_celery_worker_status():
    ERROR_KEY = "ERROR"
    try:
        from celery.task.control import inspect
        insp = inspect()
        d = insp.stats()
        if not d:
            d = { ERROR_KEY: 'No running Celery workers were found.' }
    except IOError as e:
        from errno import errorcode
        msg = "Error connecting to the backend: " + str(e)
        if len(e.args) > 0 and errorcode.get(e.args[0]) == 'ECONNREFUSED':
            msg += ' Check that the RabbitMQ server is running.'
        d = { ERROR_KEY: msg }
    except ImportError as e:
        d = { ERROR_KEY: str(e)}
    return d

try:
    backend=config['celery']['backend_url']
except KeyError:
    backend='rpc://'

try:
    broker=config['celery']['broker_url']
except KeyError:
    broker='memory://localhost/'

celery=Celery(backend=backend, broker=broker)
celery.config_from_object('dc_house_hunting.celeryconfig')
