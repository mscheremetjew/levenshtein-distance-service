import logging

from django.core.cache import caches
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template import loader
from django_celery_results.models import TaskResult

from distance_app.tasks import calculate_levenshtein_distance

logger = logging.getLogger(__name__)


def index(request):
    """Request handler for /jobs/ GET and POST requests.

    :param request:
    :return:
    """
    # Only allow authenticated POST requests
    if request.user.is_authenticated and request.POST:
        logger.info("Retrieved job index page POST request")
        try:
            uniprot_id_1 = request.POST.get("uniprot_id_1")
            uniprot_id_2 = request.POST.get("uniprot_id_2")
            assert uniprot_id_1 and uniprot_id_2
            task = calculate_levenshtein_distance.delay(uniprot_id_1, uniprot_id_2, request.user.id)
            m_cache = caches.all()[0]
            m_cache.set(task.id, request.user.id, 300)
            logger.debug("Caching task_id to user id mapping...")
        except (KeyError, AssertionError):
            return render(
                request,
                "jobs/index.html",
                {
                    "error_message": "You didn't specify a UniProt ID.",
                },
            )
        else:
            template = loader.get_template("jobs/success.html")
            context = {
                "task_id": task.id,
            }
            return HttpResponse(template.render(context, request))
    else:
        template = loader.get_template("jobs/index.html")
        latest_job_list = TaskResult.objects.filter(task_creator_id=request.user.id)
        context = {
            "latest_job_list": latest_job_list,
        }
        return HttpResponse(template.render(context, request))


def detail(request, job_id):
    """Request handler for the jobs detail page."""
    if request.user.is_authenticated:
        template = loader.get_template("jobs/detail.html")
        task_result = TaskResult.objects.filter(task_id=job_id, task_creator_id=request.user.id)
        if len(task_result) > 0:
            context = {
                "job_detail": task_result[0],
            }
            return HttpResponse(template.render(context, request))
        else:
            JsonResponse({"task_id": job_id}, status=404)
    else:
        JsonResponse({"task_id": job_id}, status=403)


def status(request, job_id):
    """Request handler for the jobs detail page."""
    if request.user and request.user.is_authenticated:
        try:
            task_result = TaskResult.objects.filter(task_id=job_id, task_creator_id=request.user.id)
            if len(task_result) > 0:
                task_result = task_result[0]
                result = {"task_id": job_id, "task_status": task_result.status, "task_result": task_result.result}
                return JsonResponse(result, status=200)
            else:
                JsonResponse({"task_id": job_id}, status=404)
        except Exception:
            JsonResponse({"task_id": job_id}, status=404)

    else:
        JsonResponse({"task_id": job_id}, status=403)
