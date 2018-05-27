import xml.etree.ElementTree as XMLTree

from couchpotato.core.logger import CPLog

log = CPLog(__name__)


class RSS(object):

    def get_text_elements(self, xml, path):
        """ Find elements and return tree"""

        textelements = []
        try:
            elements = xml.findall(path)
        except:
            return
        for element in elements:
            textelements.append(element.text)
        return textelements

    def get_elements(self, xml, path):

        elements = None
        try:
            elements = xml.findall(path)
        except:
            pass

        return elements

    def get_element(self, xml, path):
        """ Find element and return text"""

        try:
            return xml.find(path)
        except:
            return

    def get_text_element(self, xml, path):
        """ Find element and return text"""

        try:
            return xml.find(path).text
        except:
            return

    def get_items(self, data, path='channel/item'):
        try:
            return XMLTree.parse(data).findall(path)
        except Exception as e:
            log.error('Error parsing RSS. %s', e)
            return []
