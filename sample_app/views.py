import json
from django.db import transaction

from django.http import JsonResponse, Http404
from django.views import View

from sample_app import models
from sample_app import tasks

class PersonCreateView(View):
    def post(self, request, *args, **kwargs):
        person = models.Person(**json.loads(request.body))
        person.save()
        return JsonResponse(status=201, data={"status": "published", "pk": person.pk})


class PersonReplaceView(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        payload = json.loads(request.body)
        person_to_replace_id = payload.pop("person_to_replace_id")

        person = models.Person(**payload)
        person.save()

        try:
            to_delete = models.Person.objects.get(pk=person_to_replace_id)
            to_delete.delete()
        except models.Person.DoesNotExist:
            raise Http404()

        return JsonResponse(status=201, data={"status": "published", "pk": person.pk})
    
class TestView(View):
    def get(self, request, *args, **kwargs):
        response = tasks.CalculatePriceTask.asap(price=10, quantity=2, discount=0.1)
        print(response)
        return JsonResponse(data={"status": "ok"})