from django.apps import AppConfig


class SampleAppConfig(AppConfig):
    name = "sample_app"

    def ready(self):
        from sample_app import tasks  # noqa: F401
