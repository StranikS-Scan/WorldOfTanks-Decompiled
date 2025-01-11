# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch_progression/scripts/client/grinch_progression/gui/impl/gen/view_models/views/lobby/views/rewards_model.py
from grinch_progression.gui.impl.gen.view_models.views.lobby.views.enums import RewardRarity, RewardState
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel

class RewardsModel(IconBonusModel):
    __slots__ = ()

    def __init__(self, properties=19, commands=0):
        super(RewardsModel, self).__init__(properties=properties, commands=commands)

    def getChapter(self):
        return self._getNumber(9)

    def setChapter(self, value):
        self._setNumber(9, value)

    def getStep(self):
        return self._getNumber(10)

    def setStep(self, value):
        self._setNumber(10, value)

    def getPrice(self):
        return self._getNumber(11)

    def setPrice(self, value):
        self._setNumber(11, value)

    def getAmount(self):
        return self._getNumber(12)

    def setAmount(self, value):
        self._setNumber(12, value)

    def getId(self):
        return self._getString(13)

    def setId(self, value):
        self._setString(13, value)

    def getName(self):
        return self._getString(14)

    def setName(self, value):
        self._setString(14, value)

    def getIconName(self):
        return self._getString(15)

    def setIconName(self, value):
        self._setString(15, value)

    def getDescription(self):
        return self._getString(16)

    def setDescription(self, value):
        self._setString(16, value)

    def getRarity(self):
        return RewardRarity(self._getString(17))

    def setRarity(self, value):
        self._setString(17, value.value)

    def getState(self):
        return RewardState(self._getString(18))

    def setState(self, value):
        self._setString(18, value.value)

    def _initialize(self):
        super(RewardsModel, self)._initialize()
        self._addNumberProperty('chapter', 0)
        self._addNumberProperty('step', 0)
        self._addNumberProperty('price', 0)
        self._addNumberProperty('amount', 0)
        self._addStringProperty('id', '')
        self._addStringProperty('name', '')
        self._addStringProperty('iconName', '')
        self._addStringProperty('description', '')
        self._addStringProperty('rarity', RewardRarity.COMMON.value)
        self._addStringProperty('state', RewardState.NOTAVAILABLE.value)
