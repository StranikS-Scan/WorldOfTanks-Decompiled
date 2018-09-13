# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/components/FortMainViewComponent.py
from adisp import process
from constants import PREBATTLE_TYPE
from debug_utils import LOG_DEBUG, LOG_ERROR
import fortified_regions
from gui import SystemMessages
from gui.Scaleform.daapi.view.lobby.fortifications import FortificationEffects
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.prb_control.context.unit_ctx import JoinModeCtx
from gui.prb_control.dispatcher import g_prbLoader
from gui.shared import events
from gui.shared import EVENT_BUS_SCOPE
from gui.Scaleform.daapi.view.meta.FortMainViewMeta import FortMainViewMeta
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.framework import AppRef
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_text
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_formatters
from gui.shared.ClanCache import g_clanCache
from gui.shared.SoundEffectsId import SoundEffectsId
from gui.shared.events import FortEvent
from gui.shared.fortifications.context import DirectionCtx
from helpers import i18n

class FortMainViewComponent(FortMainViewMeta, FortViewHelper, AppRef):

    def __init__(self):
        super(FortMainViewComponent, self).__init__()
        self.__tempToggleHelperFlag = False
        self.__currentMode = FortificationEffects.NONE_STATE
        self.__currentModeIsDirty = True
        self.__commanderHelpShown = False

    @process
    def updateData(self):
        self.__updateCurrentMode()
        data = self.getData()
        data['clanIconId'] = yield g_clanCache.getClanEmblemID()
        if not self.isDisposed():
            self.as_setMainDataS(data)

    def _populate(self):
        super(FortMainViewComponent, self)._populate()
        self.addListener(FortEvent.SWITCH_TO_MODE, self.__handleSwitchToMode, scope=EVENT_BUS_SCOPE.LOBBY)
        self.startFortListening()
        self.updateData()
        Waiting.hide('loadPage')

    def _dispose(self):
        super(FortMainViewComponent, self)._dispose()
        self.stopFortListening()
        self.removeListener(FortEvent.SWITCH_TO_MODE, self.__handleSwitchToMode, scope=EVENT_BUS_SCOPE.LOBBY)

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
            directionName = i18n.makeString('#fortifications:General/directionName%d' % dirId)
            SystemMessages.g_instance.pushI18nMessage(SYSTEM_MESSAGES.FORTIFICATION_DIRECTIONOPENED, direction=directionName, type=SystemMessages.SM_TYPE.Warning)
            if self.app.soundManager is not None:
                self.app.soundManager.playEffectSound(SoundEffectsId.FORT_DIRECTION_CREATE)
            self.__currentModeIsDirty = True
        return

    def onFirstTransportingStep(self):
        pass

    def onNextTransportingStep(self):
        if self.app.soundManager is not None:
            self.app.soundManager.playEffectSound(SoundEffectsId.TRANSPORT_FIRST_STEP)
        self.fireEvent(events.FortEvent(events.FortEvent.TRANSPORTATION_STEP, {'step': events.FortEvent.TRANSPORTATION_STEPS.FIRST_STEP}), scope=EVENT_BUS_SCOPE.FORT)
        return

    def onEnterTransportingClick(self):
        if self.app.soundManager is not None:
            self.app.soundManager.playEffectSound(SoundEffectsId.TRANSPORT_ENTER)
        self.__switchToMode(FORTIFICATION_ALIASES.MODE_TRANSPORTING)
        self.fireEvent(events.FortEvent(events.FortEvent.TRANSPORTATION_STEP, {'step': events.FortEvent.TRANSPORTATION_STEPS.INITIAL}), scope=EVENT_BUS_SCOPE.FORT)
        return

    def onLeaveTransportingClick(self):
        if self.app.soundManager is not None:
            self.app.soundManager.playEffectSound(SoundEffectsId.TRANSPORT_EXIT)
        self.__switchToMode(FORTIFICATION_ALIASES.MODE_COMMON)
        return

    def onLeaveBuildDirectionClick(self):
        self.__switchToMode(FORTIFICATION_ALIASES.MODE_COMMON)

    def onIntelligenceClick(self):
        self.fireEvent(events.ShowViewEvent(FORTIFICATION_ALIASES.FORT_INTELLIGENCE_WINDOW_EVENT), EVENT_BUS_SCOPE.LOBBY)

    def onSortieClick(self):
        self.__joinToSortie()

    def onClanClick(self):
        self.fireEvent(events.ShowViewEvent(FORTIFICATION_ALIASES.FORT_CLAN_LIST_WINDOW_EVENT), EVENT_BUS_SCOPE.LOBBY)

    def onStatsClick(self):
        self.fireEvent(events.ShowViewEvent(FORTIFICATION_ALIASES.FORT_CLAN_STATISTICS_WINDOW_EVENT), EVENT_BUS_SCOPE.LOBBY)

    def onUpdated(self):
        self.updateData()

    def onClanMembersListChanged(self):
        self.updateData()

    def onBuildingChanged(self, buildingTypeID, reason, ctx = None):
        if reason in (self.fortCtrl.getFort().BUILDING_UPDATE_REASON.COMPLETED, self.fortCtrl.getFort().BUILDING_UPDATE_REASON.ADDED):
            self.__currentModeIsDirty = True

    def onPlayerAttached(self, buildingTypeID):
        if self.app.soundManager is not None:
            self.app.soundManager.playEffectSound(SoundEffectsId.FORT_FIXED_IN_BUILDING)
        return

    def _getCustomData(self):
        fort = self.fortCtrl.getFort()
        level = fort.level
        levelTxt = fort_formatters.getTextLevel(level)
        defResQuantity = fort.getTotalDefRes()
        defResPrefix = fort_text.getText(fort_text.MAIN_TEXT, i18n.makeString(FORTIFICATIONS.FORTMAINVIEW_COMMON_TOTALDEPOTQUANTITYTEXT))
        disabledTransporting = False
        if self.__currentMode == FORTIFICATION_ALIASES.MODE_TRANSPORTING:
            if not self.fortCtrl.getFort().isTransportationAvailable():
                disabledTransporting = True
        return {'clanName': g_clanCache.clanTag,
         'levelTitle': i18n.makeString(FORTIFICATIONS.FORTMAINVIEW_HEADER_LEVELSLBL, buildLevel=levelTxt),
         'defResText': defResPrefix + fort_formatters.getDefRes(defResQuantity, True),
         'disabledTransporting': disabledTransporting}

    def __handleSwitchToMode(self, event):
        mode = event.ctx.get('mode')
        self.__switchToMode(mode)

    def __switchToMode(self, mode):
        if mode != self.__currentMode:
            if self.fortCtrl.getFort().isStartingScriptNotStarted() and not self.__commanderHelpShown:
                self.as_toggleCommanderHelpS(True)
                self.__commanderHelpShown = True
            if mode == FORTIFICATION_ALIASES.MODE_COMMON_TUTORIAL:
                self.fireEvent(events.ShowViewEvent(FORTIFICATION_ALIASES.FORT_CREATION_CONGRATULATIONS_WINDOW_EVENT), scope=EVENT_BUS_SCOPE.LOBBY)
                self.__makeSystemMessages()
            LOG_DEBUG('%s -> %s' % (self.__currentMode, mode))
            state = FortificationEffects.STATES[self.__currentMode][mode].copy()
            STATE_TEXTS_KEY = 'stateTexts'
            descrsMode = mode
            if not self.fortCtrl.getPermissions().canTransport():
                state['transportToggle'] = FortificationEffects.INVISIBLE
            if descrsMode == FORTIFICATION_ALIASES.MODE_TRANSPORTING:
                if not self.fortCtrl.getFort().isTransportationAvailable():
                    descrsMode = 'transportingDisabled'
            state[STATE_TEXTS_KEY] = FortificationEffects.TEXTS[descrsMode]
            state[STATE_TEXTS_KEY]['headerTitle'] = FORTIFICATIONS.fortmainview(mode + '/title')
            state['mode'] = mode
            self.as_switchModeS(state)
            self.__currentModeIsDirty = False
            self.__currentMode = mode

    def __makeSystemMessages(self):
        startDefResCount = str(fortified_regions.g_cache.startResource)
        startDefResCount = i18n.makeString(MESSENGER.SERVICECHANNELMESSAGES_FORTIFICATIONSTARTUP, defResCount=startDefResCount)
        SystemMessages.g_instance.pushI18nMessage(startDefResCount, type=SystemMessages.SM_TYPE.FortificationStartUp)

    def __updateCurrentMode(self):
        if self.__currentModeIsDirty:
            self.__switchToMode(self.fortState.getUIMode(self.fortProvider))

    @process
    def __joinToSortie(self):
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is not None:
            yield dispatcher.join(JoinModeCtx(PREBATTLE_TYPE.SORTIE))
        else:
            LOG_ERROR('Prebattle dispatcher is not defined')
        return
