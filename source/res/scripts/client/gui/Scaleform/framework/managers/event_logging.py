# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/managers/event_logging.py
from constants import REQUEST_COOLDOWN
from debug_utils import LOG_DEBUG, LOG_WARNING
from gui.Scaleform.framework.entities.abstract.EventLogManagerMeta import EventLogManagerMeta
from gui.Scaleform.genConsts.EVENT_LOG_CONSTANTS import EVENT_LOG_CONSTANTS
import time
import BigWorld
import itertools
LOG_LIMIT = 70
PACKAGE_LIMIT = 70

class EventLogManager(EventLogManagerMeta):

    def __init__(self, isEnabled=False):
        super(EventLogManager, self).__init__()
        self.__currentPackage = []
        self.__sendList = []
        self.__lastSentTime = 0
        self.__onAutoSending = False
        self.__cbckIdx = None
        self.__packageIdx = 0
        self._isEnabled = isEnabled
        return

    def _populate(self):
        super(EventLogManager, self)._populate()
        self.as_setSystemEnabledS(self._isEnabled)

    def __sendPackageToServer(self, package):
        if self.__packageIdx <= PACKAGE_LIMIT:
            record = self.__encodeEvent(EVENT_LOG_CONSTANTS.SST_EVENT_LOG, EVENT_LOG_CONSTANTS.EVENT_TYPE_DATA, 0, self.__packageIdx)
            player = BigWorld.player()
            if player is not None and hasattr(player, 'logUXEvents') and not player.isDestroyed:
                self.__lastSentTime = BigWorld.time()
                self.__packageIdx += 1
                package.append(record)
                package = list(itertools.chain(*package))
                LOG_DEBUG('[EventLogging] PACKAGE event code', package)
                BigWorld.player().logUXEvents(package)
            else:
                LOG_DEBUG('[EventLogging] Records were lost', package)
        return

    def __sendSavedPackageToServer(self):
        self.__onAutoSending = False
        if len(self.__sendList) > 0:
            self.__sendPackageToServer(self.__sendList[0])
            del self.__sendList[0]
            if len(self.__sendList) > 0:
                BigWorld.callback(REQUEST_COOLDOWN.CLIENT_LOG_UX_DATA_COOLDOWN * 2, self.__sendSavedPackageToServer)
                self.__onAutoSending = True
        else:
            LOG_WARNING('saved packages are empty.')

    def __addPackageToSendList(self, package):
        if time.time() - self.__lastSentTime > REQUEST_COOLDOWN.CLIENT_LOG_UX_DATA_COOLDOWN and not self.__onAutoSending:
            self.__sendPackageToServer(package)
        else:
            self.__sendList.append(package)
            self.__cbckIdx = BigWorld.callback(REQUEST_COOLDOWN.CLIENT_LOG_UX_DATA_COOLDOWN * 2, self.__sendSavedPackageToServer)

    def __encodeEvent(self, subSystemType, eventType, uiid, arg):
        eventTypeIdx = EVENT_LOG_CONSTANTS.EVENT_TYPES.index(eventType)
        eventTypeId = EVENT_LOG_CONSTANTS.EVENT_CODES[eventTypeIdx]
        timestamp = int(BigWorld.time())
        return [timestamp,
         subSystemType,
         eventTypeId,
         uiid,
         arg]

    def logEvent(self, subSystemType, eventType, uiid, arg):
        if self.__packageIdx <= PACKAGE_LIMIT:
            eventRecord = self.__encodeEvent(subSystemType, eventType, uiid, arg)
            self.__currentPackage.append(eventRecord)
            if len(self.__currentPackage) >= LOG_LIMIT - 1:
                self.__addPackageToSendList(self.__currentPackage[-(LOG_LIMIT - 1):])
                self.__currentPackage = []

    def destroy(self):
        super(EventLogManager, self).destroy()
        self.__currentPackage = None
        if self.__cbckIdx is not None:
            BigWorld.cancelCallback(self.__cbckIdx)
        return
