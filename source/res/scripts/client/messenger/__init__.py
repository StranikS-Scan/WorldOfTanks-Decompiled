# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/__init__.py
import typing
from types import StringType
from external_strings_utils import unicode_from_utf8
from soft_exception import SoftException
from messenger.m_settings import MessengerSettings
if typing.TYPE_CHECKING:
    from types import UnicodeType, IntType

class error(SoftException):
    pass


g_settings = MessengerSettings()

def normalizeGroupId(itemId):
    return unicode_from_utf8(itemId)[0] if isinstance(itemId, StringType) else itemId
