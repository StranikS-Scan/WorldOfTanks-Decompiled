# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/bob/bob_widget_view_model.py
from frameworks.wulf import ViewModel

class BobWidgetViewModel(ViewModel):
    __slots__ = ('onWidgetClick', 'onSkillClick', 'onSkillActivated')

    def __init__(self, properties=8, commands=3):
        super(BobWidgetViewModel, self).__init__(properties=properties, commands=commands)

    def getBloggerId(self):
        return self._getNumber(0)

    def setBloggerId(self, value):
        self._setNumber(0, value)

    def getBloggerPlace(self):
        return self._getNumber(1)

    def setBloggerPlace(self, value):
        self._setNumber(1, value)

    def getBloggerPoints(self):
        return self._getNumber(2)

    def setBloggerPoints(self, value):
        self._setNumber(2, value)

    def getUsePoints(self):
        return self._getBool(3)

    def setUsePoints(self, value):
        self._setBool(3, value)

    def getActiveSkillName(self):
        return self._getString(4)

    def setActiveSkillName(self, value):
        self._setString(4, value)

    def getHasSkill(self):
        return self._getBool(5)

    def setHasSkill(self, value):
        self._setBool(5, value)

    def getJustActivated(self):
        return self._getBool(6)

    def setJustActivated(self, value):
        self._setBool(6, value)

    def getSkillRemainingTime(self):
        return self._getString(7)

    def setSkillRemainingTime(self, value):
        self._setString(7, value)

    def _initialize(self):
        super(BobWidgetViewModel, self)._initialize()
        self._addNumberProperty('bloggerId', 0)
        self._addNumberProperty('bloggerPlace', 0)
        self._addNumberProperty('bloggerPoints', 0)
        self._addBoolProperty('usePoints', False)
        self._addStringProperty('activeSkillName', '')
        self._addBoolProperty('hasSkill', False)
        self._addBoolProperty('justActivated', False)
        self._addStringProperty('skillRemainingTime', '')
        self.onWidgetClick = self._addCommand('onWidgetClick')
        self.onSkillClick = self._addCommand('onSkillClick')
        self.onSkillActivated = self._addCommand('onSkillActivated')
