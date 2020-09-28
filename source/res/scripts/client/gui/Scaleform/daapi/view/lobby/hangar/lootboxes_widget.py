# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/lootboxes_widget.py
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.lobby.loot_box.loot_box_entry_point import LootboxesEntrancePointWidget

class LootBoxWidget(InjectComponentAdaptor):

    def _makeInjectView(self):
        return LootboxesEntrancePointWidget()
