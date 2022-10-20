# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/lobby/hangar/hw_progression_entry_point.py
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from halloween.gui.impl.lobby.witches_view import WitchesView

class HW22ProgressionEntryPoint(InjectComponentAdaptor):

    def _makeInjectView(self):
        self.__view = WitchesView()
        return self.__view
