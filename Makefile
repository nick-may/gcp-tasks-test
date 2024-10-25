run_emulator:
	docker run -p 8123:8123 ghcr.io/aertje/cloud-tasks-emulator:latest -host 0.0.0.0 -port 8123

run_server:
	export GCP_LOCATION=us-east4 && \
	export GCP_PROJECT=my-project && \
	python manage.py runserver localhost:8080
