# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/minimap/common.py
from functools import partial
import BigWorld
import Math
from gui.Scaleform.daapi.view.battle.shared.minimap import entries, settings
from gui.battle_control import g_sessionProvider
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
from gui.shared.utils.plugins import IPlugin

class SimplePlugin(IPlugin):
    __slots__ = ('__weakref__', '_arenaVisitor', '_arenaDP', '_ctrlMode', '_ctrlVehicleID')

    def __init__(self, parent):
        super(SimplePlugin, self).__init__(parent)
        self._arenaVisitor = None
        self._arenaDP = None
        self._ctrlMode = 'arcade'
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

    def clearCamera(self):
        pass

    def setSettings(self):
        pass

    def updateSettings(self, diff):
        pass

    def setAttentionToCell(self, x, y, isRightClick):
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
        return self._ctrlMode in ('strategic', 'mapcase')

    def _isInArcadeMode(self):
        return self._ctrlMode in ('arcade', 'sniper')

    def _isInPostmortemMode(self):
        return self._ctrlMode == 'postmortem'

    def _isInVideoMode(self):
        return self._ctrlMode == 'video'


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

    def _addEntryEx(self, uniqueID, symbol, container, matrix=None, active=False):
        if uniqueID in self._entries:
            return self._entries[uniqueID]
        else:
            entryID = self._addEntry(symbol, container, matrix=matrix, active=active)
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


class AttentionToCellPlugin(IntervalPlugin):
    __slots__ = ('_boundingBox',)

    def __init__(self, parent):
        super(AttentionToCellPlugin, self).__init__(parent)
        self._boundingBox = (Math.Vector2(0, 0), Math.Vector2(0, 0))

    def start(self):
        super(AttentionToCellPlugin, self).start()
        self._boundingBox = self._arenaVisitor.type.getBoundingBox()
        ctrl = g_sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onMinimapFeedbackReceived += self.__onMinimapFeedbackReceived
        return

    def stop(self):
        self._boundingBox = (Math.Vector2(0, 0), Math.Vector2(0, 0))
        ctrl = g_sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onMinimapFeedbackReceived -= self.__onMinimapFeedbackReceived
        super(AttentionToCellPlugin, self).stop()
        return

    def _doAttention(self, index, duration):
        raise NotImplementedError

    def __onMinimapFeedbackReceived(self, eventID, _, value):
        if eventID == FEEDBACK_EVENT_ID.MINIMAP_MARK_CELL:
            self._doAttention(*value)
