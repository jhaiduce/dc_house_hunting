from ..models.housing_search_models import Residence
from ..celery import celery

from celery.utils.log import get_task_logger

import transaction

logger = get_task_logger(__name__)

@celery.task(ignore_result=False)
def update_scores(residence_ids=None):

    from ..celery import session_factory
    from ..models import get_tm_session

    dbsession=get_tm_session(session_factory, transaction.manager)

    logger.debug('Received update_scores task')

    if residence_ids is None:

        for residence in dbsession.query(Residence):
            residence.compute_score()

    else:

        try:
            len(residence_ids)
        except TypeError:
            residence_ids=[residence_ids]

        for residence_id in residence_ids:

            residence=dbsession.query(
                Residence(id=residence_id)).one()

            residence.compute_score()

    transaction.commit()
