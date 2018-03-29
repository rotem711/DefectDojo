import logging

from auditlog.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.shortcuts import render

from dojo.filters import LogEntryFilter
from dojo.utils import get_page_items, add_breadcrumb

logger = logging.getLogger(__name__)


def action_history(request, cid, oid):
    try:
        ct = ContentType.objects.get_for_id(cid)
        obj = ct.get_object_for_this_type(pk=oid)
    except KeyError:
        raise Http404()

    history = LogEntry.objects.filter(content_type=ct,
                                      object_pk=obj.id).order_by('-timestamp')
    history = LogEntryFilter(request.GET, queryset=history)
    paged_history = get_page_items(request, history.qs, 25)
    add_breadcrumb(parent=obj, title="Action History", top_level=False,
                   request=request)
    return render(request, 'dojo/action_history.html',
                  {"history": paged_history,
                   "filtered": history,
                   "obj": obj,
                   })
