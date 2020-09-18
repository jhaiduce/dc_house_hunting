from dc_house_hunting import celery
import logging

log = logging.getLogger(__name__)
    
while True:
    try:
        # Check whether there are celery workers running
        worker_status = celery.get_celery_worker_status()
        if worker_status is not None:
            # There are workers, exit the loop
            break
    except IOError:
        log.debug('Broker not running.')
    else:
        log.debug('No celery workers running.')
    
    sleep(1)
