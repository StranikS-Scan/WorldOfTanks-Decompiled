# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/battle_queue/base_queue.py
import datetime
import logging
import weakref
import BigWorld
import MusicControllerWWISE
import constants
from constants import ARENA_BONUS_TYPE
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
from frameworks.wulf import WindowLayer
from gui import makeHtmlString
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.BattleQueueMeta import BattleQueueMeta
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.prb_control.entities.listener import IPreQueueListener
from gui.prb_control.entities.base.unit.listener import IUnitListener
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.view_helpers.blur_manager import CachedBlur
from gui.shared.formatters import text_styles, icons
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME, getTypeBigIconPath
from gui.shared.utils import showInvitationInWindowsBar, hideInvitationInWindowsBar
from gui.sounds.ambients import BattleQueueEnv
from helpers import dependency
from helpers.i18n import makeString
from shared_utils import CONST_CONTAINER
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.game_control import IRTSBattlesController
_logger = logging.getLogger(__name__)
TYPES_ORDERED = (('heavyTank', ITEM_TYPES.VEHICLE_TAGS_HEAVY_TANK_NAME),
 ('mediumTank', ITEM_TYPES.VEHICLE_TAGS_MEDIUM_TANK_NAME),
 ('lightTank', ITEM_TYPES.VEHICLE_TAGS_LIGHT_TANK_NAME),
 ('AT-SPG', ITEM_TYPES.VEHICLE_TAGS_AT_SPG_NAME),
 ('SPG', ITEM_TYPES.VEHICLE_TAGS_SPG_NAME))
_LONG_WAITING_LEVELS = (9, 10)
_HTMLTEMP_PLAYERSLABEL = 'html_templates:lobby/queue/playersLabel'

@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def _needShowLongWaitingWarning(lobbyContext=None):
    vehicle = g_currentVehicle.item
    return lobbyContext is not None and vehicle is not None and vehicle.type == VEHICLE_CLASS_NAME.SPG and vehicle.level in _LONG_WAITING_LEVELS


class _QueueProvider(object):

    def __init__(self, proxy, qType=constants.QUEUE_TYPE.UNKNOWN):
        super(_QueueProvider, self).__init__()
        self._proxy = weakref.proxy(proxy)
        self._queueType = qType
        self._queueCallback = None
        return

    def start(self):
        g_playerEvents.onQueueInfoReceived += self.processQueueInfo
        self.requestQueueInfo()

    def stop(self):
        g_playerEvents.onQueueInfoReceived -= self.processQueueInfo
        if self._queueCallback is not None:
            BigWorld.cancelCallback(self._queueCallback)
            self._queueCallback = None
        self._queueType = constants.QUEUE_TYPE.UNKNOWN
        self._proxy = None
        return

    def getQueueType(self):
        return self._queueType

    def requestQueueInfo(self):
        self._queueCallback = None
        currPlayer = BigWorld.player()
        if currPlayer is not None and hasattr(currPlayer, 'requestQueueInfo'):
            _logger.debug('Requestion queue info: %d', self._queueType)
            currPlayer.requestQueueInfo(self._queueType)
            self._queueCallback = BigWorld.callback(5, self.requestQueueInfo)
        return

    def processQueueInfo(self, qInfo):
        pass

    def needAdditionalInfo(self):
        return False

    def additionalInfo(self):
        pass

    def getTankInfoLabel(self):
        return makeString(MENU.PREBATTLE_TANKLABEL)

    def getTankIcon(self, vehicle):
        return getTypeBigIconPath(vehicle.type)

    def forceStart(self):
        currPlayer = BigWorld.player()
        if currPlayer is not None and hasattr(currPlayer, 'createArenaFromQueue'):
            currPlayer.createArenaFromQueue()
        return


