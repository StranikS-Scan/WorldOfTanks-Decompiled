# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/consumables_panel.py
import typing
import BigWorld
from functools import partial
from constants import EQUIPMENT_STAGES
from white_tiger.gui.Scaleform.daapi.view.meta.WhiteTigerConsumablesPanelMeta import WhiteTigerConsumablesPanelMeta
from gui.battle_control import avatar_getter
from gui.Scaleform.genConsts.ANIMATION_TYPES import ANIMATION_TYPES
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.gui_items import getKpiValueString
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import TOOLTIP_FORMAT
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control.battle_constants import DEVICE_STATE_DESTROYED
from gui.battle_control.controllers.consumables.equipment_ctrl import IgnoreEntitySelection
from gui.battle_control.controllers.consumables.equipment_ctrl import NeedEntitySelection
from white_tiger.gui.battle_control.controllers.equipment_items import isWtEventItem
from white_tiger.gui.battle_control.controllers.consumables.white_tiger_equipment_ctrl import WTEquipmentSound
from white_tiger.gui.Scaleform.genConsts.WHITE_TIGER_CONSUMABLES_PANEL_TAGS import WHITE_TIGER_CONSUMABLES_PANEL_TAGS as EQUIPMENT_TAGS
from white_tiger.gui.battle_control.white_tiger_battle_constants import VEHICLE_VIEW_STATE
from gui.Scaleform.genConsts.CONSUMABLES_PANEL_SETTINGS import CONSUMABLES_PANEL_SETTINGS
if typing.TYPE_CHECKING:
    from white_tiger.gui.battle_control.controllers.consumables.white_tiger_equipment_ctrl import WhiteTigerEquipmentController

def _isEquipmentAvailableToUse(eq):
    return eq.isAvailableToUse


