# #  findings
import base64
import logging
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from pytz import timezone

from dojo.filters import OpenFindingFilter, \
    OpenFingingSuperFilter, AcceptedFingingSuperFilter, \
    ClosedFingingSuperFilter
from dojo.forms import NoteForm, CloseFindingForm, FindingForm
from dojo.models import Product_Type, Finding, Notes, \
    Risk_Acceptance, BurpRawRequestResponse
from dojo.utils import get_page_items, add_breadcrumb

localtz = timezone(settings.TIME_ZONE)

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S',
    filename=settings.DOJO_ROOT + '/../django_app.log',
)
logger = logging.getLogger(__name__)

"""
Greg
Status: in prod
on the nav menu open findings returns all the open findings for a given
engineer
"""


def open_findings(request):
    findings = Finding.objects.filter(mitigated__isnull=True,
                                      verified=True,
                                      false_p=False,
                                      duplicate=False,
                                      out_of_scope=False)
    if request.user.is_staff:
        findings = OpenFingingSuperFilter(request.GET, queryset=findings, user=request.user)
    else:
        findings = findings.filter(test__engagement__product__authorized_users__in=[request.user])
        findings = OpenFindingFilter(request.GET, queryset=findings, user=request.user)

    title_words = [word
                   for finding in findings
                   for word in finding.title.split() if len(word) > 2]

    title_words = sorted(set(title_words))
    paged_findings = get_page_items(request, findings, 25)

    product_type = None
    if 'test__engagement__product__prod_type' in request.GET:
        p = request.GET.getlist('test__engagement__product__prod_type', [])
        if len(p) == 1:
            product_type = get_object_or_404(Product_Type, id=p[0])

    add_breadcrumb(title="Open findings", top_level='all' in request.GET, request=request)

    return render(request,
                  'dojo/open_findings.html',
                  {"findings": paged_findings,
                   "filtered": findings,
                   "title_words": title_words,
                   })


"""
Greg, Jay
Status: in prod
on the nav menu accpted findings returns all the accepted findings for a given
engineer
"""


@user_passes_test(lambda u: u.is_staff)
def accepted_findings(request):
    user = request.user

    fids = [finding.id for ra in
            Risk_Acceptance.objects.all()
            for finding in ra.accepted_findings.all()]
    findings = Finding.objects.filter(id__in=fids)
    findings = AcceptedFingingSuperFilter(request.GET, queryset=findings)
    title_words = [word for ra in
                   Risk_Acceptance.objects.all()
                   for finding in ra.accepted_findings.order_by(
            'title').values('title').distinct()
                   for word in finding['title'].split() if len(word) > 2]

    title_words = sorted(set(title_words))
    paged_findings = get_page_items(request, findings, 25)

    add_breadcrumb(title="Accepted findings", top_level='all' in request.GET, request=request)

    return render(request,
                  'dojo/accepted_findings.html',
                  {"findings": paged_findings,
                   "filtered": findings,
                   "title_words": title_words,
                   })


@user_passes_test(lambda u: u.is_staff)
def closed_findings(request):
    findings = Finding.objects.filter(mitigated__isnull=False)
    findings = ClosedFingingSuperFilter(request.GET, queryset=findings)
    title_words = [word
                   for finding in findings
                   for word in finding.title.split() if len(word) > 2]

    title_words = sorted(set(title_words))
    paged_findings = get_page_items(request, findings, 25)
    add_breadcrumb(title="Closed findings", top_level='all' in request.GET, request=request)
    return render(request,
                  'dojo/closed_findings.html',
                  {"findings": paged_findings,
                   "filtered": findings,
                   "title_words": title_words,
                   })


def view_finding(request, fid):
    finding = get_object_or_404(Finding, id=fid)
    user = request.user
    if (user.is_staff
        or user in finding.test.engagement.product.authorized_users.all()):
        pass  # user is authorized for this product
    else:
        raise PermissionDenied

    notes = finding.notes.all()

    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            new_note = form.save(commit=False)
            new_note.author = request.user
            new_note.date = datetime.now(tz=localtz)
            new_note.save()
            finding.notes.add(new_note)
            finding.last_reviewed = new_note.date
            finding.last_reviewed_by = user
            finding.save()
            form = NoteForm()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Note saved.',
                                 extra_tags='alert-success')
    else:
        form = NoteForm()

    try:
        reqres = BurpRawRequestResponse.objects.get(finding=finding)
        burp_request = base64.b64decode(reqres.burpRequestBase64)
        burp_response = base64.b64decode(reqres.burpResponseBase64)
    except:
        reqres = None
        burp_request = None
        burp_response = None

    add_breadcrumb(parent=finding, top_level=False, request=request)
    return render(request, 'dojo/view_finding.html',
                  {'finding': finding,
                   'burp_request': burp_request,
                   'burp_response': burp_response,
                   'user': user, 'notes': notes, 'form': form})