class _RandomQueueProvider(_QueueProvider):

    def __init__(self, proxy, qType=constants.QUEUE_TYPE.UNKNOWN):
        super(_RandomQueueProvider, self).__init__(proxy, qType)
        self._needAdditionalInfo = None
        return

    def processQueueInfo(self, qInfo):
        info = dict(qInfo)
        if 'classes' in info:
            vClasses = info['classes']
            vClassesLen = len(vClasses)
        else:
            vClasses = []
            vClassesLen = 0
        self._createCommonPlayerString(sum(vClasses))
        if vClassesLen:
            vClassesData = []
            for vClass, message in TYPES_ORDERED:
                idx = constants.VEHICLE_CLASS_INDICES[vClass]
                vClassesData.append({'type': message,
                 'icon': getTypeBigIconPath(vClass),
                 'count': vClasses[idx] if idx < vClassesLen else 0})

            self._proxy.as_setDPS(vClassesData)
        self._proxy.as_showStartS(self._isStartButtonDisplayed(vClasses))

    def needAdditionalInfo(self):
        if self._needAdditionalInfo is None:
            self._needAdditionalInfo = _needShowLongWaitingWarning()
        return self._needAdditionalInfo

    def additionalInfo(self):
        return text_styles.main(makeString(MENU.PREBATTLE_WAITINGTIMEWARNING))

    @staticmethod
    def _isStartButtonDisplayed(vClasses):
        return constants.IS_DEVELOPMENT and sum(vClasses) > 1

    def _createCommonPlayerString(self, playerCount):
        self._proxy.flashObject.as_setPlayers(makeHtmlString(_HTMLTEMP_PLAYERSLABEL, 'players', {'count': playerCount}))


class _EpicQueueProvider(_RandomQueueProvider):

    def forceStart(self):
        currPlayer = BigWorld.player()
        if currPlayer is not None and hasattr(currPlayer, 'forceEpicDevStart'):
            currPlayer.forceEpicDevStart()
        return

    def getTankInfoLabel(self):
        return makeString(MENU.PREBATTLE_STARTINGTANKLABEL)


class _EventQueueProvider(_RandomQueueProvider):
    pass


class _RankedQueueProvider(_RandomQueueProvider):
    pass


class _BattleRoyaleQueueProvider(_RandomQueueProvider):

    def processQueueInfo(self, qInfo):
        playersCount = qInfo.get('players', 0)
        self._createCommonPlayerString(playersCount)
        modesData = []
        for mode in constants.BattleRoyaleMode.ALL:
            modesData.append({'type': backport.text(R.strings.menu.prebattle.battleRoyale.dyn(mode)()),
             'icon': RES_ICONS.getBattleRoyaleModeIconPath(mode),
             'count': qInfo.get(mode, 0)})

        self._proxy.as_setDPS(modesData)

    def getTankIcon(self, vehicle):
        return RES_ICONS.getBattleRoyaleTankIconPath(vehicle.nationName)


class _MapboxQueueProvider(_RandomQueueProvider):
    pass


