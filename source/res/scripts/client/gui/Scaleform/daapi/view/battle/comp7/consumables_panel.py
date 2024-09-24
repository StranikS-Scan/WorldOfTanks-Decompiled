# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/comp7/consumables_panel.py
import logging
from functools import partial
import typing
from Event import EventsSubscriber
from comp7_common import ROLE_EQUIPMENT_TAG
from constants import ROLE_TYPE_TO_LABEL, ARENA_PERIOD
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel
from gui.Scaleform.daapi.view.battle.shared.points_of_interest.poi_helpers import getPoiTypeByEquipment
from gui.Scaleform.genConsts.ANIMATION_TYPES import ANIMATION_TYPES
from gui.Scaleform.genConsts.CONSUMABLES_PANEL_SETTINGS import CONSUMABLES_PANEL_SETTINGS
from gui.battle_control import avatar_getter
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.tooltips.comp7_tooltips import getRoleEquipmentTooltipParts, getPoIEquipmentDescription
from gui.shared.tooltips.consumables_panel import TOOLTIP_FORMAT
from gui.shared.utils.functions import stripColorTagDescrTags
from helpers import dependency
from points_of_interest_shared import PoiType, POI_EQUIPMENT_TAG
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IComp7Controller
if typing.TYPE_CHECKING:
    from gui.battle_control.controllers.consumables.comp7_equipment_ctrl import Comp7EquipmentController
    from gui.battle_control.arena_info.interfaces import IComp7PrebattleSetupController
_logger = logging.getLogger(__name__)

