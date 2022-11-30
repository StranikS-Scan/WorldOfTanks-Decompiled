# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/notification/BaseNotificationView.py
from debug_utils import LOG_ERROR
_NOT_ID_TUPLE_INDEX = 2

class BaseNotificationView(object):

    def __init__(self, model=None):
        super(BaseNotificationView, self).__init__()
        self._model = None
        self.__flashIDCounter = 0
        self.__flashIdToEntityIdMap = {}
        self.__entityIdToFlashIdMap = {}
        self.setModel(model)
        return

    def setModel(self, value):
        self._model = value

    def cleanUp(self):
        self._model = None
        return

    def _getFlashID(self, notificationInfo):
        if notificationInfo in self.__entityIdToFlashIdMap:
            return self.__entityIdToFlashIdMap[notificationInfo]
        self.__flashIDCounter += 1
        self.__flashIdToEntityIdMap[self.__flashIDCounter] = notificationInfo
        self.__entityIdToFlashIdMap[notificationInfo] = self.__flashIDCounter
        return self.__flashIDCounter

    def _getNotificationID(self, flashId):
        if flashId in self.__flashIdToEntityIdMap:
            return self.__flashIdToEntityIdMap[flashId][_NOT_ID_TUPLE_INDEX]
        LOG_ERROR('Wrong notification ScaleForm id', flashId)
