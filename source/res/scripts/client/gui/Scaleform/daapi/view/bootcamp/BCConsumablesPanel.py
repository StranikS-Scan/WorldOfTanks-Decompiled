# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCConsumablesPanel.py
from gui.Scaleform.daapi.view.meta.BCConsumablesPanelMeta import BCConsumablesPanelMeta
from bootcamp.Bootcamp import g_bootcamp
EQUIPMENT_ICON_PATH_BIG = '../maps/icons/artefact/big/%s.png'
EQUIPMENT_ICON_PATH_DEFAULT = '../maps/icons/artefact/%s.png'

class BCConsumablesPanel(BCConsumablesPanelMeta):

    def __init__(self):
        super(BCConsumablesPanel, self).__init__()
        self.__isBigIcons = False

    def _populate(self):
        isBigIcons = g_bootcamp.checkBigConsumablesIconsLesson()
        if self.__isBigIcons != isBigIcons:
            self.__isBigIcons = isBigIcons
            self.as_setBigSizeS(self.__isBigIcons)
        super(BCConsumablesPanel, self)._populate()

    def _dispose(self):
        super(BCConsumablesPanel, self)._dispose()

    def _getEquipmentIconPath(self):
        return EQUIPMENT_ICON_PATH_BIG if self.__isBigIcons else EQUIPMENT_ICON_PATH_DEFAULT

    def _addShellSlot(self, idx, keyCode, sfKeyCode, quantity, clipCapacity, shellIconPath, noShellIconPath, tooltipText):
        pass

    def _showEquipmentGlow(self, equipmentIndex):
        if self.__isBigIcons:
            return
        super(BCConsumablesPanel, self)._showEquipmentGlow(equipmentIndex)
