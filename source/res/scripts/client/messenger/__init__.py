# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/__init__.py
from __future__ import absolute_import
import typing
from external_strings_utils import unicode_from_utf8
from soft_exception import SoftException
from messenger.m_settings import MessengerSettings

class error(SoftException):
    pass


g_settings = MessengerSettings()

def normalizeGroupId(itemId):
    return unicode_from_utf8(itemId)[1] if isinstance(itemId, bytes) else itemId
