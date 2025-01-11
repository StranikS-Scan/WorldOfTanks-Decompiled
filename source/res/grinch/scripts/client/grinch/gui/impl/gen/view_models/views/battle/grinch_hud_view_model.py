# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/impl/gen/view_models/views/battle/grinch_hud_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from grinch.gui.impl.gen.view_models.views.battle.grinch_damage_indicator_model import GrinchDamageIndicatorModel
from grinch.gui.impl.gen.view_models.views.battle.grinch_hud.ability_model import AbilityModel
from grinch.gui.impl.gen.view_models.views.battle.grinch_hud.tank_panel_model import TankPanelModel
from grinch.gui.impl.gen.view_models.views.battle.grinch_marker_model import GrinchMarkerModel
from grinch.gui.impl.gen.view_models.views.battle.team_players_model import TeamPlayersModel
from grinch.gui.impl.gen.view_models.views.battle.team_score_model import TeamScoreModel

class AnnouncementIconEnum(Enum):
    NONE = ''
    GIFT = 'gift'
    FIRST = 'first'
    SECOND = 'second'
    THIRD = 'third'


class GrinchHudViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=23, commands=0):
        super(GrinchHudViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def allies(self):
        return self._getViewModel(0)

    @staticmethod
    def getAlliesType():
        return TeamPlayersModel

    @property
    def enemies1(self):
        return self._getViewModel(1)

    @staticmethod
    def getEnemies1Type():
        return TeamPlayersModel

    @property
    def enemies2(self):
        return self._getViewModel(2)

    @staticmethod
    def getEnemies2Type():
        return TeamPlayersModel

    @property
    def tankPanel(self):
        return self._getViewModel(3)

    @staticmethod
    def getTankPanelType():
        return TankPanelModel

    def getIsRespawning(self):
        return self._getBool(4)

    def setIsRespawning(self, value):
        self._setBool(4, value)

    def getIsGameStarting(self):
        return self._getBool(5)

    def setIsGameStarting(self, value):
        self._setBool(5, value)

    def getScoreLimit(self):
        return self._getNumber(6)

    def setScoreLimit(self, value):
        self._setNumber(6, value)

    def getCarryingItems(self):
        return self._getNumber(7)

    def setCarryingItems(self, value):
        self._setNumber(7, value)

    def getItemsLimit(self):
        return self._getNumber(8)

    def setItemsLimit(self, value):
        self._setNumber(8, value)

    def getTeamScore(self):
        return self._getArray(9)

    def setTeamScore(self, value):
        self._setArray(9, value)

    @staticmethod
    def getTeamScoreType():
        return TeamScoreModel

    def getAbilities(self):
        return self._getArray(10)

    def setAbilities(self, value):
        self._setArray(10, value)

    @staticmethod
    def getAbilitiesType():
        return AbilityModel

    def getIsAnnouncementVisible(self):
        return self._getBool(11)

    def setIsAnnouncementVisible(self, value):
        self._setBool(11, value)

    def getAnnouncementCountdownTargetTime(self):
        return self._getNumber(12)

    def setAnnouncementCountdownTargetTime(self, value):
        self._setNumber(12, value)

    def getAnnouncementHeading(self):
        return self._getString(13)

    def setAnnouncementHeading(self, value):
        self._setString(13, value)

    def getAnnouncementHeadingAbove(self):
        return self._getString(14)

    def setAnnouncementHeadingAbove(self, value):
        self._setString(14, value)

    def getAnnouncementIcon(self):
        return AnnouncementIconEnum(self._getString(15))

    def setAnnouncementIcon(self, value):
        self._setString(15, value.value)

    def getDamageIndicators(self):
        return self._getArray(16)

    def setDamageIndicators(self, value):
        self._setArray(16, value)

    @staticmethod
    def getDamageIndicatorsType():
        return GrinchDamageIndicatorModel

    def getTurretLimit(self):
        return self._getNumber(17)

    def setTurretLimit(self, value):
        self._setNumber(17, value)

    def getDeployedTurrets(self):
        return self._getNumber(18)

    def setDeployedTurrets(self, value):
        self._setNumber(18, value)

    def getTurretsAvailable(self):
        return self._getNumber(19)

    def setTurretsAvailable(self, value):
        self._setNumber(19, value)

    def getTurretStackReloadTimeLeft(self):
        return self._getReal(20)

    def setTurretStackReloadTimeLeft(self, value):
        self._setReal(20, value)

    def getTurretStackReloadTime(self):
        return self._getReal(21)

    def setTurretStackReloadTime(self, value):
        self._setReal(21, value)

    def getBaseMarkers(self):
        return self._getArray(22)

    def setBaseMarkers(self, value):
        self._setArray(22, value)

    @staticmethod
    def getBaseMarkersType():
        return GrinchMarkerModel

    def _initialize(self):
        super(GrinchHudViewModel, self)._initialize()
        self._addViewModelProperty('allies', TeamPlayersModel())
        self._addViewModelProperty('enemies1', TeamPlayersModel())
        self._addViewModelProperty('enemies2', TeamPlayersModel())
        self._addViewModelProperty('tankPanel', TankPanelModel())
        self._addBoolProperty('isRespawning', False)
        self._addBoolProperty('isGameStarting', True)
        self._addNumberProperty('scoreLimit', 0)
        self._addNumberProperty('carryingItems', 0)
        self._addNumberProperty('itemsLimit', 4)
        self._addArrayProperty('teamScore', Array())
        self._addArrayProperty('abilities', Array())
        self._addBoolProperty('isAnnouncementVisible', False)
        self._addNumberProperty('announcementCountdownTargetTime', -1)
        self._addStringProperty('announcementHeading', '')
        self._addStringProperty('announcementHeadingAbove', '')
        self._addStringProperty('announcementIcon', AnnouncementIconEnum.NONE.value)
        self._addArrayProperty('damageIndicators', Array())
        self._addNumberProperty('turretLimit', 0)
        self._addNumberProperty('deployedTurrets', 0)
        self._addNumberProperty('turretsAvailable', -1)
        self._addRealProperty('turretStackReloadTimeLeft', 0.0)
        self._addRealProperty('turretStackReloadTime', 0.0)
        self._addArrayProperty('baseMarkers', Array())
