# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/personal/personal_missions_page.py
import operator
from collections import namedtuple
from constants import PERSONAL_QUEST_FINAL_PAWN_COST
from debug_utils import LOG_ERROR
from gui import SystemMessages
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.missions import missions_helper
from gui.Scaleform.daapi.view.meta.PersonalMissionsPageMeta import PersonalMissionsPageMeta
from gui.Scaleform.framework import g_entitiesFactories
from gui.Scaleform.genConsts.PERSONAL_MISSIONS_ALIASES import PERSONAL_MISSIONS_ALIASES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.PERSONAL_MISSIONS import PERSONAL_MISSIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.server_events import events_helpers
from gui.server_events.events_dispatcher import showPersonalMissionOperationsPage, showPersonalMissionDetails, hidePersonalMissionDetails
from gui.server_events.personal_missions_navigation import PersonalMissionsNavigation
from gui.server_events.pm_constants import SOUNDS, PERSONAL_MISSIONS_SOUND_SPACE, PM_TUTOR_FIELDS as _PTF
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles, icons
from gui.shared.gui_items import Vehicle
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER, getTypeShortUserName
from gui.shared.utils import decorators
from helpers import dependency
from helpers.i18n import makeString as _ms
from shared_utils import findFirst
from skeletons.account_helpers.settings_core import ISettingsCore
_ChainState = namedtuple('_ChainState', ['hasUnlocked',
 'hasVehicle',
 'isCompleted',
 'isFullCompleted',
 'questInProgress'])

