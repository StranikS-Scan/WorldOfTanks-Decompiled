# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/stats.py
from gui import makeHtmlString
from gui.battle_control.arena_info.settings import INVALIDATE_OP
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from skeletons.gui.game_event_controller import IGameEventController
from PlayerEvents import g_playerEvents
from constants import ARENA_PERIOD
from gui.Scaleform.daapi.view.meta.EventStatsMeta import EventStatsMeta
from game_event_getter import GameEventGetterMixin
from debug_utils import LOG_DEBUG_DEV
from gui.impl import backport
from gui.impl.gen import R
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.shared.badges import buildBadge
from gui.Scaleform.settings import ICONS_SIZES
from helpers import dependency
_TAB_SCREEN_TEMPLATES_PATH = 'html_templates:eventHW21/tabScreen'

class EventStats(EventStatsMeta, GameEventGetterMixin, IArenaVehiclesController):
    _gameEventController = dependency.descriptor(IGameEventController)
    _VEH_EVENT_STATS_LEN = 4

    def __init__(self):
        super(EventStats, self).__init__()
        self.__arenaDP = self.sessionProvider.getArenaDP()
        self.__buffsOrder = []
        self.__buffsData = {}

    def invalidateArenaInfo(self):
        self.__updateTitleAndDescription()
        self.__updateStats()
        self.__updateBuffList()

    def invalidateVehiclesStats(self, arenaDP):
        self.__updateStats()

    def addVehicleInfo(self, vo, arenaDP):
        if not arenaDP.isAllyTeam(vo.team):
            return
        self.__updateStats()

    def updateVehiclesInfo(self, updated, arenaDP):
        self.__updateStats()

    def updateVehiclesStats(self, updated, arenaDP):
        self.__updateStats()

    def invalidateVehicleStatus(self, flags, vInfo, arenaDP):
        if INVALIDATE_OP.VEHICLE_STATUS & flags > 0:
            self.__updateStats()

    def _populate(self):
        super(EventStats, self)._populate()
        self.sessionProvider.addArenaCtrl(self)
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange
        if self.souls is not None:
            self.souls.onSoulsChanged += self.__onSoulsChanged
        if self.damageData is not None:
            self.damageData.onDamageChanged += self.__onDamageChanged
        if self.blockedDamageData is not None:
            self.blockedDamageData.onBlockedDamageChanged += self.__onBlockedDamageChanged
        if self.environmentData is not None:
            self.environmentData.onUpdated += self.__onEnvironmentChanged
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived
        g_eventBus.addListener(events.BuffUiEvent.ON_APPLY, self.__onBuffApply, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.addListener(events.BuffUiEvent.ON_UNAPPLY, self.__onBuffUnApply, scope=EVENT_BUS_SCOPE.BATTLE)
        self.invalidateArenaInfo()
        return

    def _dispose(self):
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        if self.damageData is not None:
            self.damageData.onDamageChanged -= self.__onDamageChanged
        if self.blockedDamageData is not None:
            self.blockedDamageData.onBlockedDamageChanged -= self.__onBlockedDamageChanged
        if self.souls is not None:
            self.souls.onSoulsChanged -= self.__onSoulsChanged
        if self.environmentData is not None:
            self.environmentData.onUpdated -= self.__onEnvironmentChanged
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
        g_eventBus.removeListener(events.BuffUiEvent.ON_APPLY, self.__onBuffApply, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.removeListener(events.BuffUiEvent.ON_UNAPPLY, self.__onBuffUnApply, scope=EVENT_BUS_SCOPE.BATTLE)
        self.sessionProvider.removeArenaCtrl(self)
        super(EventStats, self)._dispose()
        return

    def __updateTitleAndDescription(self):
        envData = self.environmentData
        if envData is None:
            return
        else:
            envID = envData.getCurrentEnvironmentID()
            l10nID = envData.getL10nID(envID)
            LOG_DEBUG_DEV('EventStats::__updateTitleAndDescription', envID, l10nID)
            if envID <= envData.getMaxEnvironmentID():
                title = backport.text(R.strings.event.stats.world.num(l10nID).title())
                desc = backport.text(R.strings.event.stats.world.num(l10nID).desc())
                playerVehicleID = self.__arenaDP.getPlayerVehicleID()
                if self.__arenaDP.isSquadMan(vID=playerVehicleID):
                    difficultyLevel = self._gameEventController.getSquadDifficultyLevel()
                else:
                    difficultyLevel = self._gameEventController.getSelectedDifficultyLevel()
                if envID == envData.getBossFightEnvironmentID():
                    goal = backport.text(R.strings.event.notification.bossfight_phase_1())
                else:
                    goal = backport.text(R.strings.event.resultScreen.collectMoreMatter())
                self.as_updateDataS(title, desc, difficultyLevel, goal)
            return

    def __updateStats(self):
        alliesVehInfo = [ vInfo for vInfo in self.__arenaDP.getVehiclesInfoIterator() if self.__arenaDP.isAllyTeam(vInfo.team) ]
        vehEventStats = {vInfo.vehicleID:self.__getPlayerStats(vInfo.vehicleID) for vInfo in alliesVehInfo}
        maxVehEventStats = tuple((max((t[i] for t in vehEventStats.values())) for i in range(self._VEH_EVENT_STATS_LEN)))
        self.as_updatePlayerStatsS([ self.__makePlayerInfo(vInfo, vehEventStats, maxVehEventStats) for vInfo in alliesVehInfo ])

    def __updateBuffList(self):
        buffs = []
        for buffId in self.__buffsOrder:
            iconName, textTag = self.__buffsData[buffId]
            nameRes = R.strings.event.stats.buffs.dyn(textTag).dyn('name')
            descriptionRes = R.strings.event.stats.buffs.dyn(textTag).dyn('descr')
            name = backport.text(nameRes()) if nameRes.exists() else textTag
            description = backport.text(descriptionRes()) if descriptionRes.exists() else textTag
            buffs.append({'name': name,
             'description': description,
             'imageName': iconName})

        self.as_updateBuffsS({'buffs': buffs})

    def __makePlayerInfo(self, vInfo, vehEventStats, maxVehEventStats):
        playerVehicle = self.__arenaDP.getVehicleInfo()
        playerSquad = playerVehicle.squadIndex
        vehID = vInfo.vehicleID
        badgeID = vInfo.selectedBadge
        suffixBadgeId = vInfo.selectedSuffixBadge
        isSquad = playerSquad > 0 and playerSquad == vInfo.squadIndex
        isPlayerHimself = vehID == playerVehicle.vehicleID
        vehicleTypeIcon = 'eventStatsVehicleType_platoon_{}' if isSquad or isPlayerHimself else 'eventStatsVehicleType_{}'
        playerName = vInfo.player.name
        if vInfo.player.clanAbbrev:
            playerName = '{}[{}]'.format(vInfo.player.name, vInfo.player.clanAbbrev)
        badge = buildBadge(badgeID, vInfo.getBadgeExtraInfo())
        souls, kills, damage, blocked = vehEventStats[vehID]
        maxSouls, maxKills, maxDamage, maxBlocked = maxVehEventStats
        resultVO = {'playerName': makeHtmlString(_TAB_SCREEN_TEMPLATES_PATH, 'playerName' if isPlayerHimself else 'otherPlayers', {'value': playerName}),
         'squadIndex': str(vInfo.squadIndex) if vInfo.squadIndex else '',
         'suffixBadgeIcon': 'badge_{}'.format(suffixBadgeId) if suffixBadgeId else '',
         'suffixBadgeStripIcon': 'strip_{}'.format(suffixBadgeId) if suffixBadgeId else '',
         'isAlive': vInfo.isAlive(),
         'isSquad': isSquad,
         'energy': self.__formatVehEventStat(souls, maxSouls),
         'kills': self.__formatVehEventStat(kills, maxKills),
         'damage': self.__formatVehEventStat(damage, maxDamage),
         'blocked': self.__formatVehEventStat(blocked, maxBlocked),
         'vehicleName': vInfo.vehicleType.shortName,
         'vehicleTypeIcon': vehicleTypeIcon.format(vInfo.vehicleType.classTag),
         'isPlayerHimself': isPlayerHimself}
        if badge is not None:
            resultVO['badgeVisualVO'] = badge.getBadgeVO(ICONS_SIZES.X24, {'isAtlasSource': True}, shortIconName=True)
        return resultVO

    def __formatVehEventStat(self, value, maxValue):
        valueStrTemplate = 'maxValue' if value == maxValue and value > 0 else 'regularValue'
        valueIntegralFormat = backport.getIntegralFormat(value)
        return makeHtmlString(_TAB_SCREEN_TEMPLATES_PATH, valueStrTemplate, {'value': valueIntegralFormat})

    def __getPlayerStats(self, vehID):
        souls = self.souls.getSouls(vehID) if self.souls is not None else 0
        damage = self.damageData.getDamage(vehID) if self.damageData is not None else 0
        blocked = self.blockedDamageData.getBlockedDamage(vehID) if self.blockedDamageData is not None else 0
        vStats = self.__arenaDP.getVehicleStats(vehID)
        frags = vStats.frags if vStats is not None else 0
        return (souls,
         frags,
         damage,
         blocked)

    def __onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        if period == ARENA_PERIOD.BATTLE:
            self.__updateStats()

    def __onSoulsChanged(self, diff):
        self.__updateStats()

    def __onDamageChanged(self, diff):
        self.__updateStats()

    def __onBlockedDamageChanged(self, diff):
        self.__updateStats()

    def __onEnvironmentChanged(self):
        self.__updateTitleAndDescription()

    def __onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        self.__updateStats()

    def __onBuffUnApply(self, event):
        buff = event.ctx['id']
        if buff in self.__buffsOrder:
            self.__buffsOrder.remove(buff)
            self.__buffsData.pop(buff, None)
            self.__updateBuffList()
        return

    def __onBuffApply(self, event):
        buff = event.ctx['id']
        if buff not in self.__buffsOrder:
            self.__buffsOrder.append(buff)
            self.__buffsData[buff] = (event.ctx['iconName'], event.ctx['tooltipTextTag'])
            self.__updateBuffList()