class _RTSQueueProvider(_RandomQueueProvider):

    class AdditionalInfoType(CONST_CONTAINER):
        LONG_BOOTCAMP = 'long_bootcamp'
        IMPOSSIBLE_BOOTCAMP = 'impossible_bootcamp'
        UNBALANCED_COMMANDERS = 'unbalanced_commanders'
        SPG_TANKER = 'spg_tanker'
        EMPTY = 'empty'

    __LONGER_WAITING_TIME = 15
    __IMPOSSIBLE_WAITING_TIME = 180
    __rtsController = dependency.descriptor(IRTSBattlesController)
    __resourcePath = R.strings.rts_battles.battleQueue.widget
    __resourceIconPath = R.images.gui.maps.icons.rtsBattles.battleQueue
    __modeResource = {constants.RTSQueueModes.TANKMEN: 'tankman',
     constants.RTSQueueModes.COMMANDERS: 'commander'}
    __additionalInfoType = AdditionalInfoType.EMPTY

    def __init__(self, proxy, qType=constants.QUEUE_TYPE.UNKNOWN):
        super(_RTSQueueProvider, self).__init__(proxy, qType)
        self.__lastTankmenAvgWaitTime = 0
        self.__isProposalActive = False

    def start(self):
        self.__rtsController.onCommanderInvitation += self.__updateQueue
        super(_RTSQueueProvider, self).start()

    def stop(self):
        self.__lastTankmenAvgWaitTime = 0
        self.__rtsController.onCommanderInvitation -= self.__updateQueue
        super(_RTSQueueProvider, self).stop()

    def _getModesToProcess(self):
        queueType = self.getQueueType()
        return [constants.RTSQueueModes.COMMANDERS] if queueType in [constants.QUEUE_TYPE.RTS_1x1, constants.QUEUE_TYPE.RTS_BOOTCAMP] else constants.RTSQueueModes.ALL

    def getTankInfoLabel(self):
        return makeString(MENU.PREBATTLE_RTS_TANKLABEL)

    def processQueueInfo(self, qInfo):
        playersCount = qInfo.get('players', 0)
        self._createCommonPlayerString(playersCount)
        modes = []
        modesToProcess = self._getModesToProcess()
        for mode in modesToProcess:
            resourceName = self.__modeResource[mode]
            subItems = []
            if 'classes' in qInfo and mode == constants.RTSQueueModes.TANKMEN:
                vClasses = qInfo['classes']
                vClassesLen = len(vClasses)
            else:
                vClasses = []
                vClassesLen = 0
            if vClassesLen:
                for vClass, message in TYPES_ORDERED:
                    idx = constants.VEHICLE_CLASS_INDICES[vClass]
                    subItems.append({'type': message,
                     'icon': backport.image(self.__resourceIconPath.dyn(vClass.replace('-', '_'))()),
                     'count': vClasses[idx] if idx < vClassesLen else 0})

            modes.append({'type': backport.text(self.__resourcePath.dyn(resourceName)()),
             'icon': backport.image(self.__resourceIconPath.dyn(resourceName)()),
             'count': qInfo.get(mode, 0),
             'subItems': subItems})

        self._proxy.as_setRTSDPS(modes)
        self.__lastTankmenAvgWaitTime = qInfo.get('avgWaitTimeTankmen', 0)
        self.__checkHideProposal()
        if self.getQueueType() == constants.QUEUE_TYPE.RTS:
            self._proxy.setCommanderInfo(qInfo['avgWaitTimeCommander'], qInfo[constants.RTSQueueModes.COMMANDERS])

    def needAdditionalInfo(self):
        isRTSBootcamp = self.__rtsController.getBattleMode() == ARENA_BONUS_TYPE.RTS_BOOTCAMP
        isCommander = self.__rtsController.isCommander()
        isSPG = g_currentVehicle.item.type == VEHICLE_CLASS_NAME.SPG
        createTime = self._proxy.getCreateTime()
        isQueueUnbalanced = self._proxy.isQueueUnbalanced()
        self.__additionalInfoType = self.AdditionalInfoType.EMPTY
        if isRTSBootcamp and createTime > self.__LONGER_WAITING_TIME:
            self.__additionalInfoType = self.AdditionalInfoType.LONG_BOOTCAMP
            if createTime > self.__IMPOSSIBLE_WAITING_TIME:
                self.__additionalInfoType = self.AdditionalInfoType.IMPOSSIBLE_BOOTCAMP
        elif isCommander and isQueueUnbalanced:
            self.__additionalInfoType = self.AdditionalInfoType.UNBALANCED_COMMANDERS
        if not isCommander and isSPG:
            self.__additionalInfoType = self.AdditionalInfoType.SPG_TANKER
        return self.__additionalInfoType != self.AdditionalInfoType.EMPTY

    def additionalInfo(self):
        strPath = R.strings.rts_battles.battleQueue
        if self.__additionalInfoType == self.AdditionalInfoType.LONG_BOOTCAMP:
            return text_styles.main(backport.text(strPath.longQueueTime()))
        if self.__additionalInfoType == self.AdditionalInfoType.IMPOSSIBLE_BOOTCAMP:
            return text_styles.main(backport.text(strPath.impossibleQueueTime()))
        if self.__additionalInfoType == self.AdditionalInfoType.UNBALANCED_COMMANDERS:
            return text_styles.main(backport.text(strPath.longStrategistQueueTime()))
        return text_styles.main(backport.text(strPath.longSpgQueueTime())) if self.__additionalInfoType == self.AdditionalInfoType.SPG_TANKER else ''

    def __toggleOfferProposal(self):
        rtsCtrl = self.__rtsController
        if not rtsCtrl.isCommander():
            rtsBonusType = constants.ARENA_BONUS_TYPE.RTS
            amount, notExpired = rtsCtrl.getCommanderInvitation(rtsBonusType)
            if amount > 0 and notExpired:
                minAmountForBattle = rtsCtrl.getSettings().currencyAmountToBattle(constants.ARENA_BONUS_TYPE.RTS)
                if amount < minAmountForBattle:
                    self.__showProposalSwitchComponent(minAmountForBattle)
                    return
                self.__showProposalSwitchComponent()
                return
        self.__checkHideProposal()

    def __checkHideProposal(self):
        if not self.__isProposalActive:
            return
        rtsCtrl = self.__rtsController
        rtsBonusType = constants.ARENA_BONUS_TYPE.RTS
        amount, notExpired = rtsCtrl.getCommanderInvitation(rtsBonusType)
        if amount > 0 and notExpired:
            return
        self.__isProposalActive = False
        self._proxy.as_hideSwitchVehicleS()
        hideInvitationInWindowsBar()

    def __updateQueue(self, *_):
        self.__toggleOfferProposal()

    def __showProposalSwitchComponent(self, minCurrencyAmountToBattle=0):
        showBonusSection = minCurrencyAmountToBattle == 0
        self._proxy.as_showSwitchVehicleS({'vehicleName': backport.text(self.__resourcePath.team.tankman()),
         'changeTitle': backport.text(self.__resourcePath.changeTitle()) if showBonusSection else self.__getPaidChangeTitle(minCurrencyAmountToBattle),
         'btnLabel': backport.text(self.__resourcePath.btnLabel()),
         'calculatedText': backport.text(self.__resourcePath.calculatedText()),
         'waitingTime': str(datetime.timedelta(seconds=int(self.__lastTankmenAvgWaitTime)))[2:],
         'changeDescr': backport.text(self.__resourcePath.btnDescrBonus()) if showBonusSection else '',
         'bonusLabel': backport.text(self.__resourcePath.bonusLabel()) if showBonusSection else None})
        if not self.__isProposalActive:
            self.__isProposalActive = True
            showInvitationInWindowsBar()
        return

    def __getPaidChangeTitle(self, price):
        currencyIcon = backport.image(R.images.gui.maps.icons.rtsBattles.currency.rts1x7currency.icon_16())
        formattedPrice = ''.join((text_styles.bonusLocalTextGold(str(price)), icons.makeImageTag(currencyIcon)))
        return backport.text(self.__resourcePath.paidChangeTitle(), price=formattedPrice)


