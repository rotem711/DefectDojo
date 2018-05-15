#!/usr/bin/env python

from setuptools import setup

setup(
    name='DefectDojo',
    version='1.3.0',
    author='Greg Anderson',
    description="Tool for managing vulnerability engagements",
    install_requires=[
        'celery>=4.1',
        'defusedxml',
        'Django==1.11.11',
        'django-auditlog',
        'django-custom-field',
        'django-filter==1.0.4',
        'django-imagekit',
        'django-multiselectfield',
        'django-overextends==0.4.3',  # Required for extensions
        'django-polymorphic==1.2',
        'django-rest-swagger==2.1.2',
        'django-slack',
        'django-tagging',
        'django-tastypie-swagger',
        'django-tastypie>=0.12.2',
        'django-watson==1.3.1',
        'django-rest-swagger==2.1.2',
        'djangorestframework==3.7.7',
        'gunicorn>=19.1.1',
        'html2text',
        'humanize',
        'jira',
        'lxml',
        'mysqlclient==1.3.12',
        'pdfkit==0.6.1',
        'Pillow',
        'psycopg2',
        'pycrypto',
        'python-nmap>=0.3.4',
        'pytz>=2013.9',
        'requests>=2.2.1',
        'sqlalchemy',  # Required by Celery broker transport
        'supervisor',
        'vobject',
        'html2text',
        'django-watson',
        'celery>=4.1',
        'kombu>=4.1',
        'sqlalchemy',
        'django-polymorphic==1.2',
        'pdfkit==0.6.1',
        'django-overextends',
        'defusedxml',
        'django-tagging',
        'django-custom-field',
        'django-imagekit',
        'jira',
        'pycrypto',
        'lxml',
        'psycopg2',
        'django-multiselectfield',
        'pbr',
        'django-slack',
        'asteval',
        'Markdown>=2.6.11',
        'pandas>=0.22.0',
    ],

    dependency_links=[
        "https://github.com/grendel513/python-pdfkit/tarball/master#egg=pdfkit-0.5.0",
    ],
    url='https://github.com/owasp/django-DefectDojo'
)
