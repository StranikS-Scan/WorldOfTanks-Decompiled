# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/common/skill/skill_extended_model.py
from gui.impl.gen.view_models.views.lobby.crew.common.skill.skill_model import SkillModel

class SkillExtendedModel(SkillModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(SkillExtendedModel, self).__init__(properties=properties, commands=commands)

    def getUserName(self):
        return self._getString(6)

    def setUserName(self, value):
        self._setString(6, value)

    def getDescription(self):
        return self._getString(7)

    def setDescription(self, value):
        self._setString(7, value)

    def _initialize(self):
        super(SkillExtendedModel, self)._initialize()
        self._addStringProperty('userName', '')
        self._addStringProperty('description', '')
