# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mode_selector/mode_selector_window_states.py
from frameworks.wulf import ViewModel

class ModeSelectorWindowStates(ViewModel):
    __slots__ = ()
    NORMAL = 0
    BOOTCAMP = 1

    def __init__(self, properties=0, commands=0):
        super(ModeSelectorWindowStates, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(ModeSelectorWindowStates, self)._initialize()
