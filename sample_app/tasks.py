import abc
from functools import lru_cache

from django_cloud_tasks.tasks import (
    Task,
)
from gcp_pilot.tasks import CloudTasks
from google.cloud import tasks_v2
from google.cloud.tasks_v2.services.cloud_tasks.transports import (
    CloudTasksGrpcTransport,
)
import grpc
from django.conf import settings
import logging
from sample_app.models import TaskResult

logger = logging.getLogger(__name__)


class BaseAbstractTask(Task, abc.ABC):
    def run(self, **kwargs):
        raise NotImplementedError()

    def _track_task(self, task_id, task_name, status, result=None):
        TaskResult.objects.create(
            task_id=task_id, task_name=task_name, status=status, result=result
        )
        return task_id

    @classmethod
    @lru_cache()
    def _get_tasks_client(cls) -> CloudTasks:
        if not settings.DEBUG:
            return super()._get_tasks_client()

        logger.info("[Task] Using Cloud Tasks emulator...")
        cloud_tasks = CloudTasks()
        channel = grpc.insecure_channel("tasks-emulator:8123")
        transport = CloudTasksGrpcTransport(channel=channel)
        client = tasks_v2.CloudTasksClient(transport=transport)
        parent = "projects/my-project/locations/us-east4"
        queue_name = parent + "/queues/tasks"
        try:
            client.create_queue(parent=parent, queue={"name": queue_name})
        except Exception:
            pass

        cloud_tasks.client = client
        return cloud_tasks


class CalculatePriceTask(BaseAbstractTask):
    def run(self, price, quantity, discount):
        task_id = self._track_task(
            self._metadata.task_id, self.__class__.__name__, "running"
        )
        try:
            result = price * quantity * (1 - discount)
            TaskResult.objects.filter(task_id=task_id).update(
                status="completed", result=result
            )
            return result
        except Exception as e:
            TaskResult.objects.filter(task_id=task_id).update(
                status="failed", result=str(e)
            )
            raise
