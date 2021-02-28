# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/missions/bonuses/overlay_icon_bonus_model.py
from gui.impl.gen.view_models.common.missions.bonuses.extended_icon_bonus_model import ExtendedIconBonusModel

class OverlayIconBonusModel(ExtendedIconBonusModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(OverlayIconBonusModel, self).__init__(properties=properties, commands=commands)

    def getOverlayType(self):
        return self._getString(9)

    def setOverlayType(self, value):
        self._setString(9, value)

    def _initialize(self):
        super(OverlayIconBonusModel, self)._initialize()
        self._addStringProperty('overlayType', '')