class Comp7ConsumablesPanel(ConsumablesPanel):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __comp7Controller = dependency.descriptor(IComp7Controller)
    _ROLE_EQUIPMENT_IDX = 6
    _POI_EQUIPMENT_IDX = {PoiType.ARTILLERY: 7,
     PoiType.RECON: 8}
    _R_COMP7_EQUIPMENT_ICON = R.images.gui.maps.icons.roleSkills.c_43x43
    _R_POI_EQUIPMENT_ICON = R.images.gui.maps.icons.pointsOfInterest.equipments.c_43x43

    def __init__(self):
        super(Comp7ConsumablesPanel, self).__init__()
        self.__es = EventsSubscriber()

    @property
    def __equipmentsCtrl(self):
        return self.__sessionProvider.shared.equipments

    @property
    def __prebattleCtrl(self):
        return self.__sessionProvider.dynamic.comp7PrebattleSetup

    def _populate(self):
        super(Comp7ConsumablesPanel, self)._populate()
        if self.__equipmentsCtrl is not None:
            self.__es.subscribeToEvent(self.__equipmentsCtrl.onRoleEquipmentStateChanged, self.__updateRoleEquipmentState)
            self.__es.subscribeToEvent(self.__equipmentsCtrl.onRoleEquipmentCounterChanged, self.__updateRoleEquipmentCounter)
            self.__es.subscribeToEvent(self.__equipmentsCtrl.onEquipmentsCleared, self.__updatePrebattleRoleSkill)
        if self.__prebattleCtrl is not None:
            self.__es.subscribeToEvent(self.__prebattleCtrl.onSelectionConfirmed, self.__updatePrebattleRoleSkill)
        self.__updatePrebattleRoleSkill()
        return

    def _dispose(self):
        self.__es.unsubscribeFromAllEvents()
        super(Comp7ConsumablesPanel, self)._dispose()

    def _getEquipmentIconPath(self, item):
        if self.__isRoleEquipment(item):
            return self._R_COMP7_EQUIPMENT_ICON
        return self._R_POI_EQUIPMENT_ICON if self.__isPoiEquipment(item) else super(Comp7ConsumablesPanel, self)._getEquipmentIconPath(item)

    def _setEquipmentKeyHandler(self, item, bwKey, idx):
        if bwKey not in self._keys:
            handler = partial(self._handleEquipmentPressed, self._cds[idx])
            self._keys[bwKey] = handler

    def _onEquipmentAdded(self, intCD, item):
        if self.__isRoleEquipment(item):
            self.__addRoleEquipmentSlot(intCD, item)
        elif self.__isPoiEquipment(item):
            self.__addPoiEquipmentSlot(intCD, item)
        else:
            super(Comp7ConsumablesPanel, self)._onEquipmentAdded(intCD, item)

    def _updateEquipmentGlow(self, idx, item):
        if self.__isRoleEquipment(item) or self.__isPoiEquipment(item):
            if item.becomeReady:
                self.as_setGlowS(idx, glowID=CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN)
        else:
            super(Comp7ConsumablesPanel, self)._updateEquipmentGlow(idx, item)

    def _buildEquipmentSlotTooltipText(self, item):
        if self.__isRoleEquipment(item):
            return self.__buildRoleEquipmentTooltipText(item)
        return self.__buildPoIEquipmentTooltipText(item) if self.__isPoiEquipment(item) else super(Comp7ConsumablesPanel, self)._buildEquipmentSlotTooltipText(item)

    def __addRoleEquipmentSlot(self, intCD, item):
        idx = self._ROLE_EQUIPMENT_IDX
        equipment = item.getDescriptor()
        bwKey, sfKey = self._genKey(idx)
        self._cds[idx] = intCD
        self._extraKeys[idx] = self._keys[bwKey] = partial(self._handleEquipmentPressed, intCD)
        self.as_addRoleSkillSlotS(idx=idx, keyCode=bwKey, sfKeyCode=sfKey, quantity=item.getQuantity(), timeRemaining=item.getTimeRemaining(), reloadingTime=item.getTotalTime(), iconPath=self._getEquipmentIcon(idx, item, equipment.icon[0]), tooltipText=self._buildEquipmentSlotTooltipText(item), animation=item.getAnimationType())
        state = self.__equipmentsCtrl.getRoleEquipmentState()
        if state is not None:
            self.__updateRoleEquipmentState(state)
        counter = self.__equipmentsCtrl.getRoleEquipmentCounter()
        if counter is not None:
            self.__updateRoleEquipmentCounter(counter)
        return

    def __addPoiEquipmentSlot(self, intCD, item):
        equipment = item.getDescriptor()
        poiType = getPoiTypeByEquipment(equipment)
        idx = self._POI_EQUIPMENT_IDX.get(poiType)
        if idx is not None:
            self._addEquipmentSlot(idx, intCD, item)
        else:
            _logger.error('Unknown PointOfInterest Type: %s', poiType)
        return

    def __updateRoleEquipmentState(self, state, previousState=None):
        idx = self._ROLE_EQUIPMENT_IDX
        if self._cds[idx] is None:
            return
        else:
            self.as_setRoleSkillSlotProgressS(idx, level=state.level, progress=state.progress)
            self.__updateRoleSkillAvailability()
            return

    def __updateRoleEquipmentCounter(self, value):
        idx = self._ROLE_EQUIPMENT_IDX
        if self._cds[idx] is None:
            return
        else:
            self.as_setRoleSkillSlotCounterS(idx, value)
            self.__updateRoleSkillAvailability()
            return

    def __updateRoleSkillAvailability(self):
        idx = self._ROLE_EQUIPMENT_IDX
        intCD = self._cds[idx]
        if intCD is None:
            return
        else:
            item = self.__equipmentsCtrl.getEquipment(intCD)
            self.as_setItemQuantityInSlotS(idx, quantity=item.getQuantity() if item is not None else 0)
            return

    def __updatePrebattleRoleSkill(self):
        arena = avatar_getter.getArena()
        if arena is not None and arena.period < ARENA_PERIOD.BATTLE and self.__prebattleCtrl is not None:
            vehicle = self.__prebattleCtrl.getCurrentGUIVehicle()
            if vehicle is not None:
                roleName = ROLE_TYPE_TO_LABEL.get(vehicle.descriptor.role)
                roleSkillEquipment = self.__comp7Controller.getRoleEquipment(roleName)
                roleStartLevel = self.__comp7Controller.getEquipmentStartLevel(roleName)
                if roleSkillEquipment is None:
                    if not avatar_getter.isObserver():
                        _logger.error('No equipment found for vehicle %s', vehicle.descriptor.name)
                    return
                bwKey, sfKey = self._genKey(self._ROLE_EQUIPMENT_IDX)
                icon = backport.image(self._R_COMP7_EQUIPMENT_ICON.dyn(roleSkillEquipment.icon[0])())
                tooltip = TOOLTIP_FORMAT.format(*getRoleEquipmentTooltipParts(roleSkillEquipment, roleStartLevel))
                self.as_addRoleSkillSlotS(self._ROLE_EQUIPMENT_IDX, bwKey, sfKey, 0, 0.0, 0.0, icon, tooltip, ANIMATION_TYPES.NONE)
        return

    @staticmethod
    def __isRoleEquipment(item):
        return item is not None and ROLE_EQUIPMENT_TAG in item.getTags()

    @staticmethod
    def __isPoiEquipment(item):
        return item is not None and POI_EQUIPMENT_TAG in item.getTags()

    def __buildRoleEquipmentTooltipText(self, item):
        vehicle = self.__prebattleCtrl.getCurrentGUIVehicle()
        if vehicle is None:
            _logger.info('Cannot create roleEquipment tooltip, spawnInfoForVehicle not received yet')
            return
        else:
            roleName = ROLE_TYPE_TO_LABEL.get(vehicle.descriptor.role)
            startLevel = self.__comp7Controller.getEquipmentStartLevel(roleName)
            equipment = item.getDescriptor()
            header, body = getRoleEquipmentTooltipParts(equipment, startLevel)
            tooltip = TOOLTIP_FORMAT.format(header, body)
            return tooltip

    @staticmethod
    def __buildPoIEquipmentTooltipText(item):
        equipment = item.getDescriptor()
        description = getPoIEquipmentDescription(equipment)
        tooltip = TOOLTIP_FORMAT.format(equipment.userString, stripColorTagDescrTags(description))
        return tooltip
