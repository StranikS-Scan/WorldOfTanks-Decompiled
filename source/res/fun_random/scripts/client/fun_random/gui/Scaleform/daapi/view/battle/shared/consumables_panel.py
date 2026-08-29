# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/Scaleform/daapi/view/battle/shared/consumables_panel.py
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel
from gui.impl import backport
from gui.impl.gen import R
from items.artefacts import SharedCooldownConsumableConfigReader
from fun_random.gui.fun_gui_constants import MEDKIT_DURATION
TOOLTIP_FORMAT = '{{HEADER}}{0:>s}{{/HEADER}}\n/{{BODY}}{1:>s}{{/BODY}}'
ABILITY_EQUIPMENT_TAGS = ['visualScriptAbilityEquipment', 'abilityEquipment']

class FunRandomConsumablePanel(ConsumablesPanel):

    @staticmethod
    def __isAbilityEquipment(item):
        return any((tag in ABILITY_EQUIPMENT_TAGS for tag in item.getTags()))

    def _buildEquipmentSlotTooltipText(self, item):
        descriptor = item.getDescriptor()
        if self.__isAbilityEquipment(item):
            return self.__buildAbilityEquipmentTooltip(descriptor)
        else:
            reloadingTime = item.getTotalTime()
            isSharedCooldownConfig = isinstance(descriptor, SharedCooldownConsumableConfigReader)
            body = descriptor.description
            consumeAmmo = descriptor.consumeAmmo if isSharedCooldownConfig else False
            if not consumeAmmo and reloadingTime > 0:
                body = '\n'.join((body, ''))
                duration = MEDKIT_DURATION.get(descriptor.name, None)
                if duration is not None:
                    body = backport.text(R.strings.fun_random.consumables.dyn(descriptor.name)(), healDuration=duration).join((body, ''))
                body = '\n'.join((body, ''))
                if descriptor.isActivatable():
                    activeSecondsTooltipStr = R.strings.ingame_gui.consumables_panel.equipment.activeSeconds()
                    activeSec = descriptor.activeSeconds
                    activeSecondsParamsString = backport.text(activeSecondsTooltipStr, activeSeconds=str(int(activeSec)))
                    body = '\n'.join((body, activeSecondsParamsString))
                if isSharedCooldownConfig:
                    cdSecVal = descriptor.cooldownTime
                elif descriptor.isActivatable():
                    cdSecVal = item.getTotalCooldownTime()
                else:
                    cdSecVal = item.getTotalTime()
                cooldownSecondsTooltipStr = R.strings.ingame_gui.consumables_panel.equipment.cooldownSeconds()
                cooldownSecondsParamsString = backport.text(cooldownSecondsTooltipStr, cooldownSeconds=str(int(cdSecVal)))
                body = '\n'.join((body, cooldownSecondsParamsString))
            toolTip = TOOLTIP_FORMAT.format(descriptor.userString, body)
            return toolTip