class WhiteTigerConsumablesPanel(WhiteTigerConsumablesPanelMeta):
    _AMMO_START_IDX = 0
    _AMMO_END_IDX = 0
    _EQUIPMENT_START_IDX = 1
    _EQUIPMENT_END_IDX = 6
    _ORDERS_START_IDX = 8
    _ORDERS_END_IDX = 8
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(WhiteTigerConsumablesPanel, self).__init__()
        self._currentStage = EQUIPMENT_STAGES.UNAVAILABLE

    def _addEquipmentSlot(self, idx, intCD, item):
        self._cds[idx] = intCD
        if item is None:
            self.__createEmptyEquipmentSlot(idx)
        else:
            self.__setEquipmentSlot(idx, intCD, item)
        return

    def _buildEquipmentSlotTooltipText(self, item):
        descriptor = item.getDescriptor()
        reloadingTime = descriptor.cooldownSeconds
        body = descriptor.description
        if not {'repairkit', 'medkit'} & descriptor.tags:
            additionalStr = self.__getAdditionalTooltipBodyString(item)
            body = ''.join((body, additionalStr))
        if reloadingTime > 0:
            tooltipStr = R.strings.ingame_gui.consumables_panel.equipment.cooldownSeconds()
            cooldownSeconds = str(int(reloadingTime))
            paramsString = backport.text(tooltipStr, cooldownSeconds=cooldownSeconds)
            body = '\n\n'.join((body, paramsString))
        toolTip = TOOLTIP_FORMAT.format(descriptor.userString, body)
        return toolTip

    def _handleEquipmentPressed(self, intCD, entityName=None, idx=None):
        ctrl = self.sessionProvider.shared.equipments
        if ctrl is None:
            return
        elif not self.as_isVisibleS():
            return
        else:
            result, error = ctrl.changeSetting(intCD, entityName=entityName, avatar=BigWorld.player(), idx=idx)
            WTEquipmentSound.playPressed(ctrl.getEquipment(intCD), result)
            if not result and error:
                ctrl = self.sessionProvider.shared.messages
                if ctrl is not None:
                    ctrl.showVehicleError(error.key, error.ctx)
            return

    def __createEmptyEquipmentSlot(self, idx):
        bwKey, sfKey = self._genKey(idx)
        self.as_addWhiteTigerEquipmentSlotS(idx=idx, keyCode=bwKey, sfKeyCode=sfKey, quantity=0, timeRemaining=0, reloadingTime=0, iconPath='', tooltipText=backport.text(R.strings.ingame_gui.consumables_panel.equipment.tooltip.empty()), animation=ANIMATION_TYPES.NONE, tag=None, stage=EQUIPMENT_STAGES.NOT_RUNNING)
        snap = self._cds[self._EQUIPMENT_START_IDX:self._EQUIPMENT_END_IDX + 1]
        if snap == self._emptyEquipmentsSlice:
            self.as_showEquipmentSlotsS(False)
        return

    def __setEquipmentSlot(self, idx, intCD, item):
        tags = item.getTags()
        bwKey, sfKey = self._generateEquipmentKey(idx, item)
        if bwKey is not None:
            handler = self._getEquipmentKeyHandler(intCD, idx)
            if item.getQuantity() > 0:
                self._extraKeys[idx] = self._keys[bwKey] = handler
        descriptor = item.getDescriptor()
        quantity = item.getQuantity()
        timeRemaining = item.getTimeRemaining()
        reloadingTime = item.getTotalTime()
        iconPath = self._getEquipmentIcon(idx, item, descriptor.icon[0])
        animationType = item.getAnimationType()
        tag = EQUIPMENT_TAGS.TRIGGER_ITEM if EQUIPMENT_TAGS.TRIGGER_ITEM in tags else (EQUIPMENT_TAGS.BUILTIN_ITEM if EQUIPMENT_TAGS.BUILTIN_ITEM in tags else None)
        self.as_addWhiteTigerEquipmentSlotS(idx=idx, keyCode=bwKey, sfKeyCode=sfKey, quantity=quantity, timeRemaining=timeRemaining, reloadingTime=reloadingTime, iconPath=iconPath, tooltipText=self._getToolTipEquipmentSlot(item), animation=animationType, tag=tag, stage=item.getStage())
        self._updateEquipmentSlot(idx, item)
        return

    def __getAdditionalTooltipBodyString(self, item):
        attribs = R.strings.artefacts.dyn(item.getDescriptor().name)
        if not attribs:
            return ''
        resultStr = ''
        emptyStr = backport.text(R.strings.artefacts.empty())
        kpiArgs = {kpi.name:getKpiValueString(kpi, kpi.value) for kpi in item.getDescriptor().kpi}
        attributes = ('onUse', 'always', 'restriction')
        for atr in attributes:
            strText = backport.text(getattr(attribs, atr)(), **kpiArgs)
            if strText and strText != emptyStr:
                eq = R.strings.tooltips.equipment
                description = text_styles.middleTitle(backport.text(getattr(eq, atr)()))
                block = '\n'.join((description, strText))
                resultStr = '\n\n'.join((resultStr, block))

        return resultStr

    @property
    def __equipmentsCtrl(self):
        return self.__sessionProvider.shared.equipments

    def _populate(self):
        super(WhiteTigerConsumablesPanel, self)._populate()
        if self.__equipmentsCtrl is not None:
            self.__equipmentsCtrl.onChargeEquipmentCounterChanged += self.__onChargeCounterChanged
            self.__equipmentsCtrl.onDebuffEquipmentChanged += self.__onDebuffEquipmentChanged
        return

    def _dispose(self):
        super(WhiteTigerConsumablesPanel, self)._dispose()
        if self.__equipmentsCtrl is not None:
            self.__equipmentsCtrl.onChargeEquipmentCounterChanged -= self.__onChargeCounterChanged
            self.__equipmentsCtrl.onDebuffEquipmentChanged -= self.__onDebuffEquipmentChanged
        return

    def _updateEquipmentSlot(self, idx, item):
        self.as_setStageS(idx, item.getStage())
        self._currentStage = item.getStage()
        if self._currentStage == EQUIPMENT_STAGES.EXHAUSTED:
            self.as_hideGlowS(idx)
        super(WhiteTigerConsumablesPanel, self)._updateEquipmentSlot(idx, item)

    def _updateActivatedSlot(self, idx, item):
        self.as_setSelectedS(idx, self._currentStage == EQUIPMENT_STAGES.PREPARING)
        if self._currentStage == EQUIPMENT_STAGES.PREPARING:
            self.as_hideGlowS(idx)

    def __onChargeCounterChanged(self, intCD, charge, isVisible):
        if intCD not in self._cds:
            return
        idx = self._cds.index(intCD)
        self.as_setChargeProgressS(idx, charge, isVisible)

    def __onDebuffEquipmentChanged(self, intCD, isDebuffView):
        if intCD not in self._cds:
            return
        idx = self._cds.index(intCD)
        self.as_setDebuffViewS(idx, isDebuffView)

    def _canApplyingGlowEquipment(self, equipment):
        equipmentTags = equipment.getTags()
        if 'extinguisher' in equipmentTags or 'regenerationKit' in equipmentTags:
            correction = True
            entityName = None
        elif equipment.isAvatar() or isWtEventItem(equipment):
            correction = False
            entityName = None
        else:
            entityNames = [ name for name, state in equipment.getEntitiesIterator() if state == DEVICE_STATE_DESTROYED ]
            correction = hasDestroyed = len(entityNames)
            entityName = entityNames[0] if hasDestroyed else None
        canActivate, info = equipment.canActivate(entityName)
        infoType = type(info)
        return correction and (canActivate or infoType == NeedEntitySelection) or infoType == IgnoreEntitySelection

    def _onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.WT_INSPIRE:
            if value[0] == avatar_getter.getPlayerVehicleID() and avatar_getter.isVehicleAlive():
                self.as_setInspiredS(value[1])

    def _updateEquipmentGlow(self, idx, item):
        if item.isReusable or item.isAvatar() and item.getStage() != EQUIPMENT_STAGES.PREPARING:
            glowType = CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN_SPECIAL if item.isAvatar() else CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN
            if item.getStage() in (EQUIPMENT_STAGES.READY, EQUIPMENT_STAGES.DEPLOYING):
                self._showEquipmentGlow(idx, glowType)
        else:
            super(WhiteTigerConsumablesPanel, self)._updateEquipmentGlow(idx, item)

    def _showEquipmentGlow(self, equipmentIndex, glowType=CONSUMABLES_PANEL_SETTINGS.GLOW_ID_ORANGE):
        if BigWorld.player().isObserver():
            return
        if equipmentIndex in self._equipmentsGlowCallbacks:
            BigWorld.cancelCallback(self._equipmentsGlowCallbacks[equipmentIndex])
            del self._equipmentsGlowCallbacks[equipmentIndex]
        self.as_setGlowS(equipmentIndex, glowID=glowType)
        self._equipmentsGlowCallbacks[equipmentIndex] = BigWorld.callback(self._EQUIPMENT_GLOW_TIME, partial(self._hideEquipmentGlowCallback, equipmentIndex))
