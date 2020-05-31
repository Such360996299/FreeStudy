# Generated by Django 2.2 on 2020-03-23 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0001_initial'),
        ('courses', '0002_auto_20200323_1552'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseresource',
            name='is_teacher',
            field=models.ManyToManyField(to='organizations.Teacher', verbose_name='讲师'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='is_teacher',
            field=models.ManyToManyField(to='organizations.Teacher', verbose_name='讲师'),
        ),
        migrations.AddField(
            model_name='video',
            name='is_teacher',
            field=models.ManyToManyField(to='organizations.Teacher', verbose_name='讲师'),
        ),
    ]
