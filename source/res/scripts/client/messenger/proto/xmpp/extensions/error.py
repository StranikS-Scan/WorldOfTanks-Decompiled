# Embedded file name: scripts/client/messenger/proto/xmpp/extensions/error.py
from messenger.proto.xmpp.extensions import PyExtension
from messenger.proto.xmpp.extensions.ext_constants import XML_TAG_NAME as _TAG
from messenger.proto.xmpp.extensions.ext_constants import XML_NAME_SPACE as _NS
from messenger.proto.xmpp.gloox_constants import ERROR_TYPE
STANZA_ERRORS = {'bad-request': ERROR_TYPE.MODIFY,
 'conflict': ERROR_TYPE.CANCEL,
 'feature-not-implemented': ERROR_TYPE.CANCEL,
 'forbidden': ERROR_TYPE.AUTH,
 'gone': ERROR_TYPE.MODIFY,
 'internal-server-error': ERROR_TYPE.WAIT,
 'item-not-found': ERROR_TYPE.CANCEL,
 'jid-malformed': ERROR_TYPE.MODIFY,
 'not-acceptable': ERROR_TYPE.MODIFY,
 'not-allowed': ERROR_TYPE.CANCEL,
 'not-authorized': ERROR_TYPE.AUTH,
 'policy-violation': ERROR_TYPE.CANCEL,
 'recipient-unavailable': ERROR_TYPE.WAIT,
 'redirect': ERROR_TYPE.WAIT,
 'registration-required': ERROR_TYPE.AUTH,
 'remote-server-not-found': ERROR_TYPE.CANCEL,
 'remote-server-timeout': ERROR_TYPE.WAIT,
 'resource-constraint': ERROR_TYPE.WAIT,
 'service-unavailable': ERROR_TYPE.CANCEL,
 'subscription-required': ERROR_TYPE.AUTH,
 'undefined-condition': ERROR_TYPE.CANCEL,
 'unexpected-request': ERROR_TYPE.WAIT}
DEF_STANZA_ERROR_CONDITION = 'undefined-condition'

class StanzaErrorExtension(PyExtension):

    def __init__(self, errorCondition = None, errorType = None):
        super(StanzaErrorExtension, self).__init__(_TAG.ERROR)
        if errorCondition:
            if not errorCondition in STANZA_ERRORS:
                raise AssertionError
                codeExt = PyExtension(errorCondition)
                codeExt.setXmlNs(_NS.STANZA_ERROR)
                self.setChild(codeExt)
                if not errorType:
                    errorType = STANZA_ERRORS[errorCondition]
            errorType and self.setAttribute('type', errorType)

    def parseTag(self, pyGlooxTag):
        errorType = pyGlooxTag.findAttribute('type')
        result = pyGlooxTag.filterXPath(self.getXPath(suffix='.'))
        if result:
            errorCondition = result[0].getTagName()
        else:
            errorCondition = DEF_STANZA_ERROR_CONDITION
        return (errorType, errorCondition)

    @classmethod
    def getDefaultData(cls):
        return (ERROR_TYPE.CANCEL, DEF_STANZA_ERROR_CONDITION)
