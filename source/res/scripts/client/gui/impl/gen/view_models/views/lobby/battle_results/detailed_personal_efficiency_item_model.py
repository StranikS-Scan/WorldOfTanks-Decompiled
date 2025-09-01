# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/detailed_personal_efficiency_item_model.py
from frameworks.wulf import ViewModel

class DetailedPersonalEfficiencyItemModel(ViewModel):
    __slots__ = ()
    KILLED = 'targetKills'
    SPOTTED = 'spotted'
    DAMAGE_DEALT = 'damageDealt'
    PIERCINGS = 'piercings'
    STUN = 'damageAssistedStun'
    STUN_COUNT = 'stunCount'
    DAMAGE_ASSISTED = 'damageAssisted'
    CRITICAL_DAMAGE = 'criticalDamage'
    DAMAGE_BLOCKED_BY_ARMOR = 'damageBlockedByArmor'
    RICKOCHETS_RECEIVED = 'rickochetsReceived'
    NO_DAMAGE_DIRECT_HITS_RECIEVEVD = 'noDamageDirectHitsReceived'

    def __init__(self, properties=2, commands=0):
        super(DetailedPersonalEfficiencyItemModel, self).__init__(properties=properties, commands=commands)

    def getParamType(self):
        return self._getString(0)

    def setParamType(self, value):
        self._setString(0, value)

    def getValue(self):
        return self._getNumber(1)

    def setValue(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(DetailedPersonalEfficiencyItemModel, self)._initialize()
        self._addStringProperty('paramType', '')
        self._addNumberProperty('value', 0)