@user_passes_test(lambda u: u.is_staff)
def close_finding(request, fid):
    finding = get_object_or_404(Finding, id=fid)
    # in order to close a finding, we need to capture why it was closed
    # we can do this with a Note
    if request.method == 'POST':
        form = CloseFindingForm(request.POST)

        if form.is_valid():
            now = datetime.now(tz=localtz)
            new_note = form.save(commit=False)
            new_note.author = request.user
            new_note.date = now
            new_note.save()
            finding.notes.add(new_note)
            finding.active = False
            finding.mitigated = now
            finding.mitigated_by = request.user
            finding.last_reviewed = finding.mitigated
            finding.last_reviewed_by = request.user
            finding.endpoints.clear()
            finding.save()

            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Finding closed.',
                                 extra_tags='alert-success')
            return HttpResponseRedirect(reverse('view_test', args=(finding.test.id,)))

    else:
        form = CloseFindingForm()

    add_breadcrumb(parent=finding, title="Close", top_level=False, request=request)
    return render(request, 'dojo/close_finding.html',
                  {'finding': finding,
                   'user': request.user, 'form': form})


@user_passes_test(lambda u: u.is_staff)
def reopen_finding(request, fid):
    finding = get_object_or_404(Finding, id=fid)
    finding.active = True
    finding.mitigated = None
    finding.mitigated_by = request.user
    finding.last_reviewed = finding.mitigated
    finding.last_reviewed_by = request.user
    finding.save()

    messages.add_message(request,
                         messages.SUCCESS,
                         'Finding closed.',
                         extra_tags='alert-success')
    return HttpResponseRedirect(reverse('view_finding', args=(finding.id,)))


@user_passes_test(lambda u: u.is_staff)
def delete_finding(request, fid):
    finding = get_object_or_404(Finding, id=fid)
    tid = finding.test.id
    finding.delete()
    messages.add_message(request,
                         messages.SUCCESS,
                         'Finding deleted successfully.',
                         extra_tags='alert-success')
    return HttpResponseRedirect(reverse('view_test', args=(tid,)))


@user_passes_test(lambda u: u.is_staff)
def edit_finding(request, fid):
    finding = get_object_or_404(Finding, id=fid)
    form = FindingForm(instance=finding)
    form_error = False
    if request.method == 'POST':
        form = FindingForm(request.POST, instance=finding)
        if form.is_valid():
            new_finding = form.save(commit=False)
            new_finding.test = finding.test
            new_finding.numerical_severity = Finding.get_numerical_severity(
                new_finding.severity)
            if new_finding.false_p or new_finding.active is False:
                new_finding.mitigated = datetime.now(tz=localtz)
                new_finding.mitigated_by = request.user
            if new_finding.active is True:
                new_finding.false_p = False
                new_finding.mitigated = None
                new_finding.mitigated_by = None

            new_finding.endpoints = form.cleaned_data['endpoints']
            new_finding.last_reviewed = datetime.now(tz=localtz)
            new_finding.last_reviewed_by = request.user
            new_finding.save()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Finding saved successfully.',
                                 extra_tags='alert-success')
            return HttpResponseRedirect(reverse('view_finding', args=(new_finding.id,)))
        else:
            messages.add_message(request,
                                 messages.ERROR,
                                 'There appears to be errors on the form, please correct below.',
                                 extra_tags='alert-danger')
            form_error = True

    if form_error and 'endpoints' in form.cleaned_data:
        form.fields['endpoints'].queryset = form.cleaned_data['endpoints']
    else:
        form.fields['endpoints'].queryset = finding.endpoints.all()

    add_breadcrumb(parent=finding, title="Edit", top_level=False, request=request)
    return render(request, 'dojo/edit_findings.html',
                  {'form': form,
                   'finding': finding,
                   })


@user_passes_test(lambda u: u.is_staff)
def touch_finding(request, fid):
    finding = get_object_or_404(Finding, id=fid)
    finding.last_reviewed = datetime.now(tz=localtz)
    finding.last_reviewed_by = request.user
    finding.save()
    return HttpResponseRedirect(reverse('view_finding', args=(finding.id,)))


@user_passes_test(lambda u: u.is_staff)
def mktemplate(request, fid):
    finding = get_object_or_404(Finding, id=fid)
    finding.is_template = True
    finding.save()
    messages.add_message(request,
                         messages.SUCCESS,
                         'Finding template added successfully.',
                         extra_tags='alert-success')
    return HttpResponseRedirect(reverse('view_finding', args=(finding.id,)))


@user_passes_test(lambda u: u.is_staff)
def delete_finding_note(request, tid, nid):
    note = get_object_or_404(Notes, id=nid)
    if note.author == request.user:
        finding = get_object_or_404(Finding, id=tid)
        finding.notes.remove(note)
        note.delete()
        messages.add_message(request,
                             messages.SUCCESS,
                             'Note removed.',
                             extra_tags='alert-success')
        return view_finding(request, tid)
    return HttpResponseForbidden()
