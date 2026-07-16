# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/gen/view_models/views/lobby/battle_results/comp7_light_flag_view_model.py
from gui.impl.gen.view_models.views.lobby.battle_results.flag.flag_view_model import FlagViewModel

class Comp7LightFlagViewModel(FlagViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(Comp7LightFlagViewModel, self).__init__(properties=properties, commands=commands)

    def getIsLeave(self):
        return self._getBool(3)

    def setIsLeave(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(Comp7LightFlagViewModel, self)._initialize()
        self._addBoolProperty('isLeave', False)
