# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/weekend_brawl/ability_choice_panel.py
import BigWorld
import CommandMapping
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.battle_control.controllers.points_of_interest_ctrl import IPointOfInterestListener
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.battle.shared.attention_effect_player import AttentionEffectPlayer
from gui.Scaleform.daapi.view.meta.AbilityChoicePanelMeta import AbilityChoicePanelMeta
from gui.Scaleform.genConsts.WEEKEND_BRAWL_CONSTS import WEEKEND_BRAWL_CONSTS
from gui.Scaleform.locale.READABLE_KEY_NAMES import READABLE_KEY_NAMES
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from gui.shared.events import GameEvent
from items.vehicles import getItemByCompactDescr
from helpers import dependency
from helpers.i18n import makeString
from PlayerEvents import g_playerEvents
from ReplayEvents import g_replayEvents
from skeletons.gui.battle_session import IBattleSessionProvider
from weekend_brawl_common import VehiclePOIStatus
_STR_PATH = R.strings.weekend_brawl.abilityChoicePanel
_SHORT_STATES = (WEEKEND_BRAWL_CONSTS.ABILITY_STATE_COMPACT, WEEKEND_BRAWL_CONSTS.ABILITY_STATE_NOT_AVAILABLE)
_COLLAPSED_TIME = 5
_HIDDEN_TIME = 18

def _getFireKey(command):
    key, _ = CommandMapping.g_instance.getCommandKeys(command)
    return makeString(READABLE_KEY_NAMES.key(BigWorld.keyToString(key)))


def _getCommonInfo(item):
    return {'type': item.name,
     'title': item.userString}


def _getInspireVO(item):
    vo = _getCommonInfo(item)
    roleFactor = item.increaseFactors['crewRolesFactor']
    vo['descr'] = text_styles.mainBig(backport.text(_STR_PATH.abilityCard.inspire.descr(), percent=text_styles.tutorial(backport.text(_STR_PATH.abilityCard.percents(), count=int(round((roleFactor - 1) * 100)))), radius=text_styles.tutorial(backport.text(_STR_PATH.abilityCard.meters(), count=int(item.radius))), duration=text_styles.tutorial(backport.text(_STR_PATH.abilityCard.seconds(), count=int(item.duration))), extra=text_styles.tutorial(backport.text(_STR_PATH.abilityCard.seconds(), count=int(item.inactivationDelay)))))
    vo['fireKey'] = _getFireKey(CommandMapping.CMD_CM_ABILITY_PANEL_FIRE_KEY_1)
    return vo


def _getSmokeVO(item):
    vo = _getCommonInfo(item)
    vo['descr'] = text_styles.mainBig(backport.text(_STR_PATH.abilityCard.smoke.descr(), length=text_styles.tutorial(int(item.areaLength)), width=text_styles.tutorial(backport.text(_STR_PATH.abilityCard.meters(), count=int(item.areaWidth))), count=text_styles.tutorial(backport.text(_STR_PATH.abilityCard.units(), count=item.projectilesNumber)), duration=text_styles.tutorial(backport.text(_STR_PATH.abilityCard.seconds(), count=int(item.totalDuration))), visibility=text_styles.tutorial(round(item.visionRadiusFactor, 2))))
    vo['fireKey'] = _getFireKey(CommandMapping.CMD_CM_ABILITY_PANEL_FIRE_KEY_4)
    return vo


def _getReconVO(item):
    vo = _getCommonInfo(item)
    vo['descr'] = text_styles.mainBig(backport.text(_STR_PATH.abilityCard.recon.descr(), duration=text_styles.tutorial(backport.text(_STR_PATH.abilityCard.seconds(), count=int(item.spottingDuration)))))
    vo['fireKey'] = _getFireKey(CommandMapping.CMD_CM_ABILITY_PANEL_FIRE_KEY_3)
    return vo


