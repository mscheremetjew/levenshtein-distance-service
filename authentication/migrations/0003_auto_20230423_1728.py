import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    replaces = [
        ("django_celery_results", "0003_auto_20230423_1728"),
    ]

    def __init__(self, name, app_label):
        super(Migration, self).__init__(name, app_label)
        self.app_label = "django_celery_results"

    dependencies = [("authentication", "0002_alter_user_managers"), ("django_celery_results", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="taskresult",
            name="task_creator",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
