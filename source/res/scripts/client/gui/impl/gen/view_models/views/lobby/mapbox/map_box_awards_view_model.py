# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mapbox/map_box_awards_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel

class MapBoxAwardsViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(MapBoxAwardsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def rewards(self):
        return self._getViewModel(0)

    @staticmethod
    def getRewardsType():
        return IconBonusModel

    def getBattlesNumber(self):
        return self._getNumber(1)

    def setBattlesNumber(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(MapBoxAwardsViewModel, self)._initialize()
        self._addViewModelProperty('rewards', UserListModel())
        self._addNumberProperty('battlesNumber', 0)
