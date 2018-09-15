# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/personal/personal_missions_awards_view.py
from gui import makeHtmlString, SystemMessages
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.view.lobby.missions import missions_helper
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import MainOperationAwardComposer, AddOperationAwardComposer
from gui.Scaleform.daapi.view.meta.PersonalMissionsAwardsViewMeta import PersonalMissionsAwardsViewMeta
from gui.Scaleform.genConsts.PERSONAL_MISSIONS_ALIASES import PERSONAL_MISSIONS_ALIASES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.PERSONAL_MISSIONS import PERSONAL_MISSIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.server_events import events_helpers
from gui.server_events.awards_formatters import AWARDS_SIZES
from gui.server_events.events_dispatcher import showPersonalMissionsChain, showPersonalMissionOperationsPage
from gui.server_events.personal_missions_navigation import PersonalMissionsNavigation
from gui.server_events.pm_constants import SOUNDS, PERSONAL_MISSIONS_SOUND_SPACE
from gui.shared import money, event_dispatcher
from gui.shared.formatters import text_styles, currency
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
from gui.shared.utils import decorators
from shared_utils import findFirst, first
from gui.shared.utils.functions import makeTooltip
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from helpers.i18n import makeString as _ms
_FRAME_NAME = ('stugiv', 't28concept', 't55', 'obj260')
_TOKEN_SLOTS = ((VEHICLE_CLASS_NAME.AT_SPG, RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_BIG_COMPLETIONTOKENS_1_4),
 (VEHICLE_CLASS_NAME.SPG, RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_BIG_COMPLETIONTOKENS_1_5),
 (VEHICLE_CLASS_NAME.MEDIUM_TANK, RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_BIG_COMPLETIONTOKENS_1_3),
 (VEHICLE_CLASS_NAME.LIGHT_TANK, RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_BIG_COMPLETIONTOKENS_1_1),
 (VEHICLE_CLASS_NAME.HEAVY_TANK, RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_BIG_COMPLETIONTOKENS_1_2))
_STATS_ICONS = {'questsCompleted': RES_ICONS.MAPS_ICONS_BOOTCAMP_REWARDS_BCMISSION,
 'completionTokens': RES_ICONS.MAPS_ICONS_PERSONALMISSIONS_GEAR_MED,
 'tankwomanBonus': RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_BIG_TANKWOMAN,
 'credits': RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_BIG_CREDITS}

