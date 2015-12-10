from __future__ import absolute_import
from __future__ import unicode_literals

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from easy_pdf.rendering import render_to_pdf

from dojo.celery import app


def email_requester(report, uri, error=None):
    if error is None:
        subject = 'Report requested is ready'
        message = "Hello %s, \n\n The report you requested is ready and can be downloaded from %s.\n\n\nEnjoy, \n\n%s" \
                  "\n\n\n\nThis email was generated by DefectDojo." % (
                      report.requester.first_name, uri, settings.TEAM_NAME)
    else:
        subject = 'Report requested failed'
        message = "Hello %s, \n\n The report you requested has failed to generate.  Here are the details:\n\n %s" \
                  "\n\n\nEnjoy, \n\n%s\n\n\n\nThis email was generated by DefectDojo." % (
                      report.requester.first_name, error.message, settings.TEAM_NAME)
    send_mail(subject, message, settings.PORT_SCAN_RESULT_EMAIL_FROM, [report.requester.email],
              fail_silently=True)


@app.task(bind=True)
def async_pdf_report(self, report=None, filename='report.pdf', context={}, uri=None):
    try:
        report.task_id = async_pdf_report.request.id
        report.save()
        bytes = render_to_pdf('dojo/pdf_report.html', context)
        if report.file.name:
            with open(report.file.path, 'w') as f:
                f.write(bytes)
            f.close()
        else:
            f = ContentFile(bytes)
            report.file.save(filename, f)
        report.status = 'success'
        report.save()
        # email_requester(report, uri)
    except Exception as e:
        report.status = 'error'
        report.save()
        # email_requester(report, uri, error=e)
        raise e
    return True
