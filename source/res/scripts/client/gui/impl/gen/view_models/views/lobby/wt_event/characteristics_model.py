# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/characteristics_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.wt_event.characteristics_advantage_model import CharacteristicsAdvantageModel
from gui.impl.gen.view_models.views.lobby.wt_event.characteristics_features_model import CharacteristicsFeaturesModel
from gui.impl.gen.view_models.views.lobby.wt_event.characteristics_skill_model import CharacteristicsSkillModel

class CharacteristicsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(CharacteristicsModel, self).__init__(properties=properties, commands=commands)

    @property
    def pros(self):
        return self._getViewModel(0)

    @property
    def cons(self):
        return self._getViewModel(1)

    @property
    def features(self):
        return self._getViewModel(2)

    @property
    def skills(self):
        return self._getViewModel(3)

    def _initialize(self):
        super(CharacteristicsModel, self)._initialize()
        self._addViewModelProperty('pros', UserListModel())
        self._addViewModelProperty('cons', UserListModel())
        self._addViewModelProperty('features', UserListModel())
        self._addViewModelProperty('skills', UserListModel())
