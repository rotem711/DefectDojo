__auther__ = "phylu"

from defusedxml import ElementTree as ET
from dojo.models import Finding


class CrashtestSecurityXmlParser(object):
    """
    The objective of this class is to parse an xml file generated by the crashtest security suite.

    @param xml_output A proper xml generated by the crashtest security suite
    """

    def __init__(self, xml_output, test):
        tree = self.parse_xml(xml_output)

        if tree:
            self.items = self.get_items(tree, test)
        else:
            self.items = []

    def parse_xml(self, xml_output):
        """
        Open and parse an xml file.

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

        items = list()

        # Get all testcases
        for node in tree.findall('.//testcase'):

            # Only failed test cases contain a finding
            failure = node.find('failure')
            if failure is None:
                continue
            
            title = node.get('name')
            description = failure.get('message')
            severity = failure.get('type')

            find = Finding(title=title,
                          description=description,
                          test=test,
                          severity=severity,
                          mitigation="No mitigation provided",
                          active=False,
                          verified=False,
                          false_p=False,
                          duplicate=False,
                          out_of_scope=False,
                          mitigated=None,
                          impact="No impact provided",
                          numerical_severity=Finding.get_numerical_severity(severity))
            items.append(find)

        return items