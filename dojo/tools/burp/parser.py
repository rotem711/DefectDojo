"""
Faraday Penetration Test IDE
Copyright (C) 2013  Infobyte LLC (http://www.infobytesec.com/)
See the file 'doc/LICENSE' for the license information

"""
from __future__ import with_statement

import re
from defusedxml import ElementTree as ET

import html2text

from dojo.models import Finding, Endpoint

__author__ = "Francisco Amato"
__copyright__ = "Copyright (c) 2013, Infobyte LLC"
__credits__ = ["Francisco Amato"]
__license__ = ""
__version__ = "1.0.0"
__maintainer__ = "Francisco Amato"
__email__ = "famato@infobytesec.com"
__status__ = "Development"


class BurpXmlParser(object):
    """
    The objective of this class is to parse an xml file generated by the burp tool.

    TODO: Handle errors.
    TODO: Test burp output version. Handle what happens if the parser doesn't support it.
    TODO: Test cases.

    @param xml_output A proper xml generated by burp
    @param test A Dojo Test object
    """

    def __init__(self, xml_output, test):
        self.target = None
        self.port = "80"
        self.host = None

        tree = self.parse_xml(xml_output)
        if tree:
            self.items = [data for data in self.get_items(tree, test)]
        else:
            self.items = []

    def parse_xml(self, xml_output):
        """
        Open and parse an xml file.

        TODO: Write custom parser to just read the nodes that we need instead of
        reading the whole file.

        @return xml_tree An xml tree instance. None if error.
        """
        try:
            tree = ET.parse(xml_output)
        except SyntaxError as se:
            raise se

        return tree

    def get_items(self, tree, test):
        """
        @return items A list of Host instances
        """
        bugtype = ""
        items = {}

        for node in tree.findall('issue'):
            item = get_item(node, test)
            dupe_key = str(item.url) + item.severity + item.title
            if dupe_key in items:
                items[dupe_key].unsaved_endpoints = items[dupe_key].unsaved_endpoints + item.unsaved_endpoints

                # make sure only unique endpoints are retained
                unique_objs = []
                new_list = []
                for o in items[dupe_key].unsaved_endpoints:
                    if o.__unicode__() in unique_objs:
                        continue
                    new_list.append(o)
                    unique_objs.append(o.__unicode__())

                items[dupe_key].unsaved_endpoints = new_list
            else:
                items[dupe_key] = item

        return items.values()


def get_attrib_from_subnode(xml_node, subnode_xpath_expr, attrib_name):
    """
    Finds a subnode in the item node and the retrieves a value from it

    @return An attribute value
    """
    global ETREE_VERSION
    node = None

    if ETREE_VERSION[0] <= 1 and ETREE_VERSION[1] < 3:

        match_obj = re.search("([^\@]+?)\[\@([^=]*?)=\'([^\']*?)\'", subnode_xpath_expr)
        if match_obj is not None:
            node_to_find = match_obj.group(1)
            xpath_attrib = match_obj.group(2)
            xpath_value = match_obj.group(3)
            for node_found in xml_node.findall(node_to_find):
                if node_found.attrib[xpath_attrib] == xpath_value:
                    node = node_found
                    break
        else:
            node = xml_node.find(subnode_xpath_expr)

    else:
        node = xml_node.find(subnode_xpath_expr)

    if node is not None:
        return node.get(attrib_name)

    return None


def do_clean(value):
    myreturn = ""
    if value is not None:
        if len(value) > 0:
            for x in value:
                myreturn += x.text
    return myreturn


def get_item(item_node, test):
    host_node = item_node.findall('host')[0]

    url = host_node.text
    rhost = re.search(
            "(http|https|ftp)\://([a-zA-Z0-9\.\-]+(\:[a-zA-Z0-9\.&amp;%\$\-]+)*@)*((25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9])\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[0-9])|localhost|([a-zA-Z0-9\-]+\.)*[a-zA-Z0-9\-]+\.(com|edu|gov|int|mil|net|org|biz|arpa|info|name|pro|aero|coop|museum|[a-zA-Z]{2}))[\:]*([0-9]+)*([/]*($|[a-zA-Z0-9\.\,\?\'\\\+&amp;%\$#\=~_\-]+)).*?$",
            url)
    protocol = rhost.group(1)
    host = rhost.group(4)

    port = 80
    if protocol == 'https':
        port = 443

    if rhost.group(11) is not None:
        port = rhost.group(11)

    ip = host_node.get('ip')
    url = item_node.get('url')
    path = item_node.findall('path')[0].text
    location = item_node.findall('location')[0].text

    request = item_node.findall('./requestresponse/request')[0].text if len(
            item_node.findall('./requestresponse/request')) > 0 else ""
    response = item_node.findall('./requestresponse/response')[0].text if len(
            item_node.findall('./requestresponse/response')) > 0 else ""

    try:
        dupe_endpoint = Endpoint.objects.get(protocol=protocol,
                                             host=host + (":" + port) if port is not None else "",
                                             path=path,
                                             query=None,
                                             fragment=None,
                                             product=test.engagement.product)
    except:
        dupe_endpoint = None

    if not dupe_endpoint:
        endpoint = Endpoint(protocol=protocol,
                            host=host + (":" + str(port)) if port is not None else "",
                            path=path,
                            query=None,
                            fragment=None,
                            product=test.engagement.product)
    else:
        endpoint = dupe_endpoint

    if ip:
        try:
            dupe_endpoint = Endpoint.objects.get(protocol=None,
                                                 host=ip,
                                                 path=None,
                                                 query=None,
                                                 fragment=None,
                                                 product=test.engagement.product)
        except:
            dupe_endpoint = None

        if not dupe_endpoint:
            endpoints = [endpoint, Endpoint(host=ip, product=test.engagement.product)]
        else:
            endpoints = [endpoint, dupe_endpoint]

    background = do_clean(item_node.findall('issueBackground'))
    if background:
        background = html2text.html2text(background)

    detail = do_clean(item_node.findall('issueDetail'))
    if detail:
        detail = html2text.html2text(detail)

    remediation = do_clean(item_node.findall('remediationBackground'))
    if remediation:
        remediation = html2text.html2text(remediation)

    references = do_clean(item_node.findall('references'))
    if references:
        references = html2text.html2text(references)

    severity = item_node.findall('severity')[0].text

    # Finding and Endpoint objects returned have not been saved to the database
    finding = Finding(title=item_node.findall('name')[0].text,
                      url=url,
                      test=test,
                      severity=severity,
                      description=background + "\n\n" + detail,
                      mitigation=remediation,
                      references=references,
                      active=False,
                      verified=False,
                      false_p=False,
                      duplicate=False,
                      out_of_scope=False,
                      mitigated=None,
                      impact="No impact provided",
                      numerical_severity=Finding.get_numerical_severity(severity))
    finding.unsaved_endpoints = endpoints
    finding.unsaved_request = request
    finding.unsaved_response = response

    return finding
