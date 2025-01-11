# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/battle_control/controllers/equipment_ctrl.py
import logging
from gui.shared.system_factory import registerEquipmentItem
from gui.battle_control.controllers.consumables.equipment_ctrl import _VisualScriptItem, _ReplayItem, _ActivationError
_logger = logging.getLogger(__name__)

class _GrinchVisualScriptItem(_VisualScriptItem):
    __slots__ = ('_tags', '_descriptor', '_quantity', '_stage', '_prevStage', '_timeRemaining', '_prevQuantity', '_totalTime', '_isLocked', '_animationType', '_serverPrevStage', '_index')

    def __init__(self, *args):
        super(_GrinchVisualScriptItem, self).__init__(*args)
        component = self._getComponent()
        self._isLocked = component.locked if component else False

    def canActivate(self, entityName=None, avatar=None):
        if self._isLocked:
            _logger.debug('Equipment is locked %r :\nEquipment id=%s', self, self._descriptor.userString)
            return (False, _ActivationError('equipmentIsLocked', {'name': self._descriptor.userString}))
        return super(_GrinchVisualScriptItem, self).canActivate(entityName, avatar)

    def getQuantity(self):
        return self._quantity if not self._isLocked else 0

    def getTimeRemaining(self):
        return self._timeRemaining if not self._isLocked else 0

    def getTotalTime(self):
        return self._totalTime if not self._isLocked else 0

    def setLocked(self, isLocked):
        self._isLocked = isLocked

    def isLocked(self):
        return self._isLocked


class _GrinchAimingVisualScriptItem(_GrinchVisualScriptItem):

    def setLocked(self, isLocked):
        if isLocked:
            from AvatarInputHandler import MapCaseMode
            MapCaseMode.turnOffMapCase(self.getEquipmentID(), self._getAimingControlMode())
        super(_GrinchAimingVisualScriptItem, self).setLocked(isLocked)

    def _getAimingControlMode(self):
        from grinch.avatar_input_handler.grinch_map_case_mode import GrinchArcadeMapCaseControlMode
        return GrinchArcadeMapCaseControlMode


class _GrinchReplayItem(_ReplayItem):
    pass


def registerEquipmentsItems():
    registerEquipmentItem('builtinGrinchRepairkit', _GrinchVisualScriptItem, _GrinchReplayItem)
    registerEquipmentItem('builtinGrinchTurret', _GrinchAimingVisualScriptItem, _GrinchReplayItem)
    registerEquipmentItem('builtinGrinchHeal', _GrinchVisualScriptItem, _GrinchReplayItem)
    registerEquipmentItem('builtinGrinchStealth', _GrinchVisualScriptItem, _GrinchReplayItem)
    registerEquipmentItem('builtinGrinchFlare', _GrinchAimingVisualScriptItem, _GrinchReplayItem)
    registerEquipmentItem('builtinGrinchBlizzard', _GrinchVisualScriptItem, _GrinchReplayItem)
    registerEquipmentItem('builtinGrinchRage', _GrinchVisualScriptItem, _GrinchReplayItem)
    registerEquipmentItem('presentDrop', _GrinchAimingVisualScriptItem, _GrinchReplayItem)
