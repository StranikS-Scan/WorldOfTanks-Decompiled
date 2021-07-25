# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/maps_training/consumables_panel.py
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel
from gui.Scaleform.genConsts.CONSUMABLES_PANEL_SETTINGS import CONSUMABLES_PANEL_SETTINGS

class MapsTrainingConsumablesPanel(ConsumablesPanel):

    def _getPanelSettings(self):
        return CONSUMABLES_PANEL_SETTINGS.MAPS_TRAINING_SETTINGS_ID
