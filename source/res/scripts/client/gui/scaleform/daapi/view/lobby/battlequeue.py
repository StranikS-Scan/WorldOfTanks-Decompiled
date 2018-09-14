# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/BattleQueue.py
import BigWorld
import constants
import MusicController
from gui import prb_control, makeHtmlString
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.game_control import getFalloutCtrl
from gui.prb_control import prb_getters
import gui.prb_control.prb_getters
from gui.prb_control.prb_helpers import preQueueFunctionalProperty, prbDispatcherProperty
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from helpers.i18n import makeString
from PlayerEvents import g_playerEvents
from gui.prb_control.dispatcher import g_prbLoader
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.view.meta.BattleQueueMeta import BattleQueueMeta

class BattleQueue(BattleQueueMeta, LobbySubView):
    TYPES_ORDERED = (('heavyTank', '#item_types:vehicle/tags/heavy_tank/name'),
     ('mediumTank', '#item_types:vehicle/tags/medium_tank/name'),
     ('lightTank', '#item_types:vehicle/tags/light_tank/name'),
     ('AT-SPG', '#item_types:vehicle/tags/at-spg/name'),
     ('SPG', '#item_types:vehicle/tags/spg/name'))
    DIVISIONS_ORDERED = (constants.PREBATTLE_COMPANY_DIVISION.JUNIOR,
     constants.PREBATTLE_COMPANY_DIVISION.MIDDLE,
     constants.PREBATTLE_COMPANY_DIVISION.CHAMPION,
     constants.PREBATTLE_COMPANY_DIVISION.ABSOLUTE)

    def __init__(self, ctx = None):
        super(BattleQueue, self).__init__()
        self.createTime = 0
        self.__timerCallback = None
        self.__queueCallback = None
        self.__inited = False
        return

    def _populate(self):
        super(BattleQueue, self)._populate()
        g_playerEvents.onQueueInfoReceived += self.onQueueInfoReceived
        g_playerEvents.onArenaCreated += self.onStartBattle
        self.__updateQueueInfo()
        self.__updateTimer()
        self.__updateClientState()
        MusicController.g_musicController.play(MusicController.MUSIC_EVENT_LOBBY)
        MusicController.g_musicController.play(MusicController.AMBIENT_EVENT_LOBBY)

    def _dispose(self):
        self.__stopUpdateScreen()
        g_playerEvents.onQueueInfoReceived -= self.onQueueInfoReceived
        g_playerEvents.onArenaCreated -= self.onStartBattle
        super(BattleQueue, self)._dispose()

    def __updateClientState(self):
        dispatcher = g_prbLoader.getDispatcher()
        queueType = None
        if dispatcher is not None:
            queueType = dispatcher.getPreQueueFunctional().getEntityType()
            permissions = dispatcher.getUnitFunctional().getPermissions()
            if permissions and not permissions.canExitFromQueue():
                self.as_showExitS(False)
        postFix = ''
        if self.__isInEventBattles():
            queueType = constants.ARENA_GUI_TYPE.EVENT_BATTLES
            battleType = getFalloutCtrl().getBattleType()
            if battleType == constants.FALLOUT_BATTLE_TYPE.MULTITEAM:
                postFix = '/multiteam'
        guiType = prb_getters.getArenaGUIType(queueType=queueType)
        title = '#menu:loading/battleTypes/%d%s' % (guiType, postFix)
        description = '#menu:loading/battleTypes/desc/%d%s' % (guiType, postFix)
        if guiType != constants.ARENA_GUI_TYPE.UNKNOWN and guiType in constants.ARENA_GUI_TYPE_LABEL.LABELS:
            iconlabel = constants.ARENA_GUI_TYPE_LABEL.LABELS[guiType]
        else:
            iconlabel = 'neutral'
        self.as_setTypeInfoS(iconlabel, title, description)
        return

    @preQueueFunctionalProperty
    def preQueueFunctional(self):
        return None

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def onEscape(self):
        dialogsContainer = self.app.containerManager.getContainer(ViewTypes.TOP_WINDOW)
        if not dialogsContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.LOBBY_MENU}):
            self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_MENU), scope=EVENT_BUS_SCOPE.LOBBY)

    def startClick(self):
        currPlayer = BigWorld.player()
        if currPlayer is not None and hasattr(currPlayer, 'createArenaFromQueue'):
            currPlayer.createArenaFromQueue()
        return

    def exitClick(self):
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is not None:
            dispatcher.exitFromQueue()
        return

    def onQueueInfoReceived(self, randomsQueueInfo, companiesQueueInfo, _, eventQueueInfo):
        if gui.prb_control.prb_getters.isCompany():
            data = {'title': '#menu:prebattle/typesCompaniesTitle',
             'data': list()}
            self.flashObject.as_setPlayers(makeHtmlString('html_templates:lobby/queue/playersLabel', 'teams', {'count': sum(companiesQueueInfo['divisions'])}))
            vDivisions = companiesQueueInfo['divisions']
            if vDivisions is not None:
                vClassesLen = len(vDivisions)
                for vDivision in BattleQueue.DIVISIONS_ORDERED:
                    data['data'].append(('#menu:prebattle/CompaniesTitle/%s' % constants.PREBATTLE_COMPANY_DIVISION_NAMES[vDivision], vDivisions[vDivision] if vDivision < vClassesLen else 0))

                self.as_setListByTypeS(data)
            self.as_showStartS(constants.IS_DEVELOPMENT)
        elif self.__isInEventBattles():
            info = dict(eventQueueInfo)
            vClasses = info.get('classes', [])
            vClassesLen = len(vClasses)
            totalPlayers = info.get('players', 0)
            self.flashObject.as_setPlayers(makeHtmlString('html_templates:lobby/queue/playersLabel', 'players', {'count': totalPlayers}))
            if vClassesLen:
                data = {'title': '#menu:prebattle/typesTitle',
                 'data': []}
                vClassesData = data['data']
                for vClass, message in BattleQueue.TYPES_ORDERED:
                    idx = constants.VEHICLE_CLASS_INDICES[vClass]
                    vClassesData.append((message, vClasses[idx] if idx < vClassesLen else 0))

                self.as_setListByTypeS(data)
        else:
            info = dict(randomsQueueInfo)
            if 'classes' in info:
                vClasses = info['classes']
                vClassesLen = len(vClasses)
            else:
                vClasses = []
                vClassesLen = 0
            self.flashObject.as_setPlayers(makeHtmlString('html_templates:lobby/queue/playersLabel', 'players', {'count': sum(vClasses)}))
            if vClassesLen:
                data = {'title': '#menu:prebattle/typesTitle',
                 'data': []}
                vClassesData = data['data']
                for vClass, message in BattleQueue.TYPES_ORDERED:
                    idx = constants.VEHICLE_CLASS_INDICES[vClass]
                    vClassesData.append((message, vClasses[idx] if idx < vClassesLen else 0))

                self.as_setListByTypeS(data)
            self.as_showStartS(constants.IS_DEVELOPMENT and sum(vClasses) > 1)
        if not self.__inited:
            self.__inited = True
        return

    def onStartBattle(self):
        self.__stopUpdateScreen()

    def __stopUpdateScreen(self):
        if self.__timerCallback is not None:
            BigWorld.cancelCallback(self.__timerCallback)
            self.__timerCallback = None
        if self.__queueCallback is not None:
            BigWorld.cancelCallback(self.__queueCallback)
            self.__queueCallback = None
        return

    def __updateQueueInfo(self):
        self.__queueCallback = None
        currPlayer = BigWorld.player()
        if currPlayer is not None and hasattr(currPlayer, 'requestQueueInfo'):
            if gui.prb_control.prb_getters.isCompany():
                qType = constants.QUEUE_TYPE.COMPANIES
            elif self.__isInEventBattles():
                qType = constants.QUEUE_TYPE.EVENT_BATTLES
            else:
                qType = constants.QUEUE_TYPE.RANDOMS
            currPlayer.requestQueueInfo(qType)
            self.__queueCallback = BigWorld.callback(5, self.__updateQueueInfo)
        return

    def __updateTimer(self):
        self.__timerCallback = None
        self.__timerCallback = BigWorld.callback(1, self.__updateTimer)
        textLabel = makeString('#menu:prebattle/timerLabel')
        timeLabel = '%d:%02d' % divmod(self.createTime, 60)
        self.flashObject.as_setTimer(textLabel, timeLabel)
        self.createTime += 1
        return

    def __isInEventBattles(self):
        if self.prbDispatcher:
            isInFallout = self.prbDispatcher.getFunctionalState().isInFallout()
        else:
            isInFallout = False
        return prb_getters.isInEventBattlesQueue() or isInFallout
