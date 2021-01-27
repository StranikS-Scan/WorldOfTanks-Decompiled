# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/bob/bob_widget_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.bob.bob_widget_skills_model import BobWidgetSkillsModel

class BobWidgetViewModel(ViewModel):
    __slots__ = ('onProgressionClick', 'onSkillsClick')
    PROGRESSIVE_TOOLTIP = 'progressiveTooltip'
    SKILL_TOOLTIP = 'skillTooltip'
    STATE_NORMAL = ''
    STATE_HIDDEN = 'hidden'
    STATE_BROKEN = 'broken'

    def __init__(self, properties=4, commands=2):
        super(BobWidgetViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def skill(self):
        return self._getViewModel(0)

    def getTeamID(self):
        return self._getNumber(1)

    def setTeamID(self, value):
        self._setNumber(1, value)

    def getRank(self):
        return self._getNumber(2)

    def setRank(self, value):
        self._setNumber(2, value)

    def getRankState(self):
        return self._getString(3)

    def setRankState(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(BobWidgetViewModel, self)._initialize()
        self._addViewModelProperty('skill', BobWidgetSkillsModel())
        self._addNumberProperty('teamID', 0)
        self._addNumberProperty('rank', 0)
        self._addStringProperty('rankState', '')
        self.onProgressionClick = self._addCommand('onProgressionClick')
        self.onSkillsClick = self._addCommand('onSkillsClick')
