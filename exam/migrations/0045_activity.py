# Generated by Django 4.1.2 on 2022-12-15 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0044_remove_result_grade'),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kind', models.CharField(max_length=50)),
                ('time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]