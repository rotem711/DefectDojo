# #  product
import logging
import sys
import json
import pprint
from datetime import datetime
from math import ceil

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from dojo.filters import ProductFilter, ProductFindingFilter
from dojo.forms import ProductForm, EngForm, DeleteProductForm
from dojo.models import Product_Type, Finding, Product, Engagement, ScanSettings, Risk_Acceptance, JIRA_Conf
from dojo.utils import get_page_items, add_breadcrumb, get_punchcard_data, get_system_setting
from dojo.models import *
from dojo.forms import *
from jira import JIRA
from dojo.tasks import *
from dojo.product import views as ds

logger = logging.getLogger(__name__)


@csrf_exempt
def webhook(request):
    if request.method == 'POST':
        parsed = json.loads(request.body)
        if 'issue' in parsed.keys():
            jid = parsed['issue']['id']
            jissue = JIRA_Issue.objects.get(jira_id=jid)
            if jissue.finding is not None:
                finding = jissue.finding
                resolved = True
                if parsed['issue']['fields']['resolution'] == None:
                    resolved = False
                if finding.active == resolved:
                    if finding.active:
                        now = timezone.now()
                        finding.active = False
                        finding.mitigated = now
                        finding.endpoints.clear()
                    else:
                        finding.active = True
                        finding.mitigated = None
                        finding.save()
                    finding.save()
            """
            if jissue.engagement is not None:
                eng = jissue.engagement
                if parsed['issue']['fields']['resolution'] != None:
                    eng.active = False
                    eng.status = 'Completed'
                    eng.save()
           """
        else:
            comment_text = parsed['comment']['body']
            commentor = parsed['comment']['updateAuthor']['displayName']
            jid = parsed['comment']['self'].split('/')[7]
            jissue = JIRA_Issue.objects.get(jira_id=jid)
            finding = jissue.finding
            new_note = Notes()
            new_note.entry = '(%s): %s' % (commentor, comment_text)
            new_note.author = User.objects.get(username='JIRA')
            new_note.save()
            finding.notes.add(new_note)
            finding.save()
    return HttpResponse('')


@user_passes_test(lambda u: u.is_staff)
def new_jira(request):
    if request.method == 'POST':
        jform = JIRAForm(request.POST, instance=JIRA_Conf())
        if jform.is_valid():
            try:
                jira_server = jform.cleaned_data.get('url').rstrip('/')
                jira = JIRA(server=jform.cleaned_data.get('url').rstrip('/'),
                            basic_auth=(jform.cleaned_data.get('username'), jform.cleaned_data.get('password')))
                new_j = jform.save(commit=False)
                new_j.url = jira_server
                new_j.save()
                messages.add_message(request,
                                     messages.SUCCESS,

                                     'JIRA Configuration Successfully Created.',
                                     extra_tags='alert-success')
                return HttpResponseRedirect(reverse('jira', ))
            except:
                messages.add_message(request,
                                     messages.ERROR,
                                     'Unable to authenticate. Please check the URL, username, and password.',
                                     extra_tags='alert-danger')
    else:
        jform = JIRAForm()
        add_breadcrumb(title="New Jira Configuration", top_level=False, request=request)
    return render(request, 'dojo/new_jira.html',
                  {'jform': jform})

@user_passes_test(lambda u: u.is_staff)
def edit_jira(request, jid):
    jira = JIRA_Conf.objects.get(pk=jid)
    if request.method == 'POST':
        jform = JIRAForm(request.POST, instance=jira)
        if jform.is_valid():
            try:
                jira_server = jform.cleaned_data.get('url').rstrip('/')
                jira = JIRA(server=jira_server,
                            basic_auth=(jform.cleaned_data.get('username'), jform.cleaned_data.get('password')))

                new_j = jform.save(commit=False)
                new_j.url = jira_server
                new_j.save()
                messages.add_message(request,
                                     messages.SUCCESS,
                                     'JIRA Configuration Successfully Created.',
                                     extra_tags='alert-success')
                return HttpResponseRedirect(reverse('jira', ))
            except:
                messages.add_message(request,
                                     messages.ERROR,
                                     'Unable to authenticate. Please check the URL, username, and password.',
                                     extra_tags='alert-danger')
    else:
        jform = JIRAForm(instance=jira)
    add_breadcrumb(title="Edit JIRA Configuration", top_level=False, request=request)

    return render(request,
                  'dojo/edit_jira.html',
                  {
                      'jform': jform,
                  })

@user_passes_test(lambda u: u.is_staff)
def delete_issue(request, find):
    j_issue = JIRA_Issue.objects.get(finding=find)
    jira = JIRA(server=jira_conf.url, basic_auth=(jira_conf.username, jira_conf.password))
    issue = jira.issue(j_issue.jira_id)
    issue.delete()

@user_passes_test(lambda u: u.is_staff)
def jira(request):
    confs = JIRA_Conf.objects.all()
    add_breadcrumb(title="JIRA List", top_level=not len(request.GET), request=request)
    return render(request,
                  'dojo/jira.html',
                  {'confs': confs,
                   })

@user_passes_test(lambda u: u.is_staff)
def delete_jira(request, tid):
    inst = get_object_or_404(JIRA_Conf, pk=tid)
    #eng = test.engagement
    #TODO Make Form
    form = DeleteJIRAConfForm(instance=inst)

    from django.contrib.admin.utils import NestedObjects
    from django.db import DEFAULT_DB_ALIAS

    collector = NestedObjects(using=DEFAULT_DB_ALIAS)
    collector.collect([inst])
    rels = collector.nested()

    if request.method == 'POST':
        if 'id' in request.POST and str(inst.id) == request.POST['id']:
            form = DeleteJIRAConfForm(request.POST, instance=inst)
            if form.is_valid():
                inst.delete()
                messages.add_message(request,
                                     messages.SUCCESS,
                                     'JIRA Conf and relationships removed.',
                                     extra_tags='alert-success')
                return HttpResponseRedirect(reverse('jira'))

    add_breadcrumb( title="Delete", top_level=False, request=request)
    return render(request, 'dojo/delete_jira.html',
                  {'inst': inst,
                   'form': form,
                   'rels': rels,
                   'deletable_objects': rels,
                   })

