import abc
from functools import lru_cache
import time
from django.db.models import Model

from django_cloud_tasks.tasks import (
    PeriodicTask,
    RoutineTask,
    SubscriberTask,
    Task,
    ModelPublisherTask,
    TaskMetadata,
)
from django_cloud_tasks.exceptions import DiscardTaskException
from gcp_pilot.tasks import CloudTasks
from google.cloud import tasks_v2
from google.cloud.tasks_v2.services.cloud_tasks.transports import (
    CloudTasksGrpcTransport,
)
import grpc
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class BaseAbstractTask(Task, abc.ABC):
    def run(self, **kwargs):
        raise NotImplementedError()

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


class AnotherBaseAbstractTask(BaseAbstractTask, abc.ABC):
    def run(self, **kwargs):
        raise NotImplementedError()


class CalculatePriceTask(BaseAbstractTask):
    def run(self, price, quantity, discount):
        print("Running!")
        time.sleep(5)
        print("Slept!")
        return price * quantity * (1 - discount)


class ParentCallingChildTask(Task):
    def run(self, price, quantity):
        CalculatePriceTask.asap(price=price, quantity=quantity, discount=0)


class ExposeCustomHeadersTask(Task):
    def run(self):
        return self._metadata.custom_headers


class FailMiserablyTask(AnotherBaseAbstractTask):
    only_once = True

    def run(self, magic_number):
        return magic_number / 0


class SaySomethingTask(PeriodicTask):
    run_every = "* * * * 1"

    def run(self):
        print("Hello!!")


class PleaseNotifyMeTask(SubscriberTask):
    @classmethod
    def topic_name(cls):
        return "potato"

    @classmethod
    def dead_letter_topic_name(cls):
        return None

    def run(self, content: dict, attributes: dict[str, str] | None = None):
        return content


class ParentSubscriberTask(SubscriberTask):
    @classmethod
    def topic_name(cls):
        return "parent"

    @classmethod
    def dead_letter_topic_name(cls):
        return None

    def run(self, content: dict, attributes: dict[str, str] | None = None):
        CalculatePriceTask.asap(**content)
        return self._metadata.custom_headers


class SayHelloTask(RoutineTask):
    def run(self, **kwargs):
        return {"message": "hello"}

    @classmethod
    def revert(cls, data: dict):
        return {"message": "goodbye"}


class SayHelloWithParamsTask(RoutineTask):
    def run(self, spell: str):
        return {"message": spell}

    @classmethod
    def revert(cls, data: dict):
        return {"message": "goodbye"}


class PublishPersonTask(ModelPublisherTask):
    @classmethod
    def build_message_content(cls, obj: Model, event: str, **kwargs) -> dict:
        return {"id": obj.pk, "name": obj.name}

    @classmethod
    def build_message_attributes(
        cls, obj: Model, event: str, **kwargs
    ) -> dict[str, str]:
        return {"any-custom-attribute": "yay!", "event": event}


class FindPrimeNumbersTask(Task):
    storage: list[int] = []

    @classmethod
    def reset(cls):
        cls.storage = []

    def run(self, quantity):
        if not isinstance(quantity, int):
            raise DiscardTaskException(
                "Can't find a non-integer amount of prime numbers",
                http_status_code=299,
                http_status_reason="Unretriable failure",
            )

        if len(self.storage) >= quantity:
            raise DiscardTaskException("Nothing to do here")

        return self._find_primes(quantity)

    @classmethod
    def _find_primes(cls, quantity: int) -> list[int]:
        if not cls.storage:
            cls.storage = [2]

        while len(cls.storage) < quantity:
            cls.storage.append(cls._find_next_prime(cls.storage[-1] + 1))

        return cls.storage

    @classmethod
    def _find_next_prime(cls, candidate: int) -> int:
        for prime in cls.storage:
            if candidate % prime == 0:
                return cls._find_next_prime(candidate=candidate + 1)

        return candidate


class DummyRoutineTask(RoutineTask):
    def run(self, **kwargs): ...

    @classmethod
    def revert(cls, **kwargs): ...


class MyMetadata(TaskMetadata): ...


class MyUnsupportedMetadata: ...
