# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/common/crew_skill_model.py
from gui.impl.gen.view_models.views.lobby.crew.common.skill.skill_model import SkillModel

class CrewSkillModel(SkillModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(CrewSkillModel, self).__init__(properties=properties, commands=commands)

    def getCustomName(self):
        return self._getString(6)

    def setCustomName(self, value):
        self._setString(6, value)

    def _initialize(self):
        super(CrewSkillModel, self)._initialize()
        self._addStringProperty('customName', '')
