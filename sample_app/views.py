from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from sample_app.tasks import CalculatePriceTask
from sample_app.models import TaskResult


class TriggerTaskView(View):
    def get(self, request, *args, **kwargs):
        context = {
            "tasks": TaskResult.objects.all().order_by("-created_at"),
        }
        return render(request, "trigger_task.html", context)

    def post(self, request, *args, **kwargs):
        price = request.POST.get("price")
        quantity = request.POST.get("quantity")
        discount = request.POST.get("discount")

        # Trigger the task
        response = CalculatePriceTask.asap(
            price=float(price), quantity=int(quantity), discount=float(discount)
        )

        return HttpResponse(
            f"<p>Task triggered successfully!</p><p>Task ID: {response.task_id}</p>"
        )
