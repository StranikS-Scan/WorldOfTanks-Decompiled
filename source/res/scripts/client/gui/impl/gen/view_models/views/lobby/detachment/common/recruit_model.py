# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/recruit_model.py
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.detachment.common.recruit_base_model import RecruitBaseModel
from gui.impl.gen.view_models.views.lobby.detachment.common.skill_model import SkillModel

class RecruitModel(RecruitBaseModel):
    __slots__ = ()

    def __init__(self, properties=13, commands=0):
        super(RecruitModel, self).__init__(properties=properties, commands=commands)

    @property
    def skills(self):
        return self._getViewModel(8)

    def getStatus(self):
        return self._getString(9)

    def setStatus(self, value):
        self._setString(9, value)

    def getState(self):
        return self._getString(10)

    def setState(self, value):
        self._setString(10, value)

    def getType(self):
        return self._getString(11)

    def setType(self, value):
        self._setString(11, value)

    def getIsLocked(self):
        return self._getBool(12)

    def setIsLocked(self, value):
        self._setBool(12, value)

    def _initialize(self):
        super(RecruitModel, self)._initialize()
        self._addViewModelProperty('skills', UserListModel())
        self._addStringProperty('status', '')
        self._addStringProperty('state', '')
        self._addStringProperty('type', '')
        self._addBoolProperty('isLocked', False)
