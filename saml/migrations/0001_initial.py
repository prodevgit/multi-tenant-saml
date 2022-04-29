# Generated by Django 4.0.4 on 2022-04-27 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SAMLConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idp_entity_id', models.TextField()),
                ('idp_single_sign_on', models.TextField()),
                ('idp_single_logout', models.TextField()),
                ('saml_certificate', models.TextField()),
                ('sp_entity_id', models.TextField()),
                ('assertion_consumer_service', models.TextField()),
                ('sp_logout', models.TextField()),
            ],
            options={
                'verbose_name': 'SAML Configuration',
                'verbose_name_plural': 'SAML Configurations',
            },
        ),
    ]