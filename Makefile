run:
	docker compose up -d --build

makemigrations:
	docker compose exec web python manage.py makemigrations

migrate:
	docker compose exec web python manage.py migrate

createsuperuser:
	docker compose exec web python manage.py createsuperuser --username root --email root@example.com 

glcloud_init:
	gcloud init
	gcloud auth application-default login
	cp ~/.config/gcloud/application_default_credentials.json .