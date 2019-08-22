# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCConsumablesPanel.py
from bootcamp.Bootcamp import g_bootcamp
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel
from gui.Scaleform.genConsts.CONSUMABLES_PANEL_SETTINGS import CONSUMABLES_PANEL_SETTINGS
EQUIPMENT_ICON_PATH_BIG = '../maps/icons/artefact/big/%s.png'
EQUIPMENT_ICON_PATH_DEFAULT = '../maps/icons/artefact/%s.png'

class BCConsumablesPanel(ConsumablesPanel):

    def __init__(self):
        super(BCConsumablesPanel, self).__init__()
        self.__isBigIcons = False

    def _populate(self):
        isBigIcons = g_bootcamp.checkBigConsumablesIconsLesson()
        if self.__isBigIcons != isBigIcons:
            self.__isBigIcons = isBigIcons
        super(BCConsumablesPanel, self)._populate()

    def _getPanelSettings(self):
        return CONSUMABLES_PANEL_SETTINGS.BIG_SETTINGS_ID if self.__isBigIcons else super(BCConsumablesPanel, self)._getPanelSettings()

    def _getEquipmentIconPath(self):
        return EQUIPMENT_ICON_PATH_BIG if self.__isBigIcons else EQUIPMENT_ICON_PATH_DEFAULT

    def _addShellSlot(self, idx, intCD, descriptor, quantity, gunSettings):
        self._cds[idx] = intCD

    def _showEquipmentGlow(self, equipmentIndex, glowType=CONSUMABLES_PANEL_SETTINGS.GLOW_ID_ORANGE):
        if self.__isBigIcons:
            return
        super(BCConsumablesPanel, self)._showEquipmentGlow(equipmentIndex)
