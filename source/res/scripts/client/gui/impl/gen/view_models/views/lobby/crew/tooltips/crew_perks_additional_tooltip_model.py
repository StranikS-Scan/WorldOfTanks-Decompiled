# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/tooltips/crew_perks_additional_tooltip_model.py
from frameworks.wulf import ViewModel

class CrewPerksAdditionalTooltipModel(ViewModel):
    __slots__ = ('onError',)

    def __init__(self, properties=6, commands=1):
        super(CrewPerksAdditionalTooltipModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getString(0)

    def setTitle(self, value):
        self._setString(0, value)

    def getIcon(self):
        return self._getString(1)

    def setIcon(self, value):
        self._setString(1, value)

    def getSkillType(self):
        return self._getString(2)

    def setSkillType(self, value):
        self._setString(2, value)

    def getDescription(self):
        return self._getString(3)

    def setDescription(self, value):
        self._setString(3, value)

    def getInfo(self):
        return self._getString(4)

    def setInfo(self, value):
        self._setString(4, value)

    def getAnimationName(self):
        return self._getString(5)

    def setAnimationName(self, value):
        self._setString(5, value)

    def _initialize(self):
        super(CrewPerksAdditionalTooltipModel, self)._initialize()
        self._addStringProperty('title', '')
        self._addStringProperty('icon', '')
        self._addStringProperty('skillType', '')
        self._addStringProperty('description', '')
        self._addStringProperty('info', '')
        self._addStringProperty('animationName', '')
        self.onError = self._addCommand('onError')
