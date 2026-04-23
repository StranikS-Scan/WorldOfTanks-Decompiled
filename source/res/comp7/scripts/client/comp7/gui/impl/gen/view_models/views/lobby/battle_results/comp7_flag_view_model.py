# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/battle_results/comp7_flag_view_model.py
from gui.impl.gen.view_models.views.lobby.battle_results.flag.flag_view_model import FlagViewModel

class Comp7FlagViewModel(FlagViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(Comp7FlagViewModel, self).__init__(properties=properties, commands=commands)

    def getIsLeave(self):
        return self._getBool(3)

    def setIsLeave(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(Comp7FlagViewModel, self)._initialize()
        self._addBoolProperty('isLeave', False)
