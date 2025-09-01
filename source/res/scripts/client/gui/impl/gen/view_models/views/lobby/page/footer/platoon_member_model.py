# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/page/footer/platoon_member_model.py
from frameworks.wulf import ViewModel

class PlatoonMemberModel(ViewModel):
    __slots__ = ()
    READY = 'ready'
    NOT_READY = 'notReady'
    IN_BATTLE = 'inBattle'
    SEARCHING = 'searching'
    EMPTY = 'empty'

    def __init__(self, properties=1, commands=0):
        super(PlatoonMemberModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return self._getString(0)

    def setState(self, value):
        self._setString(0, value)

    def _initialize(self):
        super(PlatoonMemberModel, self)._initialize()
        self._addStringProperty('state', '')
