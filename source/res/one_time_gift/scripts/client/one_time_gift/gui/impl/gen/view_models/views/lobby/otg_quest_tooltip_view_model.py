# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/gui/impl/gen/view_models/views/lobby/otg_quest_tooltip_view_model.py
from frameworks.wulf import ViewModel

class OtgQuestTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(OtgQuestTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getExpireTime(self):
        return self._getNumber(0)

    def setExpireTime(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(OtgQuestTooltipViewModel, self)._initialize()
        self._addNumberProperty('expireTime', 0)
