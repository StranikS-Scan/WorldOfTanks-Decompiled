# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/subscription/wot_plus_intro_view_model.py
from frameworks.wulf import ViewModel

class WotPlusIntroViewModel(ViewModel):
    __slots__ = ('onClose', 'onAffirmative', 'onInfo')

    def __init__(self, properties=5, commands=3):
        super(WotPlusIntroViewModel, self).__init__(properties=properties, commands=commands)

    def getBattleBonusEnabled(self):
        return self._getBool(0)

    def setBattleBonusEnabled(self, value):
        self._setBool(0, value)

    def getBattleBonusEarnings(self):
        return self._getNumber(1)

    def setBattleBonusEarnings(self, value):
        self._setNumber(1, value)

    def getAdditionalWoTPlusEnabled(self):
        return self._getBool(2)

    def setAdditionalWoTPlusEnabled(self, value):
        self._setBool(2, value)

    def getAdditionalWoTPlusMaxApplications(self):
        return self._getNumber(3)

    def setAdditionalWoTPlusMaxApplications(self, value):
        self._setNumber(3, value)

    def getBadgesEnabled(self):
        return self._getBool(4)

    def setBadgesEnabled(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(WotPlusIntroViewModel, self)._initialize()
        self._addBoolProperty('battleBonusEnabled', False)
        self._addNumberProperty('battleBonusEarnings', 0)
        self._addBoolProperty('additionalWoTPlusEnabled', False)
        self._addNumberProperty('additionalWoTPlusMaxApplications', 0)
        self._addBoolProperty('badgesEnabled', False)
        self.onClose = self._addCommand('onClose')
        self.onAffirmative = self._addCommand('onAffirmative')
        self.onInfo = self._addCommand('onInfo')