def _getBomberVO(item):
    vo = _getCommonInfo(item)
    vo['descr'] = text_styles.mainBig(backport.text(_STR_PATH.abilityCard.bomber.descr(), delay=text_styles.tutorial(backport.text(_STR_PATH.abilityCard.seconds(), count=int(item.delay)))))
    vo['fireKey'] = _getFireKey(CommandMapping.CMD_CM_ABILITY_PANEL_FIRE_KEY_2)
    return vo


_FORMATTERS = {WEEKEND_BRAWL_CONSTS.ABILITY_CARD_TYPE_INSPIRE: _getInspireVO,
 WEEKEND_BRAWL_CONSTS.ABILITY_CARD_TYPE_RECON: _getReconVO,
 WEEKEND_BRAWL_CONSTS.ABILITY_CARD_TYPE_SMOKE: _getSmokeVO,
 WEEKEND_BRAWL_CONSTS.ABILITY_CARD_TYPE_AIRSTRIKE: _getBomberVO}

class _AbilityAttentionPlayer(AttentionEffectPlayer):
    __ATTENTION_TIME = 5

    def _setDelayTime(self):
        return self.__ATTENTION_TIME


class AbilityChoicePanel(AbilityChoicePanelMeta, IPointOfInterestListener):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(AbilityChoicePanel, self).__init__()
        self.__attentionEffect = _AbilityAttentionPlayer(self)
        self.__mode = WEEKEND_BRAWL_CONSTS.ABILITY_STATE_NONE
        self.__awards = []
        self.__callbackID = None
        return

    def getPointProperties(self, properties):
        self.as_setInitDataS(self.__createVO(properties.awards))

    def onCardSelect(self, itemName):
        if self.__sessionProvider.isReplayPlaying:
            return
        self.as_showSelectedCardS(itemName)
        poiCtrl = self.__getPointOfInterestCtrl()
        poiCtrl.selectAbility(self.__awards.index(itemName))

    def selectedAbility(self, isSuccessfully):
        if isSuccessfully:
            self.__hideWidget()

    def updateAbilities(self, isAvailable=True):
        vehicle = BigWorld.player().getVehicleAttached()
        if vehicle is not None and vehicle.isAlive() and isAvailable:
            self.__showNormalWidget()
        return

    def showNotificationAnim(self):
        self.as_showHighlightAnimS()

    def hideNotificationAnim(self):
        self.as_hideHighlightAnimS()

    def _populate(self):
        super(AbilityChoicePanel, self)._populate()
        self.__addListeners()

    def _dispose(self):
        self.__hideWidget()
        self.__attentionEffect.destroy()
        self.__attentionEffect = None
        self.__removeListeners()
        self.__awards = None
        self.__mode = None
        super(AbilityChoicePanel, self)._dispose()
        return

    def __getVehicleStateCtrl(self):
        return self.__sessionProvider.shared.vehicleState

    def __getPointOfInterestCtrl(self):
        return self.__sessionProvider.dynamic.pointsOfInterest

    def __addListeners(self):
        vehicleStateCtrl = self.__getVehicleStateCtrl()
        if vehicleStateCtrl is not None:
            vehicleStateCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        if self.__sessionProvider.isReplayPlaying:
            g_replayEvents.onTimeWarpStart += self.__onReplayTimeWarpStart
        g_playerEvents.onRoundFinished += self.__onRoundFinished
        g_eventBus.addListener(GameEvent.ABILITY_CHOICE_OVERLAY, self.__toggleOverlay, scope=EVENT_BUS_SCOPE.BATTLE)
        return

    def __removeListeners(self):
        g_eventBus.removeListener(GameEvent.ABILITY_CHOICE_OVERLAY, self.__toggleOverlay, scope=EVENT_BUS_SCOPE.BATTLE)
        vehicleStateCtrl = self.__getVehicleStateCtrl()
        if vehicleStateCtrl is not None:
            vehicleStateCtrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        g_playerEvents.onRoundFinished -= self.__onRoundFinished
        if self.__sessionProvider.isReplayPlaying:
            g_replayEvents.onTimeWarpStart -= self.__onReplayTimeWarpStart
        return

    def __createVO(self, properties):
        keyName = _getFireKey(CommandMapping.CMD_CM_ABILITY_PANEL)
        return {'abilities': self.__formatAbilities(properties),
         'satelliteKey': _getFireKey(CommandMapping.CMD_CM_ABILITY_PANEL_SATELLITE_KEY),
         'compactText': backport.text(_STR_PATH.info.compactText(), key=keyName),
         'availableText': backport.text(_STR_PATH.info.availableText(), key=keyName),
         'notAvailableText': backport.text(_STR_PATH.info.notAvailableText(), key=keyName)}

    def __formatAbilities(self, itemCDs):
        res = []
        for itemCD in itemCDs:
            item = getItemByCompactDescr(itemCD)
            res.append(_FORMATTERS[item.name](item))
            self.__awards.append(item.name)

        return res

    def __onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.POINT_OF_INTEREST:
            if not self.__isNeededShow(value):
                return
            vehicleStatus = value.vehicleStatus
            if vehicleStatus == VehiclePOIStatus.CAPTURED:
                self.as_deselectAllCardsS()
                self.__showNormalWidget(isAnimated=True)
        elif state == VEHICLE_VIEW_STATE.DESTROYED:
            self.__hideWidget()

    def __onRoundFinished(self, winnerTeam, reason):
        if self.__isWidgetVisible():
            self.__hideWidget()

    def __onReplayTimeWarpStart(self):
        if self.__isWidgetVisible():
            self.__hideWidget()

    def __isWidgetVisible(self):
        return self.__mode != WEEKEND_BRAWL_CONSTS.ABILITY_STATE_NONE

    def __toggleOverlay(self, _):
        if self.__mode == WEEKEND_BRAWL_CONSTS.ABILITY_STATE_NORMAL:
            return
        if self.__mode in _SHORT_STATES:
            self.__showOverlay()
        else:
            self.__showBlockedWidget()

    def __showNormalWidget(self, isAnimated=False):
        mode = WEEKEND_BRAWL_CONSTS.ABILITY_STATE_NORMAL
        self.__mode = mode
        self.__callbackID = BigWorld.callback(_COLLAPSED_TIME, self.__showCompactWidget)
        self.as_showS(mode, isAnimated)

    def __showOverlay(self):
        extendedMode = WEEKEND_BRAWL_CONSTS.ABILITY_STATE_EXTENDED
        self.__disposeCallback()
        if self.__mode == extendedMode:
            return
        self.__mode = extendedMode
        self.__attentionEffect.setVisible(visible=False)
        keyName = _getFireKey(CommandMapping.CMD_CM_ABILITY_PANEL)
        self.as_setExtendedInfoDataS({'title': text_styles.alert(backport.text(_STR_PATH.extendedInfo.title(), key=keyName)),
         'key': keyName})
        self.as_showS(extendedMode, withAnim=False)

    def __showCompactWidget(self):
        compactMode = WEEKEND_BRAWL_CONSTS.ABILITY_STATE_COMPACT
        self.__disposeCallback()
        if self.__mode != compactMode:
            self.as_showS(compactMode, withAnim=True)
            self.__mode = compactMode
            self.__attentionEffect.setVisible(visible=True)
            self.__callbackID = BigWorld.callback(_HIDDEN_TIME, self.__showBlockedWidget)

    def __showBlockedWidget(self):
        blockedMode = WEEKEND_BRAWL_CONSTS.ABILITY_STATE_NOT_AVAILABLE
        self.__attentionEffect.setVisible(visible=False)
        self.__disposeCallback()
        if self.__mode != blockedMode:
            self.as_showS(blockedMode, withAnim=True)
            self.__mode = blockedMode

    def __hideWidget(self):
        self.__disposeCallback()
        self.__attentionEffect.setVisible(visible=False)
        if not self.__isWidgetVisible():
            return
        self.__mode = WEEKEND_BRAWL_CONSTS.ABILITY_STATE_NONE
        self.as_hideS()

    def __disposeCallback(self):
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        return

    def __isNeededShow(self, value):
        battleCtx = self.__sessionProvider.getCtx()
        return battleCtx.isCurrentPlayer(value.vehicleID)
