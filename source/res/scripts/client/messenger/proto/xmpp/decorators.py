# Embedded file name: scripts/client/messenger/proto/xmpp/decorators.py
from debug_utils import LOG_WARNING
from messenger.ext import validateAccountName
from messenger.m_constants import CLIENT_ERROR_ID
from messenger.proto.shared_errors import ClientError
from messenger.proto.xmpp import xmpp_string_utils
from messenger.proto.xmpp.gloox_wrapper import ClientHolder

class QUERY_SIGN(object):
    DATABASE_ID = 1
    ACCOUNT_NAME = 2
    GROUP_NAME = 3
    OPT_GROUP_NAME = 4
    NOTE_TEXT = 5


def _validateDatabaseID(dbID):
    if not dbID:
        return ClientError(CLIENT_ERROR_ID.DBID_INVALID)
    else:
        return None


def _validateAccountName(name):
    errorID = validateAccountName(name)[1]
    if errorID:
        error = ClientError(errorID, strArg1=name)
    else:
        error = None
    return error


def _validateGroupName(name):
    return xmpp_string_utils.validateRosterItemGroup(name)[1]


def _validateOptionalGroupName(name):
    if name is not None:
        return _validateGroupName(name)
    else:
        return
        return


def _validateNoteText(note):
    return xmpp_string_utils.validateContactNote(note)[1]


_QUERY_SIGN_VALIDATORS = {QUERY_SIGN.DATABASE_ID: _validateDatabaseID,
 QUERY_SIGN.ACCOUNT_NAME: _validateAccountName,
 QUERY_SIGN.GROUP_NAME: _validateGroupName,
 QUERY_SIGN.OPT_GROUP_NAME: _validateOptionalGroupName,
 QUERY_SIGN.NOTE_TEXT: _validateNoteText}
_QUERY_OPT_SIGNS = (QUERY_SIGN.OPT_GROUP_NAME,)

class local_query(object):
    __slots__ = ('_sign',)

    def __init__(self, *args):
        super(local_query, self).__init__()
        self._sign = args[:]

    def __call__(self, func):

        def wrapper(*args, **kwargs):
            error = self._validate(*args)
            if not error:
                return func(*args, **kwargs)
            else:
                LOG_WARNING('Request is invalid', func.__name__, error)
                return (False, error)

        return wrapper

    def _validate(self, *args):
        if not self._sign:
            return None
        else:
            data = args[1:]
            if len(self._sign) > len(data):
                seq = list(self._sign)
                while len(seq) > len(data):
                    sign = seq.pop()
                    if sign not in _QUERY_OPT_SIGNS:
                        return ClientError(CLIENT_ERROR_ID.WRONG_ARGS)

            else:
                seq = self._sign[:]
            for index, sign in enumerate(seq):
                if sign in _QUERY_SIGN_VALIDATORS:
                    validator = _QUERY_SIGN_VALIDATORS[sign]
                    if validator and callable(validator):
                        error = validator(data[index])
                        if error:
                            return error

            return None


class xmpp_query(local_query, ClientHolder):

    def _validate(self, *args):
        client = self.client()
        if not client or not client.isConnected():
            return ClientError(CLIENT_ERROR_ID.NOT_CONNECTED)
        return super(xmpp_query, self)._validate(*args)
