# Generated by Django 3.2.21 on 2024-07-10 10:36

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_alter_country_name'),
        ('bot', '0002_auto_20240611_2327'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChannelCountry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enabled_regions', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=16), blank=True, default=list, size=None)),
                ('status', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='ChannelIncidentType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.BooleanField(default=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='regionstatus',
            name='channel',
        ),
        migrations.RemoveField(
            model_name='regionstatus',
            name='region',
        ),
        migrations.RemoveField(
            model_name='typestatus',
            name='channel',
        ),
        migrations.RemoveField(
            model_name='typestatus',
            name='incident_type',
        ),
        migrations.RemoveField(
            model_name='channel',
            name='country',
        ),
        migrations.RemoveField(
            model_name='channel',
            name='region',
        ),
        migrations.RemoveField(
            model_name='channel',
            name='type',
        ),
        migrations.DeleteModel(
            name='CountryStatus',
        ),
        migrations.DeleteModel(
            name='RegionStatus',
        ),
        migrations.DeleteModel(
            name='TypeStatus',
        ),
        migrations.AddField(
            model_name='channelincidenttype',
            name='channel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incident_types', to='bot.channel'),
        ),
        migrations.AddField(
            model_name='channelincidenttype',
            name='incident_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.incidenttype'),
        ),
        migrations.AddField(
            model_name='channelcountry',
            name='channel_incident_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to='bot.channelincidenttype'),
        ),
        migrations.AddField(
            model_name='channelcountry',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.country'),
        ),
        migrations.AlterUniqueTogether(
            name='channelincidenttype',
            unique_together={('channel', 'incident_type')},
        ),
        migrations.AlterUniqueTogether(
            name='channelcountry',
            unique_together={('channel_incident_type', 'country')},
        ),
    ]
