# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/skill_stats_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.comp7.dynamic_param_model import DynamicParamModel
from gui.impl.gen.view_models.views.lobby.comp7.static_param_model import StaticParamModel

class SkillStatsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(SkillStatsModel, self).__init__(properties=properties, commands=commands)

    @property
    def staticParams(self):
        return self._getViewModel(0)

    @staticmethod
    def getStaticParamsType():
        return StaticParamModel

    @property
    def dynamicParams(self):
        return self._getViewModel(1)

    @staticmethod
    def getDynamicParamsType():
        return DynamicParamModel

    def getName(self):
        return self._getString(2)

    def setName(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(SkillStatsModel, self)._initialize()
        self._addViewModelProperty('staticParams', UserListModel())
        self._addViewModelProperty('dynamicParams', UserListModel())
        self._addStringProperty('name', '')
