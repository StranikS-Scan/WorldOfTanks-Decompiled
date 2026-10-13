# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/award_congrats_view_model.py
from frameworks.wulf import Array, ViewModel
from halloween.gui.impl.gen.view_models.views.common.bonus_item_view_model import BonusItemViewModel

class AwardCongratsViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=3, commands=1):
        super(AwardCongratsViewModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getString(0)

    def setTitle(self, value):
        self._setString(0, value)

    def getIsCommunityVoted(self):
        return self._getBool(1)

    def setIsCommunityVoted(self, value):
        self._setBool(1, value)

    def getBonuses(self):
        return self._getArray(2)

    def setBonuses(self, value):
        self._setArray(2, value)

    @staticmethod
    def getBonusesType():
        return BonusItemViewModel

    def _initialize(self):
        super(AwardCongratsViewModel, self)._initialize()
        self._addStringProperty('title', '')
        self._addBoolProperty('isCommunityVoted', False)
        self._addArrayProperty('bonuses', Array())
        self.onClose = self._addCommand('onClose')
