# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/premacc/squad_bonus_tooltip_content_model.py
from frameworks.wulf import ViewModel

class SquadBonusTooltipContentModel(ViewModel):
    __slots__ = ()

    def getCreditsBonusWithPremium(self):
        return self._getNumber(0)

    def setCreditsBonusWithPremium(self, value):
        self._setNumber(0, value)

    def getCreditsBonusWithoutPremium(self):
        return self._getNumber(1)

    def setCreditsBonusWithoutPremium(self, value):
        self._setNumber(1, value)

    def getExperienceBonus(self):
        return self._getNumber(2)

    def setExperienceBonus(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(SquadBonusTooltipContentModel, self)._initialize()
        self._addNumberProperty('creditsBonusWithPremium', 0)
        self._addNumberProperty('creditsBonusWithoutPremium', 0)
        self._addNumberProperty('experienceBonus', 0)
