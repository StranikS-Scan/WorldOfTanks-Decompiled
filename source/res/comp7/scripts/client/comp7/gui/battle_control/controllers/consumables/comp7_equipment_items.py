# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/battle_control/controllers/consumables/comp7_equipment_items.py
import logging
import BigWorld
from PlayerEvents import g_playerEvents
from comp7_common_const import ROLE_EQUIPMENT_TAG
from constants import EQUIPMENT_STAGES
from gui.Scaleform.genConsts.BATTLE_MARKERS_CONSTS import BATTLE_MARKERS_CONSTS
from gui.battle_control.controllers.consumables.equipment_ctrl import _ActivationError, _ReplayItem, _VisualScriptItem
_logger = logging.getLogger(__name__)

class Comp7RoleSkillUnavailable(_ActivationError):

    def __new__(cls, name):
        return super(Comp7RoleSkillUnavailable, cls).__new__(cls, 'comp7RoleSkillUnavailable', {'name': name})

    def __init__(self, name):
        super(Comp7RoleSkillUnavailable, self).__init__('comp7RoleSkillUnavailable', {'name': name})


class Comp7RoleSkillAlreadyActivated(_ActivationError):

    def __new__(cls, name):
        return super(Comp7RoleSkillAlreadyActivated, cls).__new__(cls, 'comp7RoleSkillAlreadyActivated', {'name': name})

    def __init__(self, name):
        super(Comp7RoleSkillAlreadyActivated, self).__init__('comp7RoleSkillAlreadyActivated', {'name': name})


class Comp7RoleSkillCooldown(_ActivationError):

    def __new__(cls, name):
        return super(Comp7RoleSkillCooldown, cls).__new__(cls, 'comp7RoleSkillCooldown', {'name': name})

    def __init__(self, name):
        super(Comp7RoleSkillCooldown, self).__init__('comp7RoleSkillCooldown', {'name': name})


class _RoleSkillVSItem(_VisualScriptItem):
    __FORBIDDEN_STAGES_TO_ACTIVATE = (EQUIPMENT_STAGES.COOLDOWN,
     EQUIPMENT_STAGES.ACTIVE,
     EQUIPMENT_STAGES.UNAVAILABLE,
     EQUIPMENT_STAGES.STARTUP_COOLDOWN)

    def update(self, quantity, stage, timeRemaining, totalTime):
        prevQuantity = self._prevQuantity
        super(_RoleSkillVSItem, self).update(quantity, stage, timeRemaining, totalTime)
        self._prevQuantity = prevQuantity
        self._quantity = self.getQuantity()

    def _getErrorMsg(self):
        if self._stage == EQUIPMENT_STAGES.UNAVAILABLE:
            return Comp7RoleSkillUnavailable(self._descriptor.userString)
        if self._stage == EQUIPMENT_STAGES.ACTIVE:
            return Comp7RoleSkillAlreadyActivated(self._descriptor.userString)
        return Comp7RoleSkillCooldown(self._descriptor.userString) if self._stage in (EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.STARTUP_COOLDOWN) else super(_RoleSkillVSItem, self)._getErrorMsg()

    def getQuantity(self):
        component = self._getComponent()
        if component is None:
            return 0
        else:
            available, _ = self.canActivate()
            return int(available)

    def canActivate(self, entityName=None, avatar=None):
        return (False, self._getErrorMsg()) if self._stage in self.__FORBIDDEN_STAGES_TO_ACTIVATE else super(_RoleSkillVSItem, self).canActivate(entityName, avatar)


class _DeferredRoleSkillVSItem(_RoleSkillVSItem):
    _ACTIVATION_COOLDOWN = 0.2
    _lastActivationTime = 0

    def __init__(self, *args):
        super(_DeferredRoleSkillVSItem, self).__init__(*args)
        g_playerEvents.onRoundFinished += self.__onRoundFinished

    def clear(self):
        super(_DeferredRoleSkillVSItem, self).clear()
        g_playerEvents.onRoundFinished -= self.__onRoundFinished

    def canActivate(self, entityName=None, avatar=None):
        result, error = super(_DeferredRoleSkillVSItem, self).canActivate(entityName, avatar)
        if result and avatar:
            currentTime = BigWorld.time()
            if currentTime - self._lastActivationTime < self._ACTIVATION_COOLDOWN:
                return (False, None)
            self._lastActivationTime = currentTime
        return (result, error)

    def __onRoundFinished(self, *_):
        from AvatarInputHandler import MapCaseMode
        MapCaseMode.turnOffMapCase(self.getEquipmentID(), self._getAimingControlMode())


class _RoleSkillReconVSItem(_DeferredRoleSkillVSItem):

    def _getAimingControlMode(self):
        from AvatarInputHandler.MapCaseMode import MapCaseControlMode
        return MapCaseControlMode


class _RoleSkillArtyVSItem(_DeferredRoleSkillVSItem):

    def _getAimingControlMode(self):
        from AvatarInputHandler.MapCaseMode import MapCaseControlMode
        return MapCaseControlMode

    def getMarker(self):
        pass

    def getMarkerColor(self):
        return BATTLE_MARKERS_CONSTS.COLOR_GREEN


def _comp7ItemFactory(descriptor, quantity, stage, timeRemaining, totalTime, tag=None):
    if descriptor.name.startswith('comp7_recon'):
        itemClass = _RoleSkillReconVSItem
    elif descriptor.name.startswith('comp7_redline'):
        itemClass = _RoleSkillArtyVSItem
    else:
        itemClass = _RoleSkillVSItem
    return itemClass(descriptor, quantity, stage, timeRemaining, totalTime, tag)


EQUIPMENT_TAG_TO_ITEM = {(ROLE_EQUIPMENT_TAG,): _comp7ItemFactory}

class _ReplayRoleSkillVSItem(_ReplayItem, _RoleSkillVSItem):

    def getAnimationType(self):
        return _RoleSkillVSItem.getAnimationType(self)

    def update(self, quantity, stage, timeRemaining, totalTime):
        _ReplayItem.update(self, quantity, stage, timeRemaining, totalTime)
        _RoleSkillVSItem.update(self, quantity, stage, timeRemaining, totalTime)

    def canActivate(self, entityName=None, avatar=None):
        return _RoleSkillVSItem.canActivate(self, entityName, avatar)

    def _getErrorMsg(self):
        return _RoleSkillVSItem._getErrorMsg(self)


class _ReplayRoleSkillArtyVSItem(_ReplayRoleSkillVSItem):

    def getMarker(self):
        pass


def _replayComp7ItemFactory(descriptor, quantity, stage, timeRemaining, totalTime, tag=None):
    if descriptor.name.startswith('comp7_redline'):
        itemClass = _ReplayRoleSkillArtyVSItem
    else:
        itemClass = _ReplayRoleSkillVSItem
    return itemClass(descriptor, quantity, stage, timeRemaining, totalTime, tag)


REPLAY_EQUIPMENT_TAG_TO_ITEM = {(ROLE_EQUIPMENT_TAG,): _replayComp7ItemFactory}
