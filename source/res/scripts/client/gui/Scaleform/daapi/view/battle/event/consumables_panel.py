# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/consumables_panel.py
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel, TOOLTIP_FORMAT
from gui.Scaleform.genConsts.BATTLE_CONSUMABLES_PANEL_TAGS import BATTLE_CONSUMABLES_PANEL_TAGS
from gui.Scaleform.genConsts.CONSUMABLES_PANEL_SETTINGS import CONSUMABLES_PANEL_SETTINGS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.impl import backport
from gui.impl.gen.resources import R
from gui.shared.formatters import icons
from gui.wt_event.wt_event_helpers import isPlayerBoss
from helpers import i18n
from items.artefacts import SharedCooldownConsumableConfigReader

class EventConsumablesPanel(ConsumablesPanel):
    __slots__ = ('_isBossVehicle',)

    def _populate(self):
        self._isBossVehicle = isPlayerBoss()
        self._AMMO_END_IDX = 0
        self._ConsumablesPanel__ammoRange = xrange(self._AMMO_START_IDX, self._AMMO_END_IDX + 1)
        self._ConsumablesPanel__ammoFullMask = 1
        self._EQUIPMENT_START_IDX, self._EQUIPMENT_END_IDX = (1, 2) if self._isBossVehicle else (2, 5)
        self._ConsumablesPanel__equipmentRange = xrange(self._EQUIPMENT_START_IDX, self._EQUIPMENT_END_IDX + 1)
        self._ConsumablesPanel__equipmentFullMask = 6 if self._isBossVehicle else 60
        super(EventConsumablesPanel, self)._populate()

    def _getPanelSettings(self):
        return CONSUMABLES_PANEL_SETTINGS.WT_EVENT_BOSS if self._isBossVehicle else CONSUMABLES_PANEL_SETTINGS.WT_EVENT_HUNTER

    def _makeEquipmentItemTooltip(self, item):
        descriptor = item.getDescriptor()
        body = descriptor.description
        tags = item.getTags()
        if BATTLE_CONSUMABLES_PANEL_TAGS.EVENT_ALT_ITEM in tags:
            body = '{}\n{}'.format(body, icons.makeImageTag(source=backport.image(R.images.gui.maps.icons.wtevent.tooltips.consumable_alt_click()), width=64, height=31, vSpace=4))
        if item.getTotalTime() > 0:
            tooltipStr = INGAME_GUI.CONSUMABLES_PANEL_EQUIPMENT_COOLDOWNSECONDS
            if isinstance(descriptor, SharedCooldownConsumableConfigReader):
                cdSecVal = descriptor.cooldownTime
            else:
                cdSecVal = descriptor.cooldownSeconds
            cooldownSeconds = str(int(cdSecVal))
            paramsString = i18n.makeString(tooltipStr, cooldownSeconds=cooldownSeconds)
            body = body + '\n\n' + paramsString
        return TOOLTIP_FORMAT.format(descriptor.userString, body)

    def _makeShellTooltip(self, descriptor, piercingPower, shotSpeed):
        return TOOLTIPS_CONSTANTS.WT_EVENT_SHELL_BATTLE
