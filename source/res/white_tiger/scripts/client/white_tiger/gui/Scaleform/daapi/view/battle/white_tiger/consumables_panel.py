# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/white_tiger/consumables_panel.py
import BigWorld
from math import ceil
from items import vehicles
from gui import GUI_SETTINGS
from constants import EQUIPMENT_STAGES, SHELL_TYPES
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.gui_items import getKpiValueString
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import TOOLTIP_FORMAT, TOOLTIP_NO_BODY_FORMAT
from helpers import dependency
from cgf_components import wt_helpers
from skeletons.gui.battle_session import IBattleSessionProvider
from white_tiger.gui.Scaleform.daapi.view.meta.WTConsumablesPanelMeta import WTConsumablesPanelMeta
from white_tiger.gui.battle_control.controllers.consumables.equipment_sound import WtEquipmentSound, playAbilityVoiceOver

class WhiteTigerConsumablesPanel(WTConsumablesPanelMeta):
    _AMMO_START_IDX = 11
    _AMMO_END_IDX = 11
    _EQUIPMENT_START_IDX = 0
    _EQUIPMENT_END_IDX = 5
    _ORDERS_START_IDX = 8
    _ORDERS_END_IDX = 8
    _MAX_CHARGE_PROGRESS = 100
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(WhiteTigerConsumablesPanel, self).__init__()
        self._currentStage = EQUIPMENT_STAGES.UNAVAILABLE
        self.__abilitiesManager = None
        return

    def _addEquipmentSlot(self, idx, intCD, item):
        if hasattr(item.getDescriptor(), 'subType') and item.getDescriptor().subType == 'passive':
            self._cds[idx] = intCD
            item.init(self, idx)
            descriptor = item.getDescriptor()
            toolTip = self._buildEquipmentSlotTooltipText(item)
            self.as_wtAddPassiveAbilitySlotS(idx=idx, iconPath=self._getEquipmentIcon(idx, item, descriptor.icon[0]), tooltipText=toolTip)
        else:
            super(WhiteTigerConsumablesPanel, self)._addEquipmentSlot(idx, intCD, item)

    def _buildEquipmentSlotTooltipText(self, item):
        descriptor = item.getDescriptor()
        reloadingTime = descriptor.cooldownSeconds
        if not {'repairkit', 'medkit'} & descriptor.tags:
            body = self.__getAdditionalTooltipBodyString(item)
        else:
            body = descriptor.description
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
        if 'wt_union_strength' in item.getDescriptor().name:
            effectDuration = item.getDescriptor().effectDuration
            receiveDamageFactor = item.getDescriptor().receiveDamageFactor
            return backport.text(getattr(attribs, 'always')(), damageIncrease=int(receiveDamageFactor * 100), percent=backport.text(R.strings.common.common.percent()), time=int(effectDuration))
        attributes = ('onUse', 'always', 'restriction')
        for atr in attributes:
            if item.getDescriptor().name in ('wt_stun_area', 'wt_stun_area_mod_a') and atr == 'onUse':
                effectDuration = item.getDescriptor().debuffDuration
                effectRadius = item.getDescriptor().damageRadius
                strText = backport.text(getattr(attribs, atr)(), time=int(effectDuration), radius=int(effectRadius))
            else:
                strText = backport.text(getattr(attribs, atr)(), **kpiArgs)
            if strText and strText != emptyStr:
                if atr == 'restriction':
                    eq = R.strings.tooltips.equipment
                    description = text_styles.middleTitle(backport.text(getattr(eq, atr)()))
                    block = '\n'.join((description, strText))
                    resultStr = '\n\n'.join((resultStr, block))
                else:
                    resultStr = ''.join((resultStr, strText))

        return resultStr

    def _populate(self):
        super(WhiteTigerConsumablesPanel, self)._populate()
        equipmentCtrl = self.sessionProvider.shared.equipments
        if equipmentCtrl is not None:
            equipmentCtrl.onDebuffEquipmentChanged += self.__onDebuffEquipmentChanged
        vehicle = BigWorld.entities.get(BigWorld.player().playerVehicleID)
        self.__abilitiesManager = self.__getAbilitiesManager(vehicle)
        self.__subscribeAbilitiesManager()
        return

    def _dispose(self):
        super(WhiteTigerConsumablesPanel, self)._dispose()
        equipmentCtrl = self.sessionProvider.shared.equipments
        if equipmentCtrl is not None:
            equipmentCtrl.onDebuffEquipmentChanged -= self.__onDebuffEquipmentChanged
        self.__unsubscribeAbilitiesManager()
        self.__abilitiesManager = None
        return

    def __onEquipmentCharged(self, equipmentsData):
        for eqIntCD, value in equipmentsData:
            if eqIntCD not in self._cds:
                continue
            idx = self._cds.index(eqIntCD)
            if 0 < value < self._MAX_CHARGE_PROGRESS:
                self.as_wtSetChargeProgressS(idx, value)

    def __onEquipmentLocked(self, isLocked, lockedIntCDs):
        equipmentCtrl = self.sessionProvider.shared.equipments
        if equipmentCtrl is None:
            return
        else:
            for eqIntCD in lockedIntCDs:
                idx = self._cds.index(eqIntCD)
                item = equipmentCtrl.getEquipment(eqIntCD)
                item.setLocked(isLocked)
                self.as_wtSetLockedS(idx, isLocked)

            return

    def _updateEquipmentSlot(self, idx, item):
        currentStage = item.getStage()
        if currentStage == EQUIPMENT_STAGES.EXHAUSTED:
            self.as_wtSetDisabledS(idx, False)
        elif currentStage == EQUIPMENT_STAGES.READY:
            self.as_wtShowReadyS(idx)
        elif currentStage == EQUIPMENT_STAGES.COOLDOWN:
            self.as_wtShowCooldownS(idx, int(ceil(item.getTimeRemaining())))
        elif currentStage == EQUIPMENT_STAGES.DEPLOYING:
            self.as_wtShowDeployingS(idx)
        elif currentStage == EQUIPMENT_STAGES.PREPARING:
            if item.getDescriptor().subType == 'cancelable':
                self.as_wtShowActiveS(idx, 0)
            else:
                self.as_wtShowPreparingS(idx)
        elif currentStage == EQUIPMENT_STAGES.ACTIVE:
            self.as_wtShowActiveS(idx, int(ceil(item.getTimeRemaining())))
        elif currentStage == EQUIPMENT_STAGES.NOT_RUNNING and item.getDescriptor().subType == 'passive':
            self.as_wtSetDisabledS(idx, False)
        else:
            super(WhiteTigerConsumablesPanel, self)._updateEquipmentSlot(idx, item)
        if item.getPrevStage() != item.getStage():
            playAbilityVoiceOver(item)

    def __onDebuffEquipmentChanged(self, intCD, isDebuffView):
        if intCD not in self._cds:
            return
        idx = self._cds.index(intCD)
        self.as_wtSetDisabledS(idx, isDebuffView)

    def _makeShellTooltip(self, descriptor, gunSettings, intCD, *_, **__):
        kind = descriptor.kind
        projSpeedFactor = vehicles.g_cache.commonConfig['miscParams']['projectileSpeedFactor']
        header = backport.text(R.strings.ingame_gui.shells_kinds.dyn(kind)(), caliber=backport.getNiceNumberFormat(descriptor.caliber), userString='&#171;' + descriptor.userString + '&#187;')
        if GUI_SETTINGS.technicalInfo:
            params = [backport.text(R.strings.ingame_gui.shells_kinds.params.damage(), value=backport.getNiceNumberFormat(descriptor.damage[0]))]
            piercingPower = gunSettings.getPiercingPower(intCD)
            if piercingPower[0] != 0 and piercingPower[1] != 0:
                params.append(backport.text(R.strings.ingame_gui.shells_kinds.params.piercingPower(), value=backport.getNiceNumberFormat(piercingPower[0])))
            shotSpeed = gunSettings.getShotSpeed(intCD)
            params.append(backport.text(R.strings.ingame_gui.shells_kinds.params.shotSpeed(), value=backport.getIntegralFormat(int(round(shotSpeed / projSpeedFactor)))))
            if kind == SHELL_TYPES.HIGH_EXPLOSIVE and descriptor.type.explosionRadius > 0.0:
                params.append(backport.text(R.strings.ingame_gui.shells_kinds.params.explosionRadius(), value=backport.getNiceNumberFormat(descriptor.type.explosionRadius)))
            if descriptor.hasStun and self.lobbyContext.getServerSettings().spgRedesignFeatures.isStunEnabled():
                stun = descriptor.stun
                params.append(backport.text(R.strings.ingame_gui.shells_kinds.params.stunDuration(), maxValue=backport.getNiceNumberFormat(stun.stunDuration)))
            if not wt_helpers.isBoss():
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

    def __getAbilitiesManager(self, vehicle):
        return vehicle.dynamicComponents.get('wtAbilitiesManager')

    def __subscribeAbilitiesManager(self):
        self.__abilitiesManager.onEquipmentCharged += self.__onEquipmentCharged
        self.__abilitiesManager.onEquipmentLocked += self.__onEquipmentLocked

    def __unsubscribeAbilitiesManager(self):
        self.__abilitiesManager.onEquipmentCharged -= self.__onEquipmentCharged
        self.__abilitiesManager.onEquipmentLocked -= self.__onEquipmentLocked
