# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/gen/view_models/views/lobby/rewards_view/reward_model.py
from frameworks.wulf import ViewModel

class RewardModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(RewardModel, self).__init__(properties=properties, commands=commands)

    def getImage(self):
        return self._getString(0)

    def setImage(self, value):
        self._setString(0, value)

    def getDescription(self):
        return self._getString(1)

    def setDescription(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(RewardModel, self)._initialize()
        self._addStringProperty('image', '')
        self._addStringProperty('description', '')
