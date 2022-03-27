# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/battle_queue/strongholds_queue.py
import BigWorld
import MusicControllerWWISE
import constants
from PlayerEvents import g_playerEvents
from adisp import process, async
from client_request_lib.exceptions import ResponseCodes
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.event_boards.formaters import getClanTag
from gui.Scaleform.daapi.view.lobby.rally import vo_converters
from gui.Scaleform.daapi.view.meta.BattleStrongholdsQueueMeta import BattleStrongholdsQueueMeta
from frameworks.wulf import WindowLayer
from gui.shared.view_helpers.blur_manager import CachedBlur
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl import backport
from gui.prb_control import prbEntityProperty
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from gui.shared.view_helpers import ClanEmblemsHelper
from gui.shared.image_helper import getTextureLinkByID, ImagesFetchCoordinator
from gui.sounds.ambients import BattleQueueEnv
from helpers import dependency, i18n, time_utils, int2roman
from helpers.i18n import makeString
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from skeletons.gui.shared import IItemsCache

class BattleStrongholdsQueue(BattleStrongholdsQueueMeta, LobbySubView, ClanEmblemsHelper, IGlobalListener):
    __sound_env__ = BattleQueueEnv
    itemsCache = dependency.descriptor(IItemsCache)
    ANIMATION_DEFAULT_DURATION = 5

    def __init__(self, _=None):
        super(BattleStrongholdsQueue, self).__init__()
        self.__timerCallback = None
        self.__startAnimationTime = None
        self.__animationDuration = self.ANIMATION_DEFAULT_DURATION
        self.__groups = []
        self.__battleQueueVO = {}
        self.__imagesFetchCoordinator = ImagesFetchCoordinator()
        self._blur = CachedBlur()
        return

    @prbEntityProperty
    def prbEntity(self):
        return None

    def exitClick(self):
        self.prbEntity.exitFromQueue()

    def onClanEmblem32x32Received(self, clanDbID, emblem):
        clanEmblem = getTextureLinkByID(self.getMemoryTexturePath(emblem)) if emblem else None
        self.__battleQueueVO['myClanIcon'] = clanEmblem or ''
        self.as_setTypeInfoS(self.__battleQueueVO)
        self.prbEntity.getMatchmakingInfo(callback=self.__onMatchmakingInfo)
        return

    def onEscape(self):
        dialogsContainer = self.app.containerManager.getContainer(WindowLayer.TOP_WINDOW)
        if not dialogsContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.LOBBY_MENU}):
            self.fireEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_MENU)), scope=EVENT_BUS_SCOPE.LOBBY)

    def onStartBattle(self):
        self.__stopUpdateScreen()

    def onStrongholdMaintenance(self, showWindow):
        self.__showBattleRoom()

    def onUnitFlagsChanged(self, flags, timeLeft):
        if not self.prbEntity.canShowStrongholdsBattleQueue():
            self.__showBattleRoom()

    def onUpdateHeader(self, header, isFirstBattle, isUnitFreezed):
        self.__battleQueueVO['title'] = self.__getTitle()
        self.as_setTypeInfoS(self.__battleQueueVO)
        self.__requestClanIcon()

    def _populate(self):
        super(BattleStrongholdsQueue, self)._populate()
        self._blur.enable()
        self.addListener(events.GameEvent.SHOW_EXTERNAL_COMPONENTS, self._onShowExternals, scope=EVENT_BUS_SCOPE.GLOBAL)
        self.addListener(events.GameEvent.HIDE_EXTERNAL_COMPONENTS, self._onHideExternals, scope=EVENT_BUS_SCOPE.GLOBAL)
        self.startPrbListening()
        self.addListener(events.StrongholdEvent.STRONGHOLD_ON_TIMER, self.__onMatchmakingTimerChanged, scope=EVENT_BUS_SCOPE.STRONGHOLD)
        g_playerEvents.onArenaCreated += self.onStartBattle
        if self.prbEntity is not None:
            permissions = self.prbEntity.getPermissions()
            self.as_showExitS(permissions.canStopBattleQueue())
        self.as_showWaitingS('')
        self.__battleQueueVO = self.__getBattleQueueVO()
        self.__requestClanIcon()
        MusicControllerWWISE.play()
        return

    def _dispose(self):
        self.__stopUpdateScreen()
        g_playerEvents.onArenaCreated -= self.onStartBattle
        self.stopPrbListening()
        self.removeListener(events.StrongholdEvent.STRONGHOLD_ON_TIMER, self.__onMatchmakingTimerChanged, scope=EVENT_BUS_SCOPE.STRONGHOLD)
        self.__imagesFetchCoordinator.fini()
        self.removeListener(events.GameEvent.SHOW_EXTERNAL_COMPONENTS, self._onShowExternals, scope=EVENT_BUS_SCOPE.GLOBAL)
        self.removeListener(events.GameEvent.HIDE_EXTERNAL_COMPONENTS, self._onHideExternals, scope=EVENT_BUS_SCOPE.GLOBAL)
        self._blur.fini()
        super(BattleStrongholdsQueue, self)._dispose()

    def __getBattleQueueVO(self):
        return {'iconLabel': constants.ARENA_GUI_TYPE_LABEL.LABELS[constants.ARENA_GUI_TYPE.SORTIE_2],
         'title': self.__getTitle(),
         'leagueIcon': '',
         'myClanIcon': '',
         'myClanName': '',
         'myClanElo': text_styles.highTitleDisabled('--'),
         'myClanRating': ''}

    def __requestClanIcon(self):
        myClanIcon = self.__battleQueueVO['myClanIcon']
        if not myClanIcon:
            entity = self.prbEntity
            if entity is not None and entity.isStrongholdSettingsValid():
                clan = entity.getStrongholdSettings().getHeader().getClan()
                self.requestClanEmblem32x32(clan.getId())
                self.__battleQueueVO['myClanName'] = getClanTag(clan.getTag(), clan.getColor())
        return

    def __getTitle(self):
        entity = self.prbEntity
        if entity is not None and entity.isStrongholdSettingsValid():
            header = entity.getStrongholdSettings().getHeader()
            if header.isSortie():
                level = int2roman(header.getMaxLevel())
                title = makeString(FORTIFICATIONS.STRONGHOLDINFO_SORTIE) % {'level': level}
            else:
                direction = vo_converters.getDirection(header.getDirection())
                title = makeString(FORTIFICATIONS.STRONGHOLDINFO_STRONGHOLD) % {'direction': direction}
        else:
            title = ''
        return title

    @async
    @process
    def __parseClanData(self, clanData, serviceLeaguesEnabled, callback):
        updateData = {}
        myClanName = getClanTag(clanData.get('tag'), clanData.get('color') or '')
        if myClanName:
            updateData['myClanName'] = myClanName
        myClanIcon = yield self.__imagesFetchCoordinator.fetchImageByUrl(clanData.get('emblem'), oneUse=False)
        if myClanIcon:
            updateData['myClanIcon'] = myClanIcon
        leagueIcon = yield self.__imagesFetchCoordinator.fetchImageByUrl(clanData.get('back_emblem'), oneUse=False)
        if leagueIcon:
            updateData['leagueIcon'] = leagueIcon
        if serviceLeaguesEnabled:
            myClanRating = clanData.get('position')
            if isinstance(myClanRating, int):
                textStyle = text_styles.highTitle
                updateData['myClanRating'] = textStyle(backport.getNiceNumberFormat(myClanRating))
            else:
                textStyle = text_styles.highTitleDisabled
                updateData['myClanRating'] = textStyle('--')
        else:
            textStyle = text_styles.highTitleDisabled
        myClanElo = clanData.get('elo')
        if isinstance(myClanElo, int):
            updateData['myClanElo'] = textStyle(backport.getNiceNumberFormat(myClanElo))
        callback(updateData)

    @async
    @process
    def __parseGroupsData(self, groupsData, callback):
        groups = []
        for group in groupsData:
            clans = []
            for clan in group.get('clans', []):
                clanVO = {'title': makeString(FORTIFICATIONS.BATTLEQUEUE_CLANPOSITION, position='--'),
                 'clanName': getClanTag(clan.get('tag'), clan.get('color') or ''),
                 'clanElo': '--',
                 'tooltip': ''}
                leagueIconUrl = clan.get('back_emblem')
                if leagueIconUrl:
                    clanVO['leagueIcon'] = yield self.__imagesFetchCoordinator.fetchImageByUrl(clan.get('back_emblem'), oneUse=False)
                    if not clanVO['leagueIcon']:
                        callback([])
                        return
                clanVO['clanIcon'] = yield self.__imagesFetchCoordinator.fetchImageByUrl(clan.get('emblem'), oneUse=False)
                if not clanVO['clanIcon']:
                    callback([])
                    return
                elo = clan.get('elo')
                if isinstance(elo, int):
                    clanVO['clanElo'] = backport.getNiceNumberFormat(elo)
                position = clan.get('position')
                if isinstance(position, int):
                    position = backport.getNiceNumberFormat(position)
                    clanVO['title'] = makeString(FORTIFICATIONS.BATTLEQUEUE_CLANPOSITION, position=position)
                clans.append(clanVO)

            groups.append({'title': group.get('title'),
             'leagues': clans})

        callback(groups)

    @process
    def __onMatchmakingInfo(self, response):
        if response.getCode() == ResponseCodes.NO_ERRORS and response.getData():
            data = response.getData()
            self.__animationDuration = data.get('animation_time', self.ANIMATION_DEFAULT_DURATION)
            groupsData = data.get('groups', [])
            updateData = yield self.__parseClanData(data.get('clan', {}), bool(groupsData))
            self.__battleQueueVO.update(updateData)
            self.as_setTypeInfoS(self.__battleQueueVO)
            self.__groups = yield self.__parseGroupsData(groupsData)

    def __stopUpdateScreen(self):
        if self.__timerCallback is not None:
            BigWorld.cancelCallback(self.__timerCallback)
            self.__timerCallback = None
        return

    def __onMatchmakingTimerChanged(self, event):
        data = event.ctx
        if data['dtime'] > 0 and data['textid'] in (TOOLTIPS.STRONGHOLDS_TIMER_SQUADINQUEUE, FORTIFICATIONS.ROSTERINTROWINDOW_INTROVIEW_FORTBATTLES_NEXTTIMEOFBATTLESOON):
            timerLabel = i18n.makeString(FORTIFICATIONS.BATTLEQUEUE_WAITBATTLE)
            currentTime = data['dtime']
        else:
            _, unit = self.prbEntity.getUnit()
            currentTime = 0
            if unit:
                timestamp = unit.getModalTimestamp()
                if timestamp:
                    currentTime = max(0, int(time_utils.getServerUTCTime() - timestamp))
            if data['isSortie'] or data['isFirstBattle']:
                timerLabel = i18n.makeString(FORTIFICATIONS.BATTLEQUEUE_SEARCHENEMY)
            else:
                timerLabel = i18n.makeString(FORTIFICATIONS.BATTLEQUEUE_WAITBATTLE)
        timeLabel = '%d:%02d' % divmod(currentTime, 60)
        self.as_setTimerS(timerLabel, timeLabel)
        n = len(self.__groups)
        if n != 0:
            self.as_hideWaitingS()
            if self.__startAnimationTime is None:
                self.__startAnimationTime = time_utils.getCurrentTimestamp()
            i, r = divmod(int(time_utils.getCurrentTimestamp() - self.__startAnimationTime), self.__animationDuration)
            if r == 0:
                self.as_setLeaguesS(self.__groups[i % n])
        return

    @staticmethod
    def __showBattleRoom():
        g_eventDispatcher.loadStrongholds()
        g_eventDispatcher.loadHangar()

    def _onHideExternals(self, _):
        self._blur.disable()

    def _onShowExternals(self, _):
        self._blur.enable()
