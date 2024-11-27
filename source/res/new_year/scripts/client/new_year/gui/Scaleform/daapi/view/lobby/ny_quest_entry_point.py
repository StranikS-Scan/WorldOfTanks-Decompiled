# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/Scaleform/daapi/view/lobby/ny_quest_entry_point.py
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from new_year.gui.impl.lobby.new_year.quests.ny_quest_entry_point_view import NYQuestEntryPointView

class NYQuestEntryPoint(InjectComponentAdaptor):

    def _makeInjectView(self):
        return NYQuestEntryPointView()
