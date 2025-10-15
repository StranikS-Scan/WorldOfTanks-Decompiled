# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/battle_control/controllers/consumables/equipment_ctrl.py
from gui.battle_control.controllers.consumables.equipment_ctrl import _TriggerItem, _ReplayItem, _OrderItem, InCooldownError, _ReplayMineFieldItem, _VisualScriptItem
from gui.shared.system_factory import registerEquipmentItem
from constants import EQUIPMENT_STAGES
from gui.Scaleform.genConsts.ANIMATION_TYPES import ANIMATION_TYPES
from gui.battle_control import avatar_getter
from aih_constants import CTRL_MODE_NAME

class _PortalBuffItem(_TriggerItem):

    @property
    def becomeActive(self):
        return self._prevStage == EQUIPMENT_STAGES.READY and self._stage in (EQUIPMENT_STAGES.ACTIVE, EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.EXHAUSTED)

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(_PortalBuffItem, self).update(quantity, stage, timeRemaining, totalTime)
        if stage in (EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.READY):
            self._totalTime = self._descriptor.cooldownSeconds
        elif stage == EQUIPMENT_STAGES.ACTIVE:
            self._totalTime = timeRemaining
        elif stage == EQUIPMENT_STAGES.PREPARING:
            self._totalTime = 0

    def getAnimationType(self):
        if self._stage == EQUIPMENT_STAGES.ACTIVE:
            return ANIMATION_TYPES.MOVE_ORANGE_BAR_DOWN | ANIMATION_TYPES.SHOW_COUNTER_GREEN | ANIMATION_TYPES.DARK_COLOR_TRANSFORM
        return ANIMATION_TYPES.MOVE_ORANGE_BAR_UP | ANIMATION_TYPES.SHOW_COUNTER_GREEN | ANIMATION_TYPES.DARK_COLOR_TRANSFORM if self._stage == EQUIPMENT_STAGES.COOLDOWN else super(_PortalBuffItem, self).getAnimationType()

    def getEntitiesIterator(self, avatar=None):
        return []


class VehicleChangeShotItem(_PortalBuffItem):

    @property
    def becomeActive(self):
        return self._prevStage == EQUIPMENT_STAGES.READY and self._stage == EQUIPMENT_STAGES.PREPARING


class PortalGuidedMissileItem(_PortalBuffItem):

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(PortalGuidedMissileItem, self).update(quantity, stage, timeRemaining, totalTime)
        if stage == EQUIPMENT_STAGES.PREPARING:
            self._totalTime = timeRemaining

    def getAnimationType(self):
        return ANIMATION_TYPES.MOVE_ORANGE_BAR_DOWN | ANIMATION_TYPES.SHOW_COUNTER_GREEN | ANIMATION_TYPES.DARK_COLOR_TRANSFORM if self._stage == EQUIPMENT_STAGES.PREPARING else super(PortalGuidedMissileItem, self).getAnimationType()


class SentryGunItem(_OrderItem):

    def getAimingControlMode(self):
        from AvatarInputHandler import MapCaseMode
        return MapCaseMode.ArcadeMapCaseControlMode

    @property
    def becomeAppointed(self):
        return self._prevStage in (EQUIPMENT_STAGES.READY, EQUIPMENT_STAGES.PREPARING) and self._needActivateMapCase() and self._stage in (EQUIPMENT_STAGES.ACTIVE, EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.EXHAUSTED)

    def getEntitiesIterator(self, avatar=None):
        return []


class BerserkPortal(_PortalBuffItem):
    pass


class MinefieldPortalItem(_OrderItem):

    def getAimingControlMode(self):
        from AvatarInputHandler import MapCaseMode
        return MapCaseMode.ArcadeMapCaseControlMode

    @property
    def becomeAppointed(self):
        return self._prevStage in (EQUIPMENT_STAGES.READY, EQUIPMENT_STAGES.PREPARING) and self._needActivateMapCase() and self._stage in (EQUIPMENT_STAGES.ACTIVE, EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.EXHAUSTED)

    def _getErrorMsg(self):
        return InCooldownError(self._descriptor.userString) if self._quantity else None

    def getEntitiesIterator(self, avatar=None):
        return []


class ShieldPortalItem(_PortalBuffItem):
    pass


class AbilityShotPortal(_PortalBuffItem):

    @property
    def becomeActive(self):
        return self._prevStage == EQUIPMENT_STAGES.PREPARING and self._stage in (EQUIPMENT_STAGES.ACTIVE, EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.EXHAUSTED)


class FireShotPortal(AbilityShotPortal):
    pass


class FrozenShotPortal(AbilityShotPortal):
    pass


class LaughShotPortal(AbilityShotPortal):
    pass


class CurseShotPortal(AbilityShotPortal):
    pass


class VehicleInfluenceZonePortal(_PortalBuffItem):
    pass


class PortalVehicleTrap(_VisualScriptItem):

    def _getAimingControlMode(self):
        from AvatarInputHandler import MapCaseMode
        return MapCaseMode.ArcadeMapCaseControlMode

    def _needActivateMapCase(self):
        inputHandler = avatar_getter.getInputHandler()
        return not inputHandler.ctrlModeName == CTRL_MODE_NAME.POSTMORTEM if inputHandler is not None else True

    @property
    def becomeReady(self):
        return self.isReady and self._serverPrevStage in (EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.NOT_RUNNING)

    @property
    def becomeAppointed(self):
        return self._prevStage in (EQUIPMENT_STAGES.READY, EQUIPMENT_STAGES.PREPARING) and self._needActivateMapCase() and self._stage in (EQUIPMENT_STAGES.ACTIVE, EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.EXHAUSTED)


class ReplayPortalVehicleTrap(_ReplayItem, PortalVehicleTrap):
    pass


class PortalDeathZoneItem(_OrderItem):

    def getMarker(self):
        pass


class PortalDeathZoneReplayItem(_ReplayItem):

    def getMarker(self):
        pass


def registerPortalEquipmentCtrls():
    registerEquipmentItem('vehicle_change_shot_portal', VehicleChangeShotItem, _ReplayItem)
    registerEquipmentItem('guided_missile_portal', PortalGuidedMissileItem, _ReplayItem)
    registerEquipmentItem('sentry_gun_portal', SentryGunItem, _ReplayItem)
    registerEquipmentItem('berserk_portal', BerserkPortal, _ReplayItem)
    registerEquipmentItem('minefield_portal', MinefieldPortalItem, _ReplayMineFieldItem)
    registerEquipmentItem('shield_portal', ShieldPortalItem, _ReplayItem)
    registerEquipmentItem('fire_shot_portal', FireShotPortal, _ReplayItem)
    registerEquipmentItem('frozen_shot_portal', FrozenShotPortal, _ReplayItem)
    registerEquipmentItem('laugh_shot_portal', LaughShotPortal, _ReplayItem)
    registerEquipmentItem('curse_shot_portal', CurseShotPortal, _ReplayItem)
    registerEquipmentItem('reload_aura_portal', VehicleInfluenceZonePortal, _ReplayItem)
    registerEquipmentItem('trap_portal', PortalVehicleTrap, ReplayPortalVehicleTrap)
    registerEquipmentItem('super_boss_aoe_portal', PortalDeathZoneItem, PortalDeathZoneReplayItem)
