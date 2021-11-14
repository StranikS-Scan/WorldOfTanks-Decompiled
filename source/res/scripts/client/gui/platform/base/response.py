# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/platform/base/response.py
import httplib
import typing
import enum
from gui.shared.utils.requesters.abstract import Response

@enum.unique
class Codes(enum.IntEnum):
    SUCCESS = 0
    AUTHORIZATION_ERROR = 1
    POW_NOT_SOLVED = 2
    REQUEST_TIMEOUT = 3
    REQUEST_CANCELED = 4
    REQUEST_DESTROYED = 5
    HTTP_REQUEST_ERROR = 6
    UNEXPECTED_ERROR = 7
    SERVICE_NOT_STARTED = 8
    SERVICE_DISABLED = 9


class PlatformResponse(Response):

    @property
    def isCreated(self):
        return self.getExtraCode() == httplib.CREATED

    @classmethod
    def createRequestCanceled(cls):
        return cls.createError(Codes.REQUEST_CANCELED)

    @classmethod
    def createRequestDestroyed(cls):
        return cls.createError(Codes.REQUEST_DESTROYED)

    @classmethod
    def createServiceNotStarted(cls):
        return cls.createError(Codes.SERVICE_NOT_STARTED)

    @classmethod
    def createServiceDisabled(cls):
        return cls.createError(Codes.SERVICE_DISABLED)

    @classmethod
    def createUnexpectedError(cls, txtStr=''):
        return cls.createError(Codes.UNEXPECTED_ERROR, txtStr=txtStr)

    @classmethod
    def createAuthorizationError(cls):
        return cls.createError(Codes.AUTHORIZATION_ERROR)

    @classmethod
    def createPowNotSolved(cls):
        return cls.createError(Codes.POW_NOT_SOLVED)

    @classmethod
    def createRequestTimeout(cls):
        return cls.createError(Codes.REQUEST_TIMEOUT)

    @classmethod
    def createHttpError(cls, extraCode, txtStr='', data=None, headers=None):
        return cls.createError(Codes.HTTP_REQUEST_ERROR, extraCode, txtStr, data, headers)

    @classmethod
    def createSuccess(cls, extraCode=httplib.OK, txtStr='', data=None, headers=None):
        return cls._create(Codes.SUCCESS, extraCode, txtStr, data, headers)

    @classmethod
    def createError(cls, code, extraCode=httplib.SERVICE_UNAVAILABLE, txtStr='', data=None, headers=None):
        return cls._create(code, extraCode, txtStr, data, headers)

    def getData(self):
        return super(PlatformResponse, self).getData() or {}

    @classmethod
    def _create(cls, code, extraCode, txtStr='', data=None, headers=None):
        return cls(code.value, txtStr, data or {}, extraCode, headers or {})

    def _isError(self, errorType, *errorNames):
        return bool(set(errorNames) & set(self.getData().get('errors', {}).get(errorType, [])))
