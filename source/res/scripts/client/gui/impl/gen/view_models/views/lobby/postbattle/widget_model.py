# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/postbattle/widget_model.py
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class WidgetModel(BonusModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(WidgetModel, self).__init__(properties=properties, commands=commands)

    def getIsActionDisabled(self):
        return self._getBool(8)

    def setIsActionDisabled(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(WidgetModel, self)._initialize()
        self._addBoolProperty('isActionDisabled', False)
