# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/missions/bonuses/extended_icon_bonus_model.py
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel

class ExtendedIconBonusModel(IconBonusModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(ExtendedIconBonusModel, self).__init__(properties=properties, commands=commands)

    def getUserName(self):
        return self._getString(7)

    def setUserName(self, value):
        self._setString(7, value)

    def _initialize(self):
        super(ExtendedIconBonusModel, self)._initialize()
        self._addStringProperty('userName', '')
