# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/page/footer/platoon_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.page.footer.platoon_member_model import PlatoonMemberModel

class PlatoonModel(ViewModel):
    __slots__ = ('onInPlatoonAction',)
    SEARCHING = 'SEARCHING'
    IN_PLATOON = 'IN_PLATOON'
    CREATE = 'CREATE'
    DISABLED = 'DISABLED'

    def __init__(self, properties=8, commands=1):
        super(PlatoonModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return self._getString(0)

    def setState(self, value):
        self._setString(0, value)

    def getUseWelcomeLayout(self):
        return self._getBool(1)

    def setUseWelcomeLayout(self, value):
        self._setBool(1, value)

    def getTooltipHeader(self):
        return self._getResource(2)

    def setTooltipHeader(self, value):
        self._setResource(2, value)

    def getTooltipBody(self):
        return self._getResource(3)

    def setTooltipBody(self, value):
        self._setResource(3, value)

    def getTooltipParams(self):
        return self._getString(4)

    def setTooltipParams(self, value):
        self._setString(4, value)

    def getCommanderIndex(self):
        return self._getNumber(5)

    def setCommanderIndex(self, value):
        self._setNumber(5, value)

    def getPlayerIndex(self):
        return self._getNumber(6)

    def setPlayerIndex(self, value):
        self._setNumber(6, value)

    def getMembers(self):
        return self._getArray(7)

    def setMembers(self, value):
        self._setArray(7, value)

    @staticmethod
    def getMembersType():
        return PlatoonMemberModel

    def _initialize(self):
        super(PlatoonModel, self)._initialize()
        self._addStringProperty('state', '')
        self._addBoolProperty('useWelcomeLayout', False)
        self._addResourceProperty('tooltipHeader', R.invalid())
        self._addResourceProperty('tooltipBody', R.invalid())
        self._addStringProperty('tooltipParams', '')
        self._addNumberProperty('commanderIndex', 0)
        self._addNumberProperty('playerIndex', 0)
        self._addArrayProperty('members', Array())
        self.onInPlatoonAction = self._addCommand('onInPlatoonAction')