class PersonalMissionsAwardsView(LobbySubView, PersonalMissionsAwardsViewMeta, PersonalMissionsNavigation):
    _COMMON_SOUND_SPACE = PERSONAL_MISSIONS_SOUND_SPACE

    def __init__(self, *args, **kwargs):
        super(PersonalMissionsAwardsView, self).__init__(*args, **kwargs)
        self.__mainAwardsFormatter = MainOperationAwardComposer()
        self.__addAwardsFormatter = AddOperationAwardComposer()

    def showVehiclePreview(self):
        vehicle = self.__getVehicleAward()
        if vehicle.isInInventory:
            event_dispatcher.selectVehicleInHangar(vehicle.intCD)
        else:
            event_dispatcher.showVehiclePreview(vehicle.intCD, previewAlias=PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_AWARDS_VIEW_ALIAS)

    def refresh(self):
        self.as_setDataS(self.__getAwardsVO())

    def closeView(self):
        showPersonalMissionOperationsPage()

    def changeOperation(self, operationID):
        if operationID == -1:
            return
        if operationID != self.getOperationID():
            self.soundManager.playInstantSound(SOUNDS.OPERATION_NAV_CLICK)
        self.setOperationID(operationID)
        self.refresh()

    def showMissionByVehicleType(self, vehicleType):
        finalQuests = self.getOperation().getFinalQuests().values()
        finalQuest = findFirst(lambda q: vehicleType in q.getVehicleClasses(), finalQuests)
        showPersonalMissionsChain(finalQuest.getOperationID(), finalQuest.getChainID())

    @decorators.process('updating')
    def buyMissionsByVehicleType(self, vehicleType):
        finalQuests = self.getOperation().getFinalQuests().values()
        finalQuest = findFirst(lambda q: vehicleType in q.getVehicleClasses(), finalQuests)
        result = yield events_helpers.getPersonalMissionsPawnProcessor()(finalQuest).request()
        if result and result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)

    def _populate(self):
        super(PersonalMissionsAwardsView, self)._populate()
        self._eventsCache.onSyncCompleted += self.__onQuestsUpdated
        self._eventsCache.onProgressUpdated += self.__onQuestsUpdated
        self.refresh()
        self.as_setHeaderDataS({'operations': missions_helper.getOperations(self.getOperationID())})

    def _dispose(self):
        self._eventsCache.onSyncCompleted -= self.__onQuestsUpdated
        self._eventsCache.onProgressUpdated -= self.__onQuestsUpdated
        self.__mainAwardsFormatter = None
        self.__addAwardsFormatter = None
        super(PersonalMissionsAwardsView, self)._dispose()
        return

    def __getAwardsVO(self):
        vo = {'vehicleAward': self.__getVehicleAwardVO(),
         'additionalAwards': self.__getAdditionalAwards(),
         'mainAwards': self.__getMainAwards(),
         'awardsProgress': self.__getAwardsProgress(),
         'backBtnLabel': PERSONAL_MISSIONS.HEADER_BACKBTN_LABEL,
         'backBtnDescrLabel': PERSONAL_MISSIONS.HEADER_BACKBTN_DESCRLABEL_CAMPAIGN,
         'bottomTabs': [{'label': PERSONAL_MISSIONS.PERSONALMISSIONAWARDVIEW_BOTTOMTABS_AWARDS}, {'label': PERSONAL_MISSIONS.PERSONALMISSIONAWARDVIEW_BOTTOMTABS_STATS}]}
        return vo

    def __onQuestsUpdated(self, *args):
        self.refresh()
        self.as_setHeaderDataS({'operations': missions_helper.getOperations(self.getOperationID())})

    def __getVehicleAward(self):
        return self.getOperation().getVehicleBonus()

    def __getVehicleAwardVO(self):
        slots = []
        finalQuestsMap = {}
        for q in self.getOperation().getFinalQuests().itervalues():
            finalQuestsMap[first(q.getVehicleClasses())] = q

        for vehType, tokenIcon in _TOKEN_SLOTS:
            finalQuest = finalQuestsMap[vehType]
            isCompleted = finalQuest.isCompleted()
            slots.append(self.__getVehiclePartSlot(vehType, tokenIcon, isCompleted, self._eventsCache.personalMissions.mayPawnQuest(finalQuest), finalQuest.getPawnCost()))

        vehicleId = _FRAME_NAME[self.getOperationID() - 1]
        return {'vehicleSlotData': {'vehicleId': vehicleId,
                             'vehicleImg': RES_ICONS.getPersonalMissionVehicleImg(vehicleId),
                             'vehicleSmallImg': RES_ICONS.getPersonalMissionVehicleSmallImg(vehicleId),
                             'pathImg': RES_ICONS.getPersonalMissionVehiclePathsImg(vehicleId),
                             'pathSmallImg': RES_ICONS.getPersonalMissionVehiclePathsSmallImg(vehicleId)},
         'slots': slots}

    def __getVehiclePartSlot(self, vehicleType, iconSource, isCollected, canUnlock, unlockCost):
        slotData = {'vehicleType': vehicleType,
         'iconSource': iconSource,
         'isCollected': isCollected,
         'canUnlock': canUnlock,
         'unlockBtnLabel': makeHtmlString('html_templates:lobby/quests/personalMission', 'unlockBtnLabel', {'value': unlockCost}),
         'tooltipData': {'isSpecial': True,
                         'specialAlias': TOOLTIPS_CONSTANTS.PERSONAL_MISSIONS_TANKMODULE,
                         'specialArgs': [self.getOperationID(), vehicleType]}}
        return slotData

    def __getAdditionalAwards(self):
        return {'title': text_styles.highlightText(PERSONAL_MISSIONS.PERSONALMISSIONAWARDVIEW_BOTTOMTABS_AWARDS_ADDITIONALAWARDS),
         'awards': self.__addAwardsFormatter.getFormattedBonuses(self.getOperation(), AWARDS_SIZES.BIG)}

    def __getMainAwards(self):
        return {'title': text_styles.highlightText(PERSONAL_MISSIONS.AWARDSVIEW_MAINAWARDS_TITLE),
         'awards': self.__mainAwardsFormatter.getFormattedBonuses(self.getOperation(), AWARDS_SIZES.BIG)}

    def __getAwardsProgress(self):
        result = []
        statsData = self._eventsCache.personalMissions.getAwardsStats(self.getOperationID())
        opName = self.getOperation().getShortUserName()
        for bonusName in self._eventsCache.personalMissions.trackedStats:
            result.append(self.__packAwardProgress(bonusName, statsData[bonusName], opName))

        return result

    def __packAwardProgress(self, bonusName, stats, opName):
        acquired, total = stats['acquired'], stats['possible']
        if bonusName not in money.Currency.ALL:
            progressStr = ' / '.join((text_styles.stats(acquired), text_styles.main(total)))
        else:
            progressStr = currency.applyAll(bonusName, acquired)
        if bonusName == 'questsCompleted':
            tooltip = makeTooltip(header=TOOLTIPS.PERSONALMISSIONS_AWARDS_STATS_QUESTSCOMPLETED_HEADER, body=_ms(TOOLTIPS.PERSONALMISSIONS_AWARDS_STATS_QUESTSCOMPLETED_BODY, name=opName, acquired=acquired, excellentAcquired=len(self.getOperation().getFullCompletedQuests()), total=total))
        elif bonusName == 'completionTokens':
            tooltip = makeTooltip(header=TOOLTIPS.PERSONALMISSIONS_AWARDS_STATS_COMPLETIONTOKENS_HEADER, body=_ms(TOOLTIPS.PERSONALMISSIONS_AWARDS_STATS_COMPLETIONTOKENS_BODY, name=opName, acquired=acquired, total=total))
        elif bonusName == 'tankwomanBonus':
            tooltip = makeTooltip(header=TOOLTIPS.PERSONALMISSIONS_AWARDS_STATS_TANKWOMANBONUS_HEADER, body=_ms(TOOLTIPS.PERSONALMISSIONS_AWARDS_STATS_TANKWOMANBONUS_BODY, name=opName, acquired=acquired, total=total))
        else:
            currencyFormatter = currency.getBWFormatter(bonusName)
            tooltip = makeTooltip(header=TOOLTIPS.PERSONALMISSIONS_AWARDS_STATS_CREDITS_HEADER, body=_ms(TOOLTIPS.PERSONALMISSIONS_AWARDS_STATS_CREDITS_BODY, name=opName, acquired=currencyFormatter(acquired), total=currencyFormatter(total)))
        return {'operationId': self.getOperationID(),
         'title': text_styles.highlightText(PERSONAL_MISSIONS.awards_progress_label(bonusName)),
         'progress': progressStr,
         'awardSource': _STATS_ICONS[bonusName],
         'progressBarData': {'value': acquired,
                             'maxValue': total},
         'tooltip': tooltip}