_PROVIDER_BY_QUEUE_TYPE = {constants.QUEUE_TYPE.RANDOMS: _RandomQueueProvider,
 constants.QUEUE_TYPE.EVENT_BATTLES: _EventQueueProvider,
 constants.QUEUE_TYPE.RANKED: _RankedQueueProvider,
 constants.QUEUE_TYPE.EPIC: _EpicQueueProvider,
 constants.QUEUE_TYPE.BATTLE_ROYALE: _BattleRoyaleQueueProvider,
 constants.QUEUE_TYPE.MAPBOX: _MapboxQueueProvider,
 constants.QUEUE_TYPE.RTS: _RTSQueueProvider,
 constants.QUEUE_TYPE.RTS_1x1: _RTSQueueProvider,
 constants.QUEUE_TYPE.RTS_BOOTCAMP: _RTSQueueProvider}

def _providerFactory(proxy, qType):
    return _PROVIDER_BY_QUEUE_TYPE.get(qType, _QueueProvider)(proxy, qType)


class BattleQueueBase(BattleQueueMeta, LobbySubView, IPreQueueListener, IUnitListener):
    __sound_env__ = BattleQueueEnv

    def __init__(self, _=None):
        super(BattleQueueBase, self).__init__()
        self._createTime = 0
        self.__timerCallback = None
        self._provider = None
        self._blur = CachedBlur()
        return

    def onEscape(self):
        dialogsContainer = self.app.containerManager.getContainer(WindowLayer.TOP_WINDOW)
        if not dialogsContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.LOBBY_MENU}):
            self.fireEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_MENU)), scope=EVENT_BUS_SCOPE.LOBBY)

    def startClick(self):
        if self._provider is not None:
            self._provider.forceStart()
        return

    def exitClick(self):
        self.prbEntity.exitFromQueue()

    def onStartBattle(self):
        self.__stopUpdateScreen()

    def _populate(self):
        super(BattleQueueBase, self)._populate()
        self._blur.enable()
        self._addListeners()
        self.__updateQueueInfo()
        self._updateTimer()
        self._updateClientState()
        MusicControllerWWISE.play()

    def _dispose(self):
        self.__stopUpdateScreen()
        self._removeListeners()
        self._blur.fini()
        super(BattleQueueBase, self)._dispose()

    def _addListeners(self):
        self.addListener(events.GameEvent.SHOW_EXTERNAL_COMPONENTS, self._onShowExternals, scope=EVENT_BUS_SCOPE.GLOBAL)
        self.addListener(events.GameEvent.HIDE_EXTERNAL_COMPONENTS, self._onHideExternals, scope=EVENT_BUS_SCOPE.GLOBAL)
        g_playerEvents.onArenaCreated += self.onStartBattle
        self.startPrbListening()

    def _removeListeners(self):
        self.stopPrbListening()
        g_playerEvents.onArenaCreated -= self.onStartBattle
        self.removeListener(events.GameEvent.SHOW_EXTERNAL_COMPONENTS, self._onShowExternals, scope=EVENT_BUS_SCOPE.GLOBAL)
        self.removeListener(events.GameEvent.HIDE_EXTERNAL_COMPONENTS, self._onHideExternals, scope=EVENT_BUS_SCOPE.GLOBAL)

    def _onHideExternals(self, _):
        self._blur.disable()

    def _onShowExternals(self, _):
        self._blur.enable()

    def _getVO(self):
        return {}

    def _updateClientState(self):
        if self.prbEntity is None:
            return
        else:
            permissions = self.prbEntity.getPermissions()
            if not permissions.canExitFromQueue():
                self.as_showExitS(False)
            self.as_setTypeInfoS(self._getVO())
            return

    def __stopUpdateScreen(self):
        if self.__timerCallback is not None:
            BigWorld.cancelCallback(self.__timerCallback)
            self.__timerCallback = None
        if self._provider is not None:
            self._provider.stop()
            self._provider = None
        return

    def __updateQueueInfo(self):
        if self.prbEntity is None:
            return
        else:
            qType = self.prbEntity.getQueueType()
            self._provider = _providerFactory(self, qType)
            self._provider.start()
            return

    def _getTimerTextAndTimeLabel(self):
        textLabel = text_styles.main(makeString(MENU.PREBATTLE_TIMERLABEL))
        timeLabel = '%d:%02d' % divmod(self._createTime, 60)
        if self._provider is not None and self._provider.needAdditionalInfo():
            timeLabel = text_styles.concatStylesToSingleLine(timeLabel, '*')
        return (textLabel, timeLabel)

    def _updateTimer(self):
        self.__timerCallback = None
        self.__timerCallback = BigWorld.callback(1, self._updateTimer)
        textLabel, timeLabel = self._getTimerTextAndTimeLabel()
        self.as_setTimerS(textLabel, timeLabel)
        self._createTime += 1
        return
