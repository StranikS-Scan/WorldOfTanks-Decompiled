# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/gen/view_models/views/battle/views/fort_rush_vehicle_selector_view_model.py
from enum import Enum
from frameworks.wulf import Array, ViewModel
from fort_rush.gui.impl.gen.view_models.views.battle.views.fort_rush_playlist_item_model import FortRushPlaylistItemModel

class AnnouncementTypeEnum(Enum):
    NONE = 'none'
    TEXT = 'text'
    RESPAWN = 'respawn'


class FortRushVehicleSelectorViewModel(ViewModel):
    __slots__ = ('onTankSelected', 'onBattleButtonClicked')

    def __init__(self, properties=10, commands=2):
        super(FortRushVehicleSelectorViewModel, self).__init__(properties=properties, commands=commands)

    def getSelectedTankId(self):
        return self._getNumber(0)

    def setSelectedTankId(self, value):
        self._setNumber(0, value)

    def getIsAnnouncementVisible(self):
        return self._getBool(1)

    def setIsAnnouncementVisible(self, value):
        self._setBool(1, value)

    def getAnnouncementCountdownTargetTime(self):
        return self._getReal(2)

    def setAnnouncementCountdownTargetTime(self, value):
        self._setReal(2, value)

    def getAnnouncementHeading(self):
        return self._getString(3)

    def setAnnouncementHeading(self, value):
        self._setString(3, value)

    def getAnnouncementDescription(self):
        return self._getString(4)

    def setAnnouncementDescription(self, value):
        self._setString(4, value)

    def getAnnouncementType(self):
        return AnnouncementTypeEnum(self._getString(5))

    def setAnnouncementType(self, value):
        self._setString(5, value.value)

    def getSelectedPlaylistId(self):
        return self._getString(6)

    def setSelectedPlaylistId(self, value):
        self._setString(6, value)

    def getPlaylists(self):
        return self._getArray(7)

    def setPlaylists(self, value):
        self._setArray(7, value)

    @staticmethod
    def getPlaylistsType():
        return FortRushPlaylistItemModel

    def getEligibleVehicleTiers(self):
        return self._getArray(8)

    def setEligibleVehicleTiers(self, value):
        self._setArray(8, value)

    @staticmethod
    def getEligibleVehicleTiersType():
        return int

    def getForbiddenVehClasses(self):
        return self._getArray(9)

    def setForbiddenVehClasses(self, value):
        self._setArray(9, value)

    @staticmethod
    def getForbiddenVehClassesType():
        return unicode

    def _initialize(self):
        super(FortRushVehicleSelectorViewModel, self)._initialize()
        self._addNumberProperty('selectedTankId', 0)
        self._addBoolProperty('isAnnouncementVisible', False)
        self._addRealProperty('announcementCountdownTargetTime', -1)
        self._addStringProperty('announcementHeading', '')
        self._addStringProperty('announcementDescription', '')
        self._addStringProperty('announcementType', AnnouncementTypeEnum.NONE.value)
        self._addStringProperty('selectedPlaylistId', '')
        self._addArrayProperty('playlists', Array())
        self._addArrayProperty('eligibleVehicleTiers', Array())
        self._addArrayProperty('forbiddenVehClasses', Array())
        self.onTankSelected = self._addCommand('onTankSelected')
        self.onBattleButtonClicked = self._addCommand('onBattleButtonClicked')
