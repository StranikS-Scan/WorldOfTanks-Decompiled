# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/attachments_view.py
from gui.impl.gen.view_models.views.lobby.customization.customization_rarity_reward_screen_model import CustomizationRarityRewardScreenModel

class AttachmentsView(CustomizationRarityRewardScreenModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=2):
        super(AttachmentsView, self).__init__(properties=properties, commands=commands)

    def getHasNextScreen(self):
        return self._getBool(5)

    def setHasNextScreen(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(AttachmentsView, self)._initialize()
        self._addBoolProperty('hasNextScreen', False)
