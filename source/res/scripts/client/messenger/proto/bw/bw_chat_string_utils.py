# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/bw/bw_chat_string_utils.py
from external_strings_utils import unicode_from_utf8
from gui.Scaleform.locale.MESSENGER import MESSENGER
from messenger.proto.bw.errors import I18nError
from messenger.proto.bw.limits import CHANNEL_LIMIT

def validateUserRoomName(name):
    name = name.strip()
    if not name or len(unicode_from_utf8(name)[0]) not in xrange(CHANNEL_LIMIT.NAME_MIN_LENGTH, CHANNEL_LIMIT.NAME_MAX_LENGTH + 1):
        error = I18nError(MESSENGER.CLIENT_ERROR_LIMIT_CHANNEL_INVALID_LENGTH, int32Arg1=CHANNEL_LIMIT.NAME_MIN_LENGTH, int32Arg2=CHANNEL_LIMIT.NAME_MAX_LENGTH)
        return (name, error)
    else:
        return (name, None)


def validateUserRoomPwd(password, isRetype=False):
    if not password:
        if isRetype:
            key = MESSENGER.CLIENT_ERROR_CHANNEL_RETYPE_EMPTY
        else:
            key = MESSENGER.CLIENT_ERROR_CHANNEL_PASSWORD_EMPTY
        return ('', I18nError(key))
    else:
        pwdRange = xrange(CHANNEL_LIMIT.PWD_MIN_LENGTH, CHANNEL_LIMIT.PWD_MAX_LENGTH + 1)
        if not isRetype and len(unicode_from_utf8(password)[0]) not in pwdRange:
            error = I18nError(MESSENGER.CLIENT_ERROR_LIMIT_PWD_INVALID_LENGTH, int32Arg1=CHANNEL_LIMIT.PWD_MIN_LENGTH, int32Arg2=CHANNEL_LIMIT.PWD_MAX_LENGTH)
            return ('', error)
        return (password, None)


def validateUserRoomPwdPair(password, retype):
    password, error = validateUserRoomPwd(password, isRetype=False)
    if error is not None:
        return ('', error)
    retype, error = validateUserRoomPwd(retype, isRetype=True)
    if error is not None:
        return ('', error)
    elif password != retype:
        error = I18nError(MESSENGER.CLIENT_ERROR_CHANNEL_PASSWORDS_NOT_EQUALS)
        return ('', error)
    else:
        return (password, None)
