# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/components/FortMainViewComponent.py
import time
import BigWorld
from ClientFortifiedRegion import BUILDING_UPDATE_REASON
from account_helpers.AccountSettings import AccountSettings, FORT_MEMBER_TUTORIAL, ORDERS_FILTER
from adisp import process
from constants import PREBATTLE_TYPE, FORT_BUILDING_TYPE
from debug_utils import LOG_DEBUG, LOG_ERROR
import fortified_regions
from gui import SystemMessages
from gui.Scaleform.daapi.view.lobby.fortifications import FortificationEffects, FortifiedWindowScopes
from gui.Scaleform.daapi.view.lobby.fortifications.FortRosterIntroWindow import FortRosterIntroWindow
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortSoundController import g_fortSoundController
from gui.Scaleform.genConsts.TEXT_MANAGER_STYLES import TEXT_MANAGER_STYLES
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.prb_control.context.unit_ctx import JoinModeCtx
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.settings import UNIT_MODE_FLAGS
from gui.shared import events, g_eventBus
from gui.shared import EVENT_BUS_SCOPE
from gui.Scaleform.daapi.view.meta.FortMainViewMeta import FortMainViewMeta
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.framework import AppRef
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_formatters
from gui.shared.ClanCache import g_clanCache
from gui.shared.events import FortEvent
from gui.shared.fortifications import events_dispatcher as fort_events
from gui.shared.fortifications.context import DirectionCtx
from gui.shared.fortifications.settings import FORT_BATTLE_DIVISIONS
from gui.shared.utils import CONST_CONTAINER
from helpers import i18n, time_utils, setHangarVisibility

def _checkBattleConsumesIntro(fort):
    settings = dict(AccountSettings.getSettings('fortSettings'))
    if not settings.get('battleConsumesIntroShown') and not fort.isStartingScriptNotStarted():
        fort_events.showBattleConsumesIntro()
    settings['battleConsumesIntroShown'] = True
    AccountSettings.setSettings('fortSettings', settings)


