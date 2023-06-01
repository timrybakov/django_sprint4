# Generated by Django 3.2.16 on 2023-06-01 20:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_alter_post_author'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='post',
            managers=[
            ],
        ),
        migrations.AlterField(
            model_name='post',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='categories', to='blog.category', verbose_name='Категория'),
        ),
    ]
