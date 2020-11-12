# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/china_loot_boxes_widget.py
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.lobby.cn_loot_boxes.china_loot_boxes_entry_point import ChinaLootBoxesEntryPointWidget

class ChinaLootBoxesWidget(InjectComponentAdaptor):

    def _makeInjectView(self):
        return ChinaLootBoxesEntryPointWidget()
