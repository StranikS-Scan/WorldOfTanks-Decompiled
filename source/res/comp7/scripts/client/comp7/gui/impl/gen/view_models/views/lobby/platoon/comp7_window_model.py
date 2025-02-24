# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/platoon/comp7_window_model.py
from frameworks.wulf import Array
from comp7.gui.impl.gen.view_models.views.lobby.enums import SeasonName
from comp7.gui.impl.gen.view_models.views.lobby.meta_view.progression_item_base_model import ProgressionItemBaseModel
from comp7.gui.impl.gen.view_models.views.lobby.platoon.comp7_header_model import Comp7HeaderModel
from comp7.gui.impl.gen.view_models.views.lobby.platoon.comp7_slot_model import Comp7SlotModel
from gui.impl.gen.view_models.views.lobby.platoon.members_window_model import MembersWindowModel

class Comp7WindowModel(MembersWindowModel):
    __slots__ = ()

    def __init__(self, properties=23, commands=3):
        super(Comp7WindowModel, self).__init__(properties=properties, commands=commands)

    @property
    def header(self):
        return self._getViewModel(17)

    @staticmethod
    def getHeaderType():
        return Comp7HeaderModel

    @property
    def topPlayer(self):
        return self._getViewModel(18)

    @staticmethod
    def getTopPlayerType():
        return ProgressionItemBaseModel

    def getSeasonName(self):
        return SeasonName(self._getString(19))

    def setSeasonName(self, value):
        self._setString(19, value.value)

    def getTopPercentage(self):
        return self._getNumber(20)

    def setTopPercentage(self, value):
        self._setNumber(20, value)

    def getSlots(self):
        return self._getArray(21)

    def setSlots(self, value):
        self._setArray(21, value)

    @staticmethod
    def getSlotsType():
        return Comp7SlotModel

    def getRankLimits(self):
        return self._getArray(22)

    def setRankLimits(self, value):
        self._setArray(22, value)

    @staticmethod
    def getRankLimitsType():
        return ProgressionItemBaseModel

    def _initialize(self):
        super(Comp7WindowModel, self)._initialize()
        self._addViewModelProperty('header', Comp7HeaderModel())
        self._addViewModelProperty('topPlayer', ProgressionItemBaseModel())
        self._addStringProperty('seasonName')
        self._addNumberProperty('topPercentage', 0)
        self._addArrayProperty('slots', Array())
        self._addArrayProperty('rankLimits', Array())