class FortMainViewComponent(FortMainViewMeta, FortViewHelper, AppRef):

    class DIR_BATTLE_TYPE(CONST_CONTAINER):
        ATTACK = 'attack'
        DEFENSE = 'defense'
        ATTACK_DEFENSE = 'atkAndDef'

    TRANSPORTING_STEP_TO_MODE = {events.FortEvent.TRANSPORTATION_STEPS.NONE: None,
     events.FortEvent.TRANSPORTATION_STEPS.FIRST_STEP: FORTIFICATION_ALIASES.MODE_TRANSPORTING_FIRST_STEP,
     events.FortEvent.TRANSPORTATION_STEPS.NEXT_STEP: FORTIFICATION_ALIASES.MODE_TRANSPORTING_NEXT_STEP,
     events.FortEvent.TRANSPORTATION_STEPS.CONFIRMED: FORTIFICATION_ALIASES.MODE_TRANSPORTING_FIRST_STEP}
    TUTORIAL_TRANSPORTING_STEP_TO_MODE = {events.FortEvent.TRANSPORTATION_STEPS.NONE: None,
     events.FortEvent.TRANSPORTATION_STEPS.FIRST_STEP: FORTIFICATION_ALIASES.MODE_TRANSPORTING_TUTORIAL_FIRST_STEP,
     events.FortEvent.TRANSPORTATION_STEPS.NEXT_STEP: FORTIFICATION_ALIASES.MODE_TRANSPORTING_TUTORIAL_NEXT_STEP,
     events.FortEvent.TRANSPORTATION_STEPS.CONFIRMED: FORTIFICATION_ALIASES.MODE_TRANSPORTING_TUTORIAL_FIRST_STEP}

    def __init__(self):
        super(FortMainViewComponent, self).__init__()
        self.__tempToggleHelperFlag = False
        self.__currentMode = FortificationEffects.NONE_STATE
        self.__currentModeIsDirty = True
        self.__commanderHelpShown = False
        self.__transportingProgress = None
        self.__clanDBID = g_clanCache.clanDBID
        return

    @process
    def updateData(self):
        _checkBattleConsumesIntro(self.fortCtrl.getFort())
        self.__updateCurrentMode()
        self.__updateHeaderMessage()
        self.as_setMainDataS(self.getData())
        self.as_setBattlesDirectionDataS({'directionsBattles': self._getDirectionsBattles()})
        clanIconId = yield g_clanCache.getClanEmblemID()
        if not self.isDisposed():
            self.as_setClanIconIdS(clanIconId)

    def onSelectOrderSelector(self, value):
        filters = AccountSettings.getFilter(ORDERS_FILTER)
        filters['isSelected'] = value
        AccountSettings.setFilter(ORDERS_FILTER, filters)

    def _getDirectionsBattles(self):
        battlesByDir = {}
        timeNow = time.time()
        fort = self.fortCtrl.getFort()
        if fort is not None:
            for attack in fort.getAttacks():
                if not attack.isEnded() and timeNow < attack.getStartTime() and attack.getStartTime() - timeNow < time_utils.ONE_DAY:
                    battlesByDir[attack.getDirection()] = (self.DIR_BATTLE_TYPE.ATTACK, attack.isHot(), TOOLTIPS.FORTIFICATION_BATTLENOTIFIER_OFFENSE)

            for defence in fort.getDefences():
                if not defence.isEnded() and timeNow < defence.getStartTime() and defence.getStartTime() - timeNow < time_utils.ONE_DAY:
                    direction = defence.getDirection()
                    if direction in battlesByDir:
                        isHot = battlesByDir[direction][1]
                        battlesByDir[direction] = (self.DIR_BATTLE_TYPE.ATTACK_DEFENSE, isHot or defence.isHot(), TOOLTIPS.FORTIFICATION_BATTLENOTIFIER_OFFANDDEF)
                    else:
                        battlesByDir[direction] = (self.DIR_BATTLE_TYPE.DEFENSE, defence.isHot(), TOOLTIPS.FORTIFICATION_BATTLENOTIFIER_DEFENSE)

        result = []
        for direction, (lbl, flashing, tooltip) in battlesByDir.iteritems():
            result.append({'battleType': lbl,
             'hasActiveBattles': flashing,
             'tooltip': tooltip,
             'direction': direction})

        return result

    def _populate(self):
        super(FortMainViewComponent, self)._populate()
        self.addListener(FortEvent.SWITCH_TO_MODE, self.__handleSwitchToMode, scope=EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.FortEvent.TRANSPORTATION_STEP, self.__onTransportingStep, scope=EVENT_BUS_SCOPE.FORT)
        self.startFortListening()
        self.updateData()
        setHangarVisibility(isVisible=False)
        self.as_setTutorialArrowVisibilityS(FORTIFICATION_ALIASES.TUTORIAL_ARROW_DEFENCE, False)
        self.as_setTutorialArrowVisibilityS(FORTIFICATION_ALIASES.TUTORIAL_ARROW_INTELLIGENCE, False)

    def _dispose(self):
        setHangarVisibility(isVisible=True)
        super(FortMainViewComponent, self)._dispose()
        self.stopFortListening()
        self.removeListener(FortEvent.SWITCH_TO_MODE, self.__handleSwitchToMode, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.FortEvent.TRANSPORTATION_STEP, self.__onTransportingStep, scope=EVENT_BUS_SCOPE.FORT)
        self.__clanDBID = None
        return

    def onWindowClose(self):
        self.destroy()

    def onEnterBuildDirectionClick(self):
        if self.fortCtrl.getFort().isStartingScriptNotStarted():
            self.__switchToMode(FORTIFICATION_ALIASES.MODE_DIRECTIONS_TUTORIAL)
        else:
            self.__switchToMode(FORTIFICATION_ALIASES.MODE_DIRECTIONS)

    def onCreateDirectionClick(self, dirId):
        self.__requestToCreate(dirId)

    @process
    def __requestToCreate(self, dirId):
        result = yield self.fortProvider.sendRequest(DirectionCtx(dirId, waitingID='fort/direction/open'))
        if result:
            g_fortSoundController.playCreateDirection()
            directionName = i18n.makeString('#fortifications:General/directionName%d' % dirId)
            SystemMessages.g_instance.pushI18nMessage(SYSTEM_MESSAGES.FORTIFICATION_DIRECTIONOPENED, direction=directionName, type=SystemMessages.SM_TYPE.Warning)
            self.__currentModeIsDirty = True

    def __onTransportingStep(self, event):
        step = event.ctx.get('step')
        isInTutorial = event.ctx.get('isInTutorial')
        if self.fortCtrl.getFort().isStartingScriptDone():
            self.__transportingProgress = self.TRANSPORTING_STEP_TO_MODE.get(step)
        else:
            self.__transportingProgress = self.TUTORIAL_TRANSPORTING_STEP_TO_MODE.get(step)
        if isInTutorial and step == events.FortEvent.TRANSPORTATION_STEPS.CONFIRMED:
            self.onFirstTransportingStep()
        self.__refreshCurrentMode()

    def onFirstTransportingStep(self):
        self.fireEvent(events.FortEvent(events.FortEvent.TRANSPORTATION_STEP, {'step': events.FortEvent.TRANSPORTATION_STEPS.FIRST_STEP}), scope=EVENT_BUS_SCOPE.FORT)

    def onNextTransportingStep(self):
        g_fortSoundController.playFirstStepTransport()
        self.fireEvent(events.FortEvent(events.FortEvent.TRANSPORTATION_STEP, {'step': events.FortEvent.TRANSPORTATION_STEPS.NEXT_STEP}), scope=EVENT_BUS_SCOPE.FORT)

    def onEnterTransportingClick(self):
        g_fortSoundController.playEnterTransport()
        self.fireEvent(events.FortEvent(events.FortEvent.TRANSPORTATION_STEP, {'step': events.FortEvent.TRANSPORTATION_STEPS.FIRST_STEP}), scope=EVENT_BUS_SCOPE.FORT)

    def onBuildingsUpdated(self, buildingsTypeIDs, cooldownPassed = False):
        if cooldownPassed:
            self.__refreshCurrentMode()

    def onLeaveTransportingClick(self):
        g_fortSoundController.playExitTransport()
        self.fireEvent(events.FortEvent(events.FortEvent.TRANSPORTATION_STEP, {'step': events.FortEvent.TRANSPORTATION_STEPS.NONE}), scope=EVENT_BUS_SCOPE.FORT)
        self.fireEvent(events.FortEvent(events.FortEvent.CLOSE_TRANSPORT_CONFIRM_WINDOW, ctx=None), scope=FortifiedWindowScopes.FORT_MAIN_SCOPE)
        return

    def onLeaveBuildDirectionClick(self):
        self.__refreshCurrentMode()

    def onIntelligenceClick(self):
        isDefenceHourEnabled = self.fortCtrl.getFort().isDefenceHourEnabled()
        if not self.app.varsManager.isFortificationBattleAvailable():
            isDefenceHourEnabled = False
            alias = FORTIFICATION_ALIASES.FORT_INTELLIGENCE_NOT_AVAILABLE_WINDOW
        elif not isDefenceHourEnabled:
            alias = FORTIFICATION_ALIASES.FORT_INTELLIGENCE_NOT_AVAILABLE_WINDOW
        else:
            alias = FORTIFICATION_ALIASES.FORT_INTELLIGENCE_WINDOW
        self.fireEvent(events.LoadViewEvent(alias, ctx={'isDefenceHourEnabled': isDefenceHourEnabled}), EVENT_BUS_SCOPE.LOBBY)
        self.as_setTutorialArrowVisibilityS(FORTIFICATION_ALIASES.TUTORIAL_ARROW_INTELLIGENCE, False)

    def onSortieClick(self):
        self.__joinToSortie()

    def onClanClick(self):
        self.fireEvent(events.LoadViewEvent(FORTIFICATION_ALIASES.FORT_CLAN_LIST_WINDOW_ALIAS), EVENT_BUS_SCOPE.LOBBY)

    def onStatsClick(self):
        self.fireEvent(events.LoadViewEvent(FORTIFICATION_ALIASES.FORT_CLAN_STATISTICS_WINDOW_ALIAS), EVENT_BUS_SCOPE.LOBBY)

    def onCalendarClick(self):
        self.fireEvent(events.LoadViewEvent(FORTIFICATION_ALIASES.FORT_CALENDAR_WINDOW_ALIAS), EVENT_BUS_SCOPE.LOBBY)

    def onSettingClick(self):
        self.fireEvent(events.LoadViewEvent(FORTIFICATION_ALIASES.FORT_SETTINGS_WINDOW_ALIAS), EVENT_BUS_SCOPE.LOBBY)
        self.as_setTutorialArrowVisibilityS(FORTIFICATION_ALIASES.TUTORIAL_ARROW_DEFENCE, False)

    def onUpdated(self, isFullUpdate):
        self.updateData()

    def onClanMembersListChanged(self):
        self.updateData()

    def onDefenceHourActivated(self, hour, initiatorDBID):
        if initiatorDBID == 0:
            return None
        elif initiatorDBID == BigWorld.player().databaseID:
            self.__setTutorialArrowToIntelligenceVisibility()
            return None
        else:
            self.fireEvent(events.LoadViewEvent(FORTIFICATION_ALIASES.FORT_ROSTER_INTRO_WINDOW_ALIAS, ctx={'type': FortRosterIntroWindow.TYPE_DEFENCE_START}), EVENT_BUS_SCOPE.LOBBY)
            return None

    def onDefenceHourChanged(self, hour):
        self.__updateHeaderMessage()

    def onBuildingChanged(self, buildingTypeID, reason, ctx = None):
        if reason in (BUILDING_UPDATE_REASON.COMPLETED, BUILDING_UPDATE_REASON.ADDED):
            self.__currentModeIsDirty = True
        if reason == BUILDING_UPDATE_REASON.UPGRADED and buildingTypeID == FORT_BUILDING_TYPE.MILITARY_BASE:
            commandCenterLevel = self.fortCtrl.getFort().getBuilding(FORT_BUILDING_TYPE.MILITARY_BASE).level
            if commandCenterLevel == FORT_BATTLE_DIVISIONS.ABSOLUTE.minFortLevel:
                self.fireEvent(events.LoadViewEvent(FORTIFICATION_ALIASES.FORT_ROSTER_INTRO_WINDOW_ALIAS, ctx={'type': FortRosterIntroWindow.TYPE_FORT_UPGRADE}), EVENT_BUS_SCOPE.LOBBY)
            if commandCenterLevel == FORT_BATTLE_DIVISIONS.CHAMPION.minFortLevel:
                self.__setTutorialArrowToDefenseHourSettingsVisibility()

    def onViewReady(self):
        g_eventBus.handleEvent(events.FortEvent(events.FortEvent.VIEW_LOADED), scope=EVENT_BUS_SCOPE.FORT)

    def _getCustomData(self):
        fort = self.fortCtrl.getFort()
        level = fort.level
        levelTxt = fort_formatters.getTextLevel(level)
        defResQuantity = fort.getTotalDefRes()
        defResPrefix = self.app.utilsManager.textManager.getText(TEXT_MANAGER_STYLES.MAIN_TEXT, i18n.makeString(FORTIFICATIONS.FORTMAINVIEW_COMMON_TOTALDEPOTQUANTITYTEXT))
        disabledTransporting = False
        if self.__currentMode in (FORTIFICATION_ALIASES.MODE_TRANSPORTING_FIRST_STEP, FORTIFICATION_ALIASES.MODE_TRANSPORTING_NEXT_STEP, FORTIFICATION_ALIASES.MODE_TRANSPORTING_NOT_AVAILABLE):
            if not self.fortCtrl.getFort().isTransportationAvailable():
                disabledTransporting = True
        return {'clanName': g_clanCache.clanTag,
         'levelTitle': i18n.makeString(FORTIFICATIONS.FORTMAINVIEW_HEADER_LEVELSLBL, buildLevel=levelTxt),
         'defResText': defResPrefix + fort_formatters.getDefRes(defResQuantity, True),
         'disabledTransporting': disabledTransporting,
         'orderSelectorVO': {'isSelected': AccountSettings.getFilter(ORDERS_FILTER)['isSelected'],
                             'icon': RES_ICONS.MAPS_ICONS_LIBRARY_FORTIFICATION_AIM}}

    def __updateHeaderMessage(self):
        message = ''
        isDefHourEnabled = self.fortCtrl.getFort().isDefenceHourEnabled()
        if self._isFortFrozen():
            message = i18n.makeString(FORTIFICATIONS.FORTMAINVIEW_HEADER_FORTFROZEN)
            message = self.app.utilsManager.textManager.getText(TEXT_MANAGER_STYLES.ERROR_TEXT, message)
        elif isDefHourEnabled:
            periodStr = self.fortCtrl.getFort().getDefencePeriodStr()
            message = i18n.makeString(FORTIFICATIONS.FORTMAINVIEW_HEADER_DEFENCEPERIOD, period=periodStr)
            message = self.app.utilsManager.textManager.getText(TEXT_MANAGER_STYLES.STATS_TEXT, message)
        self.as_setHeaderMessageS(message, self._isWrongLocalTime() and isDefHourEnabled)

    def __refreshCurrentMode(self):
        self.__currentModeIsDirty = True
        self.__updateCurrentMode()

    def __handleSwitchToMode(self, event):
        mode = event.ctx.get('mode')
        self.__switchToMode(mode)

    def __switchToMode(self, mode):
        if mode != self.__currentMode:
            storedValue = AccountSettings.getFilter(FORT_MEMBER_TUTORIAL)
            notCommanderHelpShown = storedValue['wasShown']
            if self.fortCtrl.getPermissions().canViewNotCommanderHelp() and not notCommanderHelpShown:
                self.fireEvent(events.LoadViewEvent(FORTIFICATION_ALIASES.FORT_NOT_COMMANDER_FIRST_ENTER_WINDOW_ALIAS), scope=EVENT_BUS_SCOPE.LOBBY)
                AccountSettings.setFilter(FORT_MEMBER_TUTORIAL, {'wasShown': True})
            if self.fortCtrl.getFort().isStartingScriptNotStarted() and not self.__commanderHelpShown:
                self.as_toggleCommanderHelpS(True)
                self.__commanderHelpShown = True
            if mode == FORTIFICATION_ALIASES.MODE_COMMON_TUTORIAL:
                self.fireEvent(events.LoadViewEvent(FORTIFICATION_ALIASES.FORT_CREATION_CONGRATULATIONS_WINDOW_ALIAS), scope=EVENT_BUS_SCOPE.LOBBY)
                self.__makeSystemMessages()
            if mode in (FORTIFICATION_ALIASES.MODE_TRANSPORTING_FIRST_STEP,
             FORTIFICATION_ALIASES.MODE_TRANSPORTING_NEXT_STEP,
             FORTIFICATION_ALIASES.MODE_TRANSPORTING_NOT_AVAILABLE,
             FORTIFICATION_ALIASES.MODE_TRANSPORTING_TUTORIAL,
             FORTIFICATION_ALIASES.MODE_TRANSPORTING_TUTORIAL_FIRST_STEP,
             FORTIFICATION_ALIASES.MODE_TRANSPORTING_TUTORIAL_NEXT_STEP):
                g_fortSoundController.setTransportingMode(True)
            else:
                g_fortSoundController.setTransportingMode(False)
            LOG_DEBUG('%s -> %s' % (self.__currentMode, mode))
            state = FortificationEffects.STATES[self.__currentMode][mode].copy()
            STATE_TEXTS_KEY = 'stateTexts'
            if not self.fortCtrl.getPermissions().canTransport():
                state['transportToggle'] = FortificationEffects.INVISIBLE
            if not self.fortCtrl.getPermissions().canChangeSettings():
                state['settingBtn'] = FortificationEffects.INVISIBLE
            state[STATE_TEXTS_KEY] = FortificationEffects.TEXTS[mode]
            state['mode'] = mode
            self.as_switchModeS(state)
            self.__currentModeIsDirty = False
            self.__currentMode = mode

    @staticmethod
    def __makeSystemMessages():
        startDefResCount = str(fortified_regions.g_cache.startResource)
        startDefResCount = i18n.makeString(MESSENGER.SERVICECHANNELMESSAGES_FORTIFICATIONSTARTUP, defResCount=startDefResCount)
        SystemMessages.g_instance.pushI18nMessage(startDefResCount, type=SystemMessages.SM_TYPE.FortificationStartUp)

    def __updateCurrentMode(self):
        if self.__currentModeIsDirty:
            self.__switchToMode(self.fortState.getUIMode(self.fortProvider, self.__transportingProgress))

    @process
    def __joinToSortie(self):
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is not None:
            yield dispatcher.join(JoinModeCtx(PREBATTLE_TYPE.SORTIE, modeFlags=UNIT_MODE_FLAGS.SHOW_LIST))
        else:
            LOG_ERROR('Prebattle dispatcher is not defined')
        return

    def __setTutorialArrowToDefenseHourSettingsVisibility(self):
        isVisible = self.__isClanConditionsSuccess() and not self.fortCtrl.getFort().isDefenceHourEnabled() and self.fortCtrl.getPermissions().canChangeSettings() and self.__currentMode == FORTIFICATION_ALIASES.MODE_COMMON
        self.as_setTutorialArrowVisibilityS(FORTIFICATION_ALIASES.TUTORIAL_ARROW_DEFENCE, isVisible)

    def __setTutorialArrowToIntelligenceVisibility(self):
        isVisible = self.__isClanConditionsSuccess() and self.fortCtrl.getFort().isDefenceHourEnabled() and self.fortCtrl.getPermissions().canCreateFortBattle() and not self.fortCtrl.getFort().getAttacks() and self.__currentMode == FORTIFICATION_ALIASES.MODE_COMMON
        self.as_setTutorialArrowVisibilityS(FORTIFICATION_ALIASES.TUTORIAL_ARROW_INTELLIGENCE, isVisible)

    def __isClanConditionsSuccess(self):
        currentCountOfClanMembers = len(g_clanCache.clanMembers)
        minClanMembers = fortified_regions.g_cache.defenceConditions.minClanMembers
        isClanMembersEnough = currentCountOfClanMembers >= minClanMembers
        baseLevel = self.fortCtrl.getFort().getBuilding(FORT_BUILDING_TYPE.MILITARY_BASE).level
        minRegionLevel = fortified_regions.g_cache.defenceConditions.minRegionLevel
        isBaseLevelEnough = baseLevel >= minRegionLevel
        return isClanMembersEnough and isBaseLevelEnough
