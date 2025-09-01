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

    def __init__(self, properties=7, commands=1):
        super(PlatoonModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return self._getString(0)

    def setState(self, value):
        self._setString(0, value)

    def getTooltipHeader(self):
        return self._getResource(1)

    def setTooltipHeader(self, value):
        self._setResource(1, value)

    def getTooltipBody(self):
        return self._getResource(2)

    def setTooltipBody(self, value):
        self._setResource(2, value)

    def getTooltipParams(self):
        return self._getString(3)

    def setTooltipParams(self, value):
        self._setString(3, value)

    def getCommanderIndex(self):
        return self._getNumber(4)

    def setCommanderIndex(self, value):
        self._setNumber(4, value)

    def getPlayerIndex(self):
        return self._getNumber(5)

    def setPlayerIndex(self, value):
        self._setNumber(5, value)

    def getMembers(self):
        return self._getArray(6)

    def setMembers(self, value):
        self._setArray(6, value)

    @staticmethod
    def getMembersType():
        return PlatoonMemberModel

    def _initialize(self):
        super(PlatoonModel, self)._initialize()
        self._addStringProperty('state', '')
        self._addResourceProperty('tooltipHeader', R.invalid())
        self._addResourceProperty('tooltipBody', R.invalid())
        self._addStringProperty('tooltipParams', '')
        self._addNumberProperty('commanderIndex', 0)
        self._addNumberProperty('playerIndex', 0)
        self._addArrayProperty('members', Array())
        self.onInPlatoonAction = self._addCommand('onInPlatoonAction')
