# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/notifications/ny_sack_rare_loot_model.py
from gui.impl.gen.view_models.views.lobby.notifications.notification_model import NotificationModel

class NySackRareLootModel(NotificationModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=4, commands=1):
        super(NySackRareLootModel, self).__init__(properties=properties, commands=commands)

    def getUserName(self):
        return self._getString(1)

    def setUserName(self, value):
        self._setString(1, value)

    def getItemType(self):
        return self._getString(2)

    def setItemType(self, value):
        self._setString(2, value)

    def getIsButtonDisabled(self):
        return self._getBool(3)

    def setIsButtonDisabled(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(NySackRareLootModel, self)._initialize()
        self._addStringProperty('userName', '')
        self._addStringProperty('itemType', '')
        self._addBoolProperty('isButtonDisabled', False)
        self.onClick = self._addCommand('onClick')
