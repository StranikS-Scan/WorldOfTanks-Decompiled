# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: event_platform/scripts/client/event_platform/gui/impl/gen/view_models/views/lobby/test_view/advanced_award_model.py
from event_platform.gui.impl.gen.view_models.views.lobby.test_view.award_model import AwardModel

class AdvancedAwardModel(AwardModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(AdvancedAwardModel, self).__init__(properties=properties, commands=commands)

    def getAwardDescription(self):
        return self._getString(4)

    def setAwardDescription(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(AdvancedAwardModel, self)._initialize()
        self._addStringProperty('awardDescription', '')
