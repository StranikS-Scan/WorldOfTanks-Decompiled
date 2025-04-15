# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/skeletons/gui/game_event_controller.py
import typing
from skeletons.gui.game_control import IGameController
if typing.TYPE_CHECKING:
    from Event import Event
    from HBCoinsComponent import HBCoinsComponent
    from HBFrontCouponsComponent import HBFrontCouponsComponent
    from historical_battles.gui.server_events.game_event.hero_tank import HBHeroTankController
    from historical_battles.gui.server_events.game_event.front_progress import FrontsProgressController

class IGameEventController(IGameController):
    onProgressChanged = None
    onSelectedCommanderChanged = None
    onFrontTimeStatusUpdated = None
    onSelectedFrontChanged = None
    onSubdivisionLockChanged = None
    onGameParamsChanged = None
    onDisableFrontsWidget = None
    onDisableDivisionsWidget = None
    onLobbyHeaderUpdate = None
    onShowBattleQueueView = None
    onCloseAllAwardsWindow = None
    frontDataUpdated = None
    onDivisionsExpChanged = None
    onPrbEntityStateChanged = None

    @property
    def frontsWidgetDisabled(self):
        raise NotImplementedError

    @property
    def coins(self):
        raise NotImplementedError

    @property
    def frontCoupons(self):
        raise NotImplementedError

    @property
    def frontController(self):
        raise NotImplementedError

    @property
    def heroTank(self):
        raise NotImplementedError

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    def isEnabled(self):
        raise NotImplementedError

    def isLastDay(self):
        raise NotImplementedError

    def getHoursLeft(self):
        raise NotImplementedError

    def getQuestsUpdateHoursLeft(self):
        raise NotImplementedError

    def isBattlesEnabled(self):
        raise NotImplementedError

    def isHistoricalBattlesMode(self):
        raise NotImplementedError

    def getGameEventData(self):
        raise NotImplementedError

    def getEnvironmentSettings(self):
        raise NotImplementedError

    def getMainDiscount(self):
        raise NotImplementedError

    def getEventStartTime(self):
        raise NotImplementedError

    def getEventFinishTime(self):
        raise NotImplementedError

    def getEventFinishTimeLeft(self):
        raise NotImplementedError

    def getSelectedSubdivisionIdCache(self):
        raise NotImplementedError

    def setSelectedSubdivisionIdCache(self, value):
        raise NotImplementedError

    def updateVehicle(self):
        raise NotImplementedError

    def getSelectedSubdivisionVehicles(self):
        raise NotImplementedError

    def switchPrb(self):
        raise NotImplementedError

    def selectRandomMode(self):
        raise NotImplementedError

    def isShowingProgressionView(self):
        raise NotImplementedError

    def setShowingProgressionView(self, isShow):
        raise NotImplementedError

    @property
    def isBanned(self):
        raise NotImplementedError

    @property
    def banDuration(self):
        raise NotImplementedError

    @property
    def banExpiryTime(self):
        raise NotImplementedError

    def updateFrontData(self, frontId=None, divisionID=None):
        raise NotImplementedError

    def isHBPrbActive(self):
        raise NotImplementedError

    def onDivisionLevelUp(self, divisionID, prevLvl, currLvl):
        raise NotImplementedError