class PersonalMissionsPage(LobbySubView, PersonalMissionsPageMeta, PersonalMissionsNavigation):
    _COMMON_SOUND_SPACE = PERSONAL_MISSIONS_SOUND_SPACE
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, ctx):
        super(PersonalMissionsPage, self).__init__(ctx)
        self.__mapView = None
        self.__eventID = None
        self.__lastTutorState = None
        self.__initialize(ctx)
        return

    def onBarClick(self, vehIdx, operationID):
        if vehIdx == -1 or operationID == -1:
            return
        if vehIdx != self.getChainID():
            self.soundManager.playInstantSound(SOUNDS.CHAIN_NAV_CLICK)
        if operationID != self.getOperationID():
            self.soundManager.playInstantSound(SOUNDS.OPERATION_NAV_CLICK_ANIMATION)
            self.soundManager.playInstantSound(SOUNDS.OPERATION_NAV_CLICK)
        self.__navigateTo(operationID, vehIdx)

    def onSkipTaskClick(self):
        chainState = self.__getChainState(self.getChain())
        if chainState.questInProgress is not None:
            self.__pawnMission(chainState.questInProgress)
        else:
            LOG_ERROR('No quest in progress to pawn: ', chainState)
        return

    def onBackBtnClick(self):
        showPersonalMissionOperationsPage()

    def closeView(self):
        event = g_entitiesFactories.makeLoadEvent(VIEW_ALIAS.LOBBY_HANGAR)
        self.fireEvent(event, scope=EVENT_BUS_SCOPE.LOBBY)

    def onTutorialAcceptBtnClicked(self):
        if self.__lastTutorState == _PTF.FOUR_FAL_SHOWN:
            self.soundManager.playSound(SOUNDS.FOUR_AWARD_LISTS_RECEIVED_CONFIRM)
        elif self.__lastTutorState == _PTF.ONE_FAL_SHOWN:
            self.soundManager.playSound(SOUNDS.ONE_AWARD_LIST_RECEIVED_CONFIRM)
        self.__resetToIncomplete()
        if self.__lastTutorState == _PTF.FOUR_FAL_SHOWN:
            if self.__PMController.getFreeTokensCount() >= PERSONAL_QUEST_FINAL_PAWN_COST:
                showPersonalMissionDetails(self.__getLastQuest().getID())
            else:
                self.as_showAwardsPopoverForTutorS()

    def _populate(self):
        super(PersonalMissionsPage, self)._populate()
        self._eventsCache.onSyncCompleted += self.__onQuestsUpdated
        self._eventsCache.onProgressUpdated += self.__onQuestsUpdated
        self.__tryOpenMissionDetails()
        self.__updateComponents()
        self.soundManager.setRTPC(SOUNDS.RTCP_MISSIONS_ZOOM, SOUNDS.MIN_MISSIONS_ZOOM)
        self.soundManager.setRTPC(SOUNDS.RTCP_DEBRIS_CONTROL, SOUNDS.MIN_MISSIONS_ZOOM)
        self.__checkTutorState()

    def _dispose(self):
        self.soundManager.stopSound(SOUNDS.ONE_AWARD_LIST_RECEIVED)
        self.soundManager.stopSound(SOUNDS.FOUR_AWARD_LISTS_RECEIVED)
        self.soundManager.stopSound(SOUNDS.FOUR_AWARD_LISTS_RECEIVED_CONFIRM)
        self.soundManager.stopSound(SOUNDS.ONE_AWARD_LIST_RECEIVED_CONFIRM)
        self._eventsCache.onSyncCompleted -= self.__onQuestsUpdated
        self._eventsCache.onProgressUpdated -= self.__onQuestsUpdated
        super(PersonalMissionsPage, self)._dispose()

    def _invalidate(self, ctx=None):
        super(PersonalMissionsPage, self)._invalidate(ctx)
        self.__initialize(ctx)
        self.__tryOpenMissionDetails()
        self.__updateComponents()

    def _onRegisterFlashComponent(self, viewPy, alias):
        if alias in PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_MAP_VIEW_ALIAS:
            self.__mapView = viewPy
            self.__updateMapData()

    @property
    def __PMController(self):
        return self._eventsCache.personalMissions

    def __initialize(self, ctx=None):
        ctx = ctx or {}
        eventID = ctx.get('eventID')
        operationID = ctx.get('operationID')
        chainID = ctx.get('chainID')
        self.__eventID = int(eventID) if eventID is not None else eventID
        if eventID:
            quest = self._eventsCache.personalMissions.getQuests().get(self.__eventID)
            if quest:
                self.setOperationID(quest.getOperationID())
                self.setChainID(quest.getChainID())
        elif operationID and chainID:
            self.setOperationID(operationID)
            self.setChainID(chainID)
        return

    def __updateComponents(self):
        self.__updateHeader()
        self.__updateSideBar()
        self.__updateFooter()

    def __updateMapData(self):
        if self.__mapView:
            self.__mapView.refresh()

    def __getProgress(self, quests):
        completed = filter(operator.methodcaller('isCompleted'), quests.itervalues())
        return {'value': len(completed),
         'minValue': 0,
         'maxValue': len(quests),
         'useAnim': False}

    def __updateHeader(self):
        self.as_setHeaderDataS({'operations': missions_helper.getOperations(self.getOperationID()),
         'operationTitle': self.__getOperationTitle(),
         'backBtnLabel': PERSONAL_MISSIONS.HEADER_BACKBTN_LABEL,
         'backBtnDescrLabel': PERSONAL_MISSIONS.HEADER_BACKBTN_DESCRLABEL_CAMPAIGN})

    def __updateFooter(self):
        chainState = self.__getChainState(self.getChain())
        isQuestInProgress = False
        btnVisible = False
        btnEnabled = False
        btnLabel = ''
        descr = ''
        currentOperation = self.getOperation()
        currentVehicleType = currentOperation.getChainVehicleClass(self.getChainID())
        vehicleClass = getTypeShortUserName(currentVehicleType)
        pm = self._eventsCache.personalMissions
        freeSheets = pm.getFreeTokensCount()
        pawnedSheets = pm.getPawnedTokensCount()
        if not chainState.hasUnlocked:
            status = text_styles.concatStylesWithSpace(icons.markerBlocked(), text_styles.error(PERSONAL_MISSIONS.STATUSPANEL_STATUS_LOCKED))
        elif chainState.questInProgress is not None:
            quest = chainState.questInProgress
            isQuestInProgress = True
            status = text_styles.concatStylesWithSpace(icons.inProgress(), text_styles.tutorial(quest.getUserName()))
            if quest.areTokensPawned():
                descr = text_styles.neutral(_ms(PERSONAL_MISSIONS.STATUSPANEL_STATUS_PAWNED, count=quest.getPawnCost(), icon=icons.makeImageTag(RES_ICONS.MAPS_ICONS_PERSONALMISSIONS_SHEET_RECEIVED_SMALL, 16, 16, -3, 8)))
            elif quest.isMainCompleted():
                descr = text_styles.neutral(PERSONAL_MISSIONS.STATUSPANEL_STATUS_IMPROVE)
            elif quest.canBePawned():
                btnVisible = True
                pawnCost = quest.getPawnCost()
                btnLabel = _ms(PERSONAL_MISSIONS.STATUSPANEL_FREESHEETBTN_LABEL, count=pawnCost, icon=icons.makeImageTag(RES_ICONS.MAPS_ICONS_PERSONALMISSIONS_SHEET_RECEIVED_SMALL, 16, 16, -3, 8))
                if pawnCost <= freeSheets:
                    btnEnabled = True
        elif chainState.isFullCompleted:
            status = text_styles.concatStylesWithSpace(icons.checkmark(-2), text_styles.bonusAppliedText(_ms(PERSONAL_MISSIONS.STATUSPANEL_STATUS_ALLEXCELLENTDONE, vehicleClass=vehicleClass)))
        elif chainState.isCompleted:
            status = text_styles.concatStylesWithSpace(icons.checkmark(-2), text_styles.bonusAppliedText(_ms(PERSONAL_MISSIONS.STATUSPANEL_STATUS_ALLDONE, vehicleClass=vehicleClass)))
        elif not chainState.hasVehicle:
            status = text_styles.concatStylesWithSpace(icons.markerBlocked(), text_styles.error(_ms(PERSONAL_MISSIONS.STATUSPANEL_STATUS_NOVEHICLE, vehicleClass=vehicleClass)))
        else:
            status = text_styles.concatStylesWithSpace(icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_ATTENTIONICONFILLED, 16, 16, -2), text_styles.neutral(PERSONAL_MISSIONS.STATUSPANEL_STATUS_SELECTTASK))

        def tankwomanFilter(quest):
            tankman, isMainBonus = quest.getTankmanBonus()
            return tankman and (quest.needToGetAddReward() and not isMainBonus or quest.needToGetMainReward() and isMainBonus)

        tankwomanQuests = []
        for operation in pm.getOperations().itervalues():
            tankwomanQuests.extend(operation.getQuestsByFilter(tankwomanFilter).itervalues())

        counterText = ''
        tankwomanVisible = False
        if tankwomanQuests:
            counterText = text_styles.highlightText('x%s' % len(tankwomanQuests))
            tankwomanVisible = True
        self.as_setStatusDataS({'statusText': status,
         'descrText': descr,
         'btnVisible': btnVisible,
         'btnEnabled': btnEnabled,
         'btnLabel': btnLabel,
         'sheetsBlockData': {'freeSheetsText': text_styles.main(_ms(PERSONAL_MISSIONS.STATUSPANEL_FREESHEETS, count=text_styles.highlightText(freeSheets))),
                             'pawnedSheetsText': text_styles.main(_ms(PERSONAL_MISSIONS.STATUSPANEL_PAWNEDSHEETS, count=text_styles.highlightText(pawnedSheets))),
                             'tooltipData': {'isSpecial': True,
                                             'specialAlias': TOOLTIPS_CONSTANTS.FREE_SHEET_RETURN if freeSheets or pawnedSheets else TOOLTIPS_CONSTANTS.FREE_SHEET,
                                             'specialArgs': []},
                             'popover': PERSONAL_MISSIONS_ALIASES.FREE_SHEET_POPOVER},
         'tankgirlsBlockData': {'counterText': counterText,
                                'visible': tankwomanVisible,
                                'tooltipData': {'isSpecial': True,
                                                'specialAlias': TOOLTIPS_CONSTANTS.PERSONAL_MISSIONS_TANKWOMAN,
                                                'specialArgs': []},
                                'popover': PERSONAL_MISSIONS_ALIASES.TANK_GIRLS_POPOVER},
         'tooltip': None,
         'isQuestInProgress': isQuestInProgress})
        return

    def __updateSideBar(self):
        chains = []
        currChainID = self.getChainID()
        currentOperation = self.getOperation()
        currentVehicleType = currentOperation.getChainVehicleClass(currChainID)
        for vehicleType in VEHICLE_TYPES_ORDER:
            chainID, quests = currentOperation.getChainByVehicleType(vehicleType)
            chainState = self.__getChainState(quests)
            progress = self.__getProgress(quests)
            if chainState.isCompleted:
                currentProgress = text_styles.bonusAppliedText(progress['value'])
            else:
                currentProgress = text_styles.stats(progress['value'])
            if currentVehicleType == vehicleType:
                label = text_styles.tutorial(PERSONAL_MISSIONS.chainNameByVehicleType(currentVehicleType))
            elif chainState.questInProgress is not None:
                label = text_styles.main(chainState.questInProgress.getShortUserName())
            elif chainState.isFullCompleted:
                label = text_styles.bonusAppliedText(PERSONAL_MISSIONS.SIDEBAR_FULLCOMPLETED)
            elif chainState.isCompleted:
                label = text_styles.bonusAppliedText(PERSONAL_MISSIONS.SIDEBAR_COMPLETED)
            else:
                label = text_styles.main(PERSONAL_MISSIONS.SIDEBAR_NOTSELECTED)
            progressText = text_styles.main(' / ').join((currentProgress, text_styles.main(progress['maxValue'])))
            chains.append({'chainID': chainID,
             'progressText': progressText,
             'label': label,
             'tankIcon': Vehicle.getTypeBigIconPath(vehicleType, False),
             'progress': progress})

        self.as_updateBranchesDataS({'chains': chains})
        self.as_setSelectedBranchIndexS(currChainID)
        return

    def __getOperationTitle(self):
        currentOperation = self.getOperation()
        label = text_styles.stats(PERSONAL_MISSIONS.OPERATIONTITLE_LABEL_UNLOCKED)
        state = PERSONAL_MISSIONS_ALIASES.OPERATION_UNLOCKED_STATE
        tooltip = {'tooltip': None,
         'isSpecial': False,
         'specialAlias': None,
         'specialArgs': None}
        if not currentOperation.isUnlocked():
            label = text_styles.stats(PERSONAL_MISSIONS.OPERATIONTITLE_LABEL_LOCKED)
            state = PERSONAL_MISSIONS_ALIASES.OPERATION_LOCKED_STATE
        elif currentOperation.isFullCompleted():
            label = text_styles.bonusAppliedText(PERSONAL_MISSIONS.OPERATIONTITLE_LABEL_EXCELLENTDONE)
            state = PERSONAL_MISSIONS_ALIASES.OPERATION_COMPLETE_FULL_STATE
        elif currentOperation.isAwardAchieved():
            infoIcon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_NOTIF_FILTERS_INFORMATION_16X16, 16, 16, -2)
            state = PERSONAL_MISSIONS_ALIASES.OPERATION_COMPLETE_STATE
            currentCount = currentOperation.getFreeTokensCount()
            totalCount = currentOperation.getFreeTokensTotalCount()
            if currentCount < totalCount:
                icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_PERSONALMISSIONS_FREE_SHEET, 24, 24, -7)
                count = str(currentCount)
                total = str(totalCount)
                label = text_styles.stats(_ms(PERSONAL_MISSIONS.OPERATIONTITLE_LABEL_DONE, icon=icon, count=count, total=total, infoIcon=infoIcon))
                tooltip.update({'isSpecial': True,
                 'specialAlias': TOOLTIPS_CONSTANTS.FREE_SHEET,
                 'specialArgs': []})
            else:
                count = str(len(currentOperation.getFullCompletedQuests()))
                total = str(currentOperation.getQuestsCount())
                label = text_styles.stats(_ms(PERSONAL_MISSIONS.OPERATIONTITLE_LABEL_TOMASTER, count=count, total=total, infoIcon=infoIcon))
                tooltip['tooltip'] = TOOLTIPS.PERSONALMISSIONS_OPERATIONTITLE_COMPLETESTATE
        elif currentOperation.isInProgress():
            infoIcon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_NOTIF_FILTERS_INFORMATION_16X16, 16, 16, -2)
            currentCount, totalCount = currentOperation.getTokensCount()
            count = str(currentCount)
            total = str(totalCount)
            label = text_styles.stats(_ms(PERSONAL_MISSIONS.OPERATIONTITLE_LABEL_INPROGRESS, count=count, total=total, infoIcon=infoIcon))
            state = PERSONAL_MISSIONS_ALIASES.OPERATION_CURRENT_STATE
            tooltip['tooltip'] = TOOLTIPS.PERSONALMISSIONS_OPERATIONTITLE_CURRENTSTATE
        elif not currentOperation.hasRequiredVehicles():
            label = text_styles.stats(PERSONAL_MISSIONS.OPERATIONTITLE_LABEL_NOVEHICLE)
            state = PERSONAL_MISSIONS_ALIASES.OPERATION_NO_VEHICLE_STATE
        return {'title': text_styles.promoSubTitle(_ms(PERSONAL_MISSIONS.OPERATIONTITLE_TITLE, title=_ms('#personal_missions:operations/title%d' % currentOperation.getID()))),
         'label': label,
         'state': state,
         'tooltip': tooltip}

    def __getChainState(self, quests):
        hasUnlocked = False
        hasVehicle = False
        isCompleted = True
        isFullCompleted = True
        questInProgress = None
        for q in quests.itervalues():
            if q.isUnlocked():
                hasUnlocked = True
            if q.hasRequiredVehicles():
                hasVehicle = True
            if not q.isCompleted():
                isCompleted = False
            if not q.isFullCompleted():
                isFullCompleted = False
            if q.isInProgress():
                questInProgress = q

        return _ChainState(hasUnlocked, hasVehicle, isCompleted, isFullCompleted, questInProgress)

    @decorators.process('updating')
    def __pawnMission(self, questInProgress):
        result = yield events_helpers.getPersonalMissionsPawnProcessor()(questInProgress).request()
        if result and result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)

    def __onQuestsUpdated(self, *args):
        self.__checkTutorState()
        self.__updateComponents()
        self.__updateMapData()

    def __tryOpenMissionDetails(self):
        """ Depending on the open context, we may need to open personal missions details.
        """
        if self.__eventID:
            showPersonalMissionDetails(self.__eventID)
        else:
            hidePersonalMissionDetails()

    def __getLastQuest(self):
        activeOperation = self.__PMController.getIncompleteOperation()
        completedQuests = activeOperation.getCompletedFinalQuests()
        return findFirst(lambda q: q.getID() not in completedQuests, activeOperation.getFinalQuests().values())

    def __checkTutorState(self):
        storageData = self.__settingsCore.serverSettings.getUIStorage()
        if not storageData.get(_PTF.FOUR_FAL_SHOWN):
            falCount = self.__PMController.getFreeTokensCount()
            falGained = falCount - (storageData.get(_PTF.INITIAL_FAL_COUNT) or 0)
            activeOperation = self.__PMController.getIncompleteOperation()
            chainsCount = len(activeOperation.getQuests())
            if len(activeOperation.getCompletedFinalQuests()) == chainsCount - 1:
                pawnedFalCount = self.__PMController.getPawnedTokensCount()
                if falCount >= PERSONAL_QUEST_FINAL_PAWN_COST:
                    self.__showTutor(_PTF.FOUR_FAL_SHOWN)
                elif falCount + pawnedFalCount >= PERSONAL_QUEST_FINAL_PAWN_COST:
                    self.__showTutor(_PTF.FOUR_FAL_SHOWN, showPawned=True)
            elif not storageData.get(_PTF.ONE_FAL_SHOWN) and falGained > 0:
                self.__showTutor(_PTF.ONE_FAL_SHOWN)

    def __navigateTo(self, operationID=None, chainID=None):
        if operationID is not None:
            self.setOperationID(operationID)
        if chainID is not None:
            self.setChainID(chainID)
        self.__updateComponents()
        self.__updateMapData()
        return

    def __resetToIncomplete(self):
        self.__navigateTo(self.__PMController.getIncompleteOperation().getID())

    def __showTutor(self, tutorState, showPawned=False):
        self.__resetToIncomplete()
        if tutorState == _PTF.ONE_FAL_SHOWN:
            self.soundManager.playSound(SOUNDS.ONE_AWARD_LIST_RECEIVED)
            self.as_showFirstAwardSheetObtainedPopupS(True)
        else:
            self.soundManager.playSound(SOUNDS.FOUR_AWARD_LISTS_RECEIVED)
            self.as_showFourAwardSheetsObtainedPopupS(True, self.__packTutorData(showPawned))
        self.__lastTutorState = tutorState
        self.__settingsCore.serverSettings.saveInUIStorage({self.__lastTutorState: True})

    def __packTutorData(self, hasPawned):
        questName = self.__getLastQuest().getShortUserName()
        if hasPawned:
            description = _ms(PERSONAL_MISSIONS.FOURFREESHEETSOBTAINEDPOPUP_DESCR2, pawnedCount=self.__PMController.getPawnedTokensCount(), questName=questName)
        else:
            description = _ms(PERSONAL_MISSIONS.FOURFREESHEETSOBTAINEDPOPUP_DESCR1, questName=questName)
        return {'icon0': {'icon': RES_ICONS.MAPS_ICONS_PERSONALMISSIONS_FREE_SHEET_BIG,
                   'label': 'x' + str(PERSONAL_QUEST_FINAL_PAWN_COST)},
         'icon1': {'icon': RES_ICONS.MAPS_ICONS_PERSONALMISSIONS_ORDER_BLANK,
                   'label': questName},
         'icon2': {'icon': RES_ICONS.MAPS_ICONS_PERSONALMISSIONS_GEAR_BIG,
                   'label': 'x1'},
         'description': description,
         'header': PERSONAL_MISSIONS.FOURFREESHEETSOBTAINEDPOPUP_HEADER}
