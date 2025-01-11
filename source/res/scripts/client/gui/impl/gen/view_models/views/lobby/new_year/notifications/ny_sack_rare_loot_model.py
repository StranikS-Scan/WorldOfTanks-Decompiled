# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/notifications/ny_sack_rare_loot_model.py
from gui.impl.gen.view_models.views.lobby.notifications.notification_model import NotificationModel

class NySackRareLootModel(NotificationModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=6, commands=1):
        super(NySackRareLootModel, self).__init__(properties=properties, commands=commands)

    def getUserName(self):
        return self._getString(1)

    def setUserName(self, value):
        self._setString(1, value)

    def getItemType(self):
        return self._getString(2)

    def setItemType(self, value):
        self._setString(2, value)

    def getIconName(self):
        return self._getString(3)

    def setIconName(self, value):
        self._setString(3, value)

    def getAmount(self):
        return self._getNumber(4)

    def setAmount(self, value):
        self._setNumber(4, value)

    def getIsButtonDisabled(self):
        return self._getBool(5)

    def setIsButtonDisabled(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(NySackRareLootModel, self)._initialize()
        self._addStringProperty('userName', '')
        self._addStringProperty('itemType', '')
        self._addStringProperty('iconName', '')
        self._addNumberProperty('amount', 0)
        self._addBoolProperty('isButtonDisabled', False)
        self.onClick = self._addCommand('onClick')
