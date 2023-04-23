import logging

from celery import shared_task
from django.core.cache import caches
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django_celery_results.models import TaskResult
from Levenshtein import distance

from authentication.models import User
from distance_app.uniprot_api import uniprot_client

logger = logging.getLogger(__name__)


@shared_task
def calculate_levenshtein_distance(uniprot_id_1: str, uniprot_id_2: str, user_id):
    """Task, which calculates and returns the Levenshtein distance between the given UniProt entries.

    Step 1: Calculate distance
    Step 2: Notify user via email
    """
    logger.info(f"Calculating Levenshtein distance between {uniprot_id_1} and {uniprot_id_2}")
    protein_seq_1 = uniprot_client.fetch_sequence_by_uniprot_id(uniprot_id_1)
    protein_seq_2 = uniprot_client.fetch_sequence_by_uniprot_id(uniprot_id_2)

    user = User.objects.get(pk=user_id)
    user.email_user(
        subject="Notification of job status", message="The processing of your job has finished!", fail_silently=True
    )
    result = distance(protein_seq_1, protein_seq_2)
    logger.info("Levenshtein distance successfully calculated.")
    logger.debug(f"Levenshtein distance between {uniprot_id_1} and {uniprot_id_2} is: {result}")
    return result


@receiver(pre_save, sender=TaskResult)
def task_result_callback(sender, instance, *args, **kwargs):
    m_cache = caches.all()[0]
    user_id = m_cache.get(instance.task_id, "not found")
    instance.task_creator_id = user_id
