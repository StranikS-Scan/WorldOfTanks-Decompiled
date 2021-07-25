# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/perks_matrix/ultimate_perk_model.py
from gui.impl.gen.view_models.views.lobby.detachment.common.perk_base_model import PerkBaseModel

class UltimatePerkModel(PerkBaseModel):
    __slots__ = ()
    STATE_LOCKED = 'locked'
    STATE_OPENED = 'opened'
    STATE_SELECTED = 'selected'
    STATE_NOT_SELECTED = 'notSelected'

    def __init__(self, properties=6, commands=0):
        super(UltimatePerkModel, self).__init__(properties=properties, commands=commands)

    def getSavedState(self):
        return self._getString(3)

    def setSavedState(self, value):
        self._setString(3, value)

    def getTemporaryState(self):
        return self._getString(4)

    def setTemporaryState(self, value):
        self._setString(4, value)

    def getIsRecommended(self):
        return self._getBool(5)

    def setIsRecommended(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(UltimatePerkModel, self)._initialize()
        self._addStringProperty('savedState', 'locked')
        self._addStringProperty('temporaryState', 'locked')
        self._addBoolProperty('isRecommended', False)
