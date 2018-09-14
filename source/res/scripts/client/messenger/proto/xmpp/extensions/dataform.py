# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/xmpp/extensions/dataform.py
from collections import namedtuple
from messenger.proto.xmpp.extensions import PyExtension, SimpleExtension
from messenger.proto.xmpp.extensions.ext_constants import XML_NAME_SPACE as _NS
from messenger.proto.xmpp.extensions.ext_constants import XML_TAG_NAME as _TAG
from messenger.proto.xmpp.xmpp_constants import FORM_TYPE
from shared_utils import findFirst
Field = namedtuple('Field', ('type', 'var', 'value'))

class FieldElement(PyExtension):

    def __init__(self, field=None):
        super(FieldElement, self).__init__(_TAG.FIELD)
        if field is not None:
            self.setAttribute('type', field.type)
            self.setAttribute('var', field.var)
            self.setChild(SimpleExtension(_TAG.VALUE, field.value))
        return

    @classmethod
    def getDefaultData(cls):
        return None

    def parseTag(self, pyGlooxTag):
        fieldType = pyGlooxTag.findAttribute('type')
        fieldVar = pyGlooxTag.findAttribute('var')
        tag = findFirst(None, pyGlooxTag.filterXPath(self.getXPath(suffix='value')))
        if tag:
            value = tag.getCData()
        else:
            value = ''
        return Field(fieldType, fieldVar, value)


class DataForm(PyExtension):

    def __init__(self, fields=None):
        super(DataForm, self).__init__(_TAG.X)
        self.setXmlNs(_NS.DATA_FORMS)
        self._isEmpty = fields is None
        if not self._isEmpty:
            self.setAttribute('type', FORM_TYPE.SUBMIT)
            for field in fields:
                self.setChild(FieldElement(field))

        else:
            self.setChild(FieldElement())
        return

    @classmethod
    def getDefaultData(cls):
        return (FORM_TYPE.UNDEFINED, ())

    def getTag(self):
        if self._isEmpty:
            return ''
        else:
            return super(DataForm, self).getTag()

    def parseTag(self, pyGlooxTag):
        formType = pyGlooxTag.findAttribute('type')
        if formType not in FORM_TYPE.RANGE:
            formType = FORM_TYPE.UNDEFINED
        fields = []
        child = self.getChild(0)
        if child is not None:
            for tag in self._getChildTags(pyGlooxTag, 0):
                field = child.parseTag(tag)
                if field is not None:
                    fields.append(field)

        return (formType, fields)
