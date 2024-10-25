# Generated by Django 5.1.2 on 2024-10-25 20:50

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sample_app', '0002_delete_person'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_id', models.CharField(max_length=255, unique=True)),
                ('task_name', models.CharField(max_length=255)),
                ('status', models.CharField(max_length=50)),
                ('result', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
