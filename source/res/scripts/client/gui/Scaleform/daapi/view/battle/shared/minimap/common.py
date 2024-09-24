# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/minimap/common.py
from functools import partial
import BigWorld
from aih_constants import CTRL_MODE_NAME
from gui.Scaleform.daapi.view.battle.shared.minimap import entries, settings
from gui.shared.utils.plugins import IPlugin
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider

class SimplePlugin(IPlugin):
    __slots__ = ('__weakref__', '_arenaVisitor', '_arenaDP', '_ctrlMode', '_ctrlVehicleID')
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, parent):
        super(SimplePlugin, self).__init__(parent)
        self._arenaVisitor = None
        self._arenaDP = None
        self._ctrlMode = CTRL_MODE_NAME.ARCADE
        self._ctrlVehicleID = 0
        return

    def init(self, arenaVisitor, arenaDP):
        super(SimplePlugin, self).init()
        self._arenaVisitor = arenaVisitor
        self._arenaDP = arenaDP

    def fini(self):
        self._arenaVisitor = None
        self._arenaDP = None
        super(SimplePlugin, self).fini()
        return

    def initControlMode(self, mode, available):
        self._ctrlMode = mode

    def updateControlMode(self, mode, vehicleID):
        self._ctrlMode = mode
        self._ctrlVehicleID = vehicleID

    def setSettings(self):
        pass

    def updateSettings(self, diff):
        pass

    def onMinimapClicked(self, x, y, buttonIdx, minimapScaleIndex):
        pass

    def applyNewSize(self, sizeIndex):
        pass

    def _addEntry(self, symbol, container, matrix=None, active=False, transformProps=settings.TRANSFORM_FLAG.DEFAULT):
        return self._parentObj.addEntry(symbol, container, matrix=matrix, active=active, transformProps=transformProps)

    def _delEntry(self, entryID):
        self._parentObj.delEntry(entryID)

    def _invoke(self, entryID, name, *args):
        self._parentObj.invoke(entryID, name, *args)

    def _move(self, entryID, container):
        self._parentObj.move(entryID, container)

    def _setMatrix(self, entryID, matrix):
        self._parentObj.setMatrix(entryID, matrix)

    def _setActive(self, entryID, active):
        self._parentObj.setActive(entryID, active)

    def _playSound2D(self, soundID):
        self._parentObj.playSound2D(soundID)

    def _isInStrategicMode(self):
        return self._ctrlMode in (CTRL_MODE_NAME.STRATEGIC,
         CTRL_MODE_NAME.ARTY,
         CTRL_MODE_NAME.MAP_CASE,
         CTRL_MODE_NAME.MAP_CASE_EPIC)

    def _isInArcadeMode(self):
        return self._ctrlMode in (CTRL_MODE_NAME.ARCADE, CTRL_MODE_NAME.SNIPER)

    def _isInArtyMode(self):
        return self._ctrlMode == CTRL_MODE_NAME.ARTY

    def _isInPostmortemMode(self):
        return self._ctrlMode == CTRL_MODE_NAME.POSTMORTEM

    def _isInVideoMode(self):
        return self._ctrlMode in (CTRL_MODE_NAME.VIDEO, CTRL_MODE_NAME.DEATH_FREE_CAM)

    def _isInFreeCamMode(self):
        return self._ctrlMode in CTRL_MODE_NAME.DEATH_FREE_CAM

    def _isInRespawnDeath(self):
        return self._ctrlMode == CTRL_MODE_NAME.RESPAWN_DEATH

    def _isVehicleSelection(self):
        return self._ctrlMode == CTRL_MODE_NAME.VEHICLES_SELECTION


class EntriesPlugin(SimplePlugin):
    __slots__ = ('_entries', '_clazz')

    def __init__(self, parent, clazz=None):
        super(EntriesPlugin, self).__init__(parent)
        self._entries = {}
        self._clazz = clazz or entries.MinimapEntry

    def stop(self):
        while self._entries:
            _, model = self._entries.popitem()
            model.clear()

        super(EntriesPlugin, self).stop()

    def _addEntryEx(self, uniqueID, symbol, container, matrix=None, active=False, transformProps=settings.TRANSFORM_FLAG.DEFAULT):
        if uniqueID in self._entries:
            return self._entries[uniqueID]
        else:
            entryID = self._addEntry(symbol, container, matrix=matrix, active=active, transformProps=transformProps)
            if entryID:
                model = self._clazz(entryID, active, matrix)
                self._entries[uniqueID] = model
            else:
                model = None
            return model

    def _delEntryEx(self, uniqueID):
        if uniqueID not in self._entries:
            return False
        model = self._entries.pop(uniqueID)
        self._delEntry(model.getID())
        model.clear()
        return True

    def _setMatrixEx(self, uniqueID, matrix):
        model = self._entries.get(uniqueID, None)
        if model:
            self._setMatrix(model.getID(), matrix)
        return

    def _invokeEx(self, uniqueID, name, *args):
        model = self._entries.get(uniqueID)
        if model:
            self._invoke(model.getID(), name, *args)

    def _setActiveEx(self, uniqueID, isActive):
        model = self._entries.get(uniqueID)
        if model:
            self._setActive(model.getID(), isActive)


class IntervalPlugin(EntriesPlugin):
    __slots__ = ('__callbackIDs',)

    def __init__(self, parent):
        super(IntervalPlugin, self).__init__(parent)
        self.__callbackIDs = {}

    def stop(self):
        while self.__callbackIDs:
            _, callbackID = self.__callbackIDs.popitem()
            if callbackID is not None:
                BigWorld.cancelCallback(callbackID)

        super(IntervalPlugin, self).stop()
        return

    def _clearCallback(self, uniqueID):
        callbackID = self.__callbackIDs.pop(uniqueID, None)
        if callbackID is not None:
            BigWorld.cancelCallback(callbackID)
        return

    def _setCallback(self, uniqueID, interval):
        self._clearCallback(uniqueID)
        self.__callbackIDs[uniqueID] = BigWorld.callback(interval, partial(self._handleCallback, uniqueID))

    def _handleCallback(self, uniqueID):
        self.__callbackIDs[uniqueID] = None
        self._delEntryEx(uniqueID)
        return

    def _isCallbackExisting(self, uniqueID):
        return self.__callbackIDs[uniqueID] is not None if uniqueID in self.__callbackIDs else False

    def _clearAllCallbacks(self):
        for key in self.__callbackIDs:
            self._delEntryEx(key)

        self.__callbackIDs.clear()

    def _killOtherCallbacks(self, uniqueID):
        toKill = []
        for key in self.__callbackIDs:
            if key != uniqueID:
                self._delEntryEx(key)
                self.__callbackIDs[key] = None
                toKill.append(key)

        for i in range(0, len(toKill)):
            del self.__callbackIDs[toKill[i]]

        return


class BaseAreaMarkerEntriesPlugin(EntriesPlugin):
    __slots__ = ()

    def createMarker(self, uniqueID, symbol, container, matrix, active):
        model = self._addEntryEx(uniqueID, symbol, container, matrix=matrix, active=active)
        return True if model is not None else False

    def deleteMarker(self, uniqueID):
        self._delEntryEx(uniqueID)

    def setMatrix(self, uniqueID, matrix):
        self._setMatrixEx(uniqueID, matrix)

    def update(self, *args, **kwargs):
        super(BaseAreaMarkerEntriesPlugin, self).update()

    def invoke(self, uniqueID, name, *args):
        self._invokeEx(uniqueID, name, *args)

    def setActive(self, uniqueID, isActive):
        self._setActiveEx(uniqueID, isActive)
