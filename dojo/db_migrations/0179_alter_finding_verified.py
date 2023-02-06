# Generated by Django 4.1.5 on 2023-01-20 18:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dojo', '0178_alter_answer_polymorphic_ctype_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='finding',
            name='verified',
            field=models.BooleanField(default=False, help_text='Denotes if this flaw has been manually verified by the tester.', verbose_name='Verified'),
        ),
    ]
