# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/mentor_assigment_view_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.crew.common.base_crew_view_model import BaseCrewViewModel
from gui.impl.gen.view_models.views.lobby.crew.common.info_tip_model import InfoTipModel
from gui.impl.gen.view_models.views.lobby.crew.mentor_assigment_tankman_model import MentorAssigmentTankmanModel

class MentorAssigmentViewModel(BaseCrewViewModel):
    __slots__ = ('onResetFilters', 'onLoadCards', 'onTankmanSelected', 'onCardMouseEnter', 'onCardMouseLeave', 'onTipClose', 'onTipsReadyToShow')

    def __init__(self, properties=10, commands=11):
        super(MentorAssigmentViewModel, self).__init__(properties=properties, commands=commands)

    def getSelectedTankmanID(self):
        return self._getNumber(2)

    def setSelectedTankmanID(self, value):
        self._setNumber(2, value)

    def getLicensesAmount(self):
        return self._getNumber(3)

    def setLicensesAmount(self, value):
        self._setNumber(3, value)

    def getNation(self):
        return self._getString(4)

    def setNation(self, value):
        self._setString(4, value)

    def getHasFilters(self):
        return self._getBool(5)

    def setHasFilters(self, value):
        self._setBool(5, value)

    def getItemsAmount(self):
        return self._getNumber(6)

    def setItemsAmount(self, value):
        self._setNumber(6, value)

    def getItemsOffset(self):
        return self._getNumber(7)

    def setItemsOffset(self, value):
        self._setNumber(7, value)

    def getTankmanList(self):
        return self._getArray(8)

    def setTankmanList(self, value):
        self._setArray(8, value)

    @staticmethod
    def getTankmanListType():
        return MentorAssigmentTankmanModel

    def getTips(self):
        return self._getArray(9)

    def setTips(self, value):
        self._setArray(9, value)

    @staticmethod
    def getTipsType():
        return InfoTipModel

    def _initialize(self):
        super(MentorAssigmentViewModel, self)._initialize()
        self._addNumberProperty('selectedTankmanID', 0)
        self._addNumberProperty('licensesAmount', 0)
        self._addStringProperty('nation', '')
        self._addBoolProperty('hasFilters', False)
        self._addNumberProperty('itemsAmount', 0)
        self._addNumberProperty('itemsOffset', 0)
        self._addArrayProperty('tankmanList', Array())
        self._addArrayProperty('tips', Array())
        self.onResetFilters = self._addCommand('onResetFilters')
        self.onLoadCards = self._addCommand('onLoadCards')
        self.onTankmanSelected = self._addCommand('onTankmanSelected')
        self.onCardMouseEnter = self._addCommand('onCardMouseEnter')
        self.onCardMouseLeave = self._addCommand('onCardMouseLeave')
        self.onTipClose = self._addCommand('onTipClose')
        self.onTipsReadyToShow = self._addCommand('onTipsReadyToShow')
