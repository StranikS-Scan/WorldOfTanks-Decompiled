# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/white_tiger/consumables_panel.py
import BigWorld
from items import vehicles
from gui import GUI_SETTINGS
from constants import EQUIPMENT_STAGES, SHELL_TYPES
from gui.battle_control.battle_constants import DEVICE_STATE_DESTROYED
from gui.battle_control.controllers.consumables.equipment_ctrl import IgnoreEntitySelection, NeedEntitySelection
from gui.Scaleform.genConsts.ANIMATION_TYPES import ANIMATION_TYPES
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.gui_items import getKpiValueString
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import TOOLTIP_FORMAT, TOOLTIP_NO_BODY_FORMAT
from gui.Scaleform.genConsts.CONSUMABLES_PANEL_SETTINGS import CONSUMABLES_PANEL_SETTINGS
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from white_tiger.gui.battle_control.controllers.consumables.equipment_items import isWtEventItem
from white_tiger.gui.Scaleform.daapi.view.meta.WTConsumablesPanelMeta import WTConsumablesPanelMeta
from white_tiger.gui.battle_control.controllers.consumables.equipment_sound import WtEquipmentSound

class WhiteTigerConsumablesPanel(WTConsumablesPanelMeta):
    _AMMO_START_IDX = 0
    _AMMO_END_IDX = 0
    _EQUIPMENT_START_IDX = 1
    _EQUIPMENT_END_IDX = 6
    _ORDERS_START_IDX = 8
    _ORDERS_END_IDX = 8
    _BOSS_EQUIPMENT_TO_INDEX = {'builtinInstantStunShoot_wt': _EQUIPMENT_START_IDX,
     'builtinImpulse_wt': _EQUIPMENT_START_IDX + 1,
     'builtinTeleport_wt': _EQUIPMENT_START_IDX + 2,
     'builtinHyperion_wt': _EQUIPMENT_START_IDX + 3}
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(WhiteTigerConsumablesPanel, self).__init__()
        self._currentStage = EQUIPMENT_STAGES.UNAVAILABLE

    def _isBossAbility(self, item):
        return item.getDescriptor().name in self._BOSS_EQUIPMENT_TO_INDEX and 'eventItem' in item.getDescriptor().tags

    def _onEquipmentAdded(self, intCD, item):
        if self._isBossAbility(item):
            self._addBossEquipmentSlot(intCD, item)
        else:
            super(WhiteTigerConsumablesPanel, self)._onEquipmentAdded(intCD, item)

    def _addBossEquipmentSlot(self, intCD, item):
        idx = self._BOSS_EQUIPMENT_TO_INDEX[item.getDescriptor().name]
        self._addEquipmentSlot(idx, intCD, item)

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

    def _handleEquipmentPressed(self, intCD, entityName=None):
        ctrl = self.sessionProvider.shared.equipments
        if ctrl is None:
            return
        elif not self.as_isVisibleS():
            return
        else:
            result, error = ctrl.changeSetting(intCD, entityName=entityName, avatar=BigWorld.player())
            WtEquipmentSound.playPressed(ctrl.getEquipment(intCD), result)
            if not result and error:
                ctrl = self.sessionProvider.shared.messages
                if ctrl is not None:
                    ctrl.showVehicleError(error.key, error.ctx)
            else:
                self._collapseEquipmentSlot()
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

    def _populate(self):
        super(WhiteTigerConsumablesPanel, self)._populate()
        equipmentCtrl = self.sessionProvider.shared.equipments
        if equipmentCtrl is not None:
            equipmentCtrl.onChargeEquipmentCounterChanged += self.__onChargeCounterChanged
            equipmentCtrl.onDebuffEquipmentChanged += self.__onDebuffEquipmentChanged
        return

    def _dispose(self):
        super(WhiteTigerConsumablesPanel, self)._dispose()
        equipmentCtrl = self.sessionProvider.shared.equipments
        if equipmentCtrl is not None:
            equipmentCtrl.onChargeEquipmentCounterChanged -= self.__onChargeCounterChanged
            equipmentCtrl.onDebuffEquipmentChanged -= self.__onDebuffEquipmentChanged
        return

    def _updateEquipmentSlot(self, idx, item):
        self._currentStage = item.getStage()
        if self._currentStage == EQUIPMENT_STAGES.COOLDOWN:
            if item.getDescriptor().name == 'builtinHyperion_wt':
                item.setAnimationType(ANIMATION_TYPES.SHOW_COUNTER_GREEN)
            else:
                item.setAnimationType(ANIMATION_TYPES.MOVE_ORANGE_BAR_UP | ANIMATION_TYPES.SHOW_COUNTER_ORANGE | ANIMATION_TYPES.DARK_COLOR_TRANSFORM)
        elif self._currentStage == EQUIPMENT_STAGES.ACTIVE:
            item.setAnimationType(ANIMATION_TYPES.MOVE_GREEN_BAR_DOWN)
        super(WhiteTigerConsumablesPanel, self)._updateEquipmentSlot(idx, item)
        if self._currentStage == EQUIPMENT_STAGES.EXHAUSTED:
            self.as_hideGlowS(idx)

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

    def _updateEquipmentGlow(self, idx, item):
        if item.isReusable or item.isAvatar() and item.getStage() != EQUIPMENT_STAGES.PREPARING:
            glowType = CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN_SPECIAL if item.isAvatar() else CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN
            if self.__canApplyingGlowEquipment(item):
                self._showEquipmentGlow(idx)
            elif item.becomeReady and not isWtEventItem(item):
                self._showEquipmentGlow(idx, glowType)
            elif idx in self.getEquipmentsGlowCallbacks():
                self.clearEquipmentGlow(idx)

    def __canApplyingGlowEquipment(self, equipment):
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

    def _makeShellTooltip(self, descriptor, piercingPower, shotSpeed):
        kind = descriptor.kind
        projSpeedFactor = vehicles.g_cache.commonConfig['miscParams']['projectileSpeedFactor']
        header = backport.text(R.strings.ingame_gui.shells_kinds.dyn(kind)(), caliber=backport.getNiceNumberFormat(descriptor.caliber), userString='&#171;' + descriptor.userString + '&#187;')
        if GUI_SETTINGS.technicalInfo:
            params = [backport.text(R.strings.ingame_gui.shells_kinds.params.damage(), value=backport.getNiceNumberFormat(descriptor.damage[0]))]
            if piercingPower != 0:
                params.append(backport.text(R.strings.ingame_gui.shells_kinds.params.piercingPower(), value=backport.getNiceNumberFormat(piercingPower)))
            params.append(backport.text(R.strings.ingame_gui.shells_kinds.params.shotSpeed(), value=backport.getIntegralFormat(int(round(shotSpeed / projSpeedFactor)))))
            if kind == SHELL_TYPES.HIGH_EXPLOSIVE and descriptor.type.explosionRadius > 0.0:
                params.append(backport.text(R.strings.ingame_gui.shells_kinds.params.explosionRadius(), value=backport.getNiceNumberFormat(descriptor.type.explosionRadius)))
            if descriptor.hasStun and self.lobbyContext.getServerSettings().spgRedesignFeatures.isStunEnabled():
                stun = descriptor.stun
                params.append(backport.text(R.strings.ingame_gui.shells_kinds.params.stunDuration(), maxValue=backport.getNiceNumberFormat(stun.stunDuration)))
            if descriptor.shortDescriptionSpecial is not None:
                params.append('\n' + text_styles.middleTitle(descriptor.shortDescriptionSpecial))
            if descriptor.longDescriptionSpecial is not None:
                params.append(descriptor.longDescriptionSpecial)
            body = text_styles.concatStylesToMultiLine(*params)
            fmt = TOOLTIP_FORMAT
        else:
            body = ''
            fmt = TOOLTIP_NO_BODY_FORMAT
        return fmt.format(header, body)
