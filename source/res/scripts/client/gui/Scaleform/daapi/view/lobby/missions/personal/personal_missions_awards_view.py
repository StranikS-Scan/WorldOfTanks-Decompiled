# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/personal/personal_missions_awards_view.py
from gui import makeHtmlString, SystemMessages
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import MainOperationAwardComposer, AddOperationAwardComposer
from gui.Scaleform.daapi.view.meta.PersonalMissionsAwardsViewMeta import PersonalMissionsAwardsViewMeta
from gui.Scaleform.genConsts.PERSONAL_MISSIONS_ALIASES import PERSONAL_MISSIONS_ALIASES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.PERSONAL_MISSIONS import PERSONAL_MISSIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.server_events.awards_formatters import AWARDS_SIZES
from gui.server_events.events_dispatcher import showPersonalMissionsChain, showPersonalMissionOperationsPage
from gui.server_events.personal_missions_navigation import PersonalMissionsNavigation
from gui.server_events.pm_constants import SOUNDS, PERSONAL_MISSIONS_SOUND_SPACE
from gui.shared import event_dispatcher
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME, getTypeBigIconPath
from gui.shared.gui_items.processors import quests
from gui.shared.utils import decorators
from nations import Alliances, ALLIANCES_TAGS_ORDER
from personal_missions import PM_BRANCH
from shared_utils import findFirst
_FRAME_NAME = ('stugiv', 't28concept', 't55', 'obj260', 'excalibur', 'chimera', 'obj729')
_TOKEN_SLOTS = {PM_BRANCH.REGULAR: ((VEHICLE_CLASS_NAME.AT_SPG, RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_BIG_COMPLETIONTOKENS_1_4),
                     (VEHICLE_CLASS_NAME.SPG, RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_BIG_COMPLETIONTOKENS_1_5),
                     (VEHICLE_CLASS_NAME.MEDIUM_TANK, RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_BIG_COMPLETIONTOKENS_1_3),
                     (VEHICLE_CLASS_NAME.LIGHT_TANK, RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_BIG_COMPLETIONTOKENS_1_1),
                     (VEHICLE_CLASS_NAME.HEAVY_TANK, RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_BIG_COMPLETIONTOKENS_1_2)),
 PM_BRANCH.PERSONAL_MISSION_2: ((Alliances.FRANCE, RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_BIG_COMPLETIONTOKENS_5_4),
                                (Alliances.GERMANY, RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_BIG_COMPLETIONTOKENS_5_2),
                                (Alliances.USSR, RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_BIG_COMPLETIONTOKENS_5_1),
                                (Alliances.USA, RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_BIG_COMPLETIONTOKENS_5_3))}

class PersonalMissionsAwardsView(LobbySubView, PersonalMissionsAwardsViewMeta, PersonalMissionsNavigation):
    _COMMON_SOUND_SPACE = PERSONAL_MISSIONS_SOUND_SPACE

    def __init__(self, ctx):
        super(PersonalMissionsAwardsView, self).__init__(ctx)
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
        showPersonalMissionOperationsPage(self.getBranch(), self.getOperationID())

    def changeOperation(self, operationID):
        if operationID == -1:
            return
        if operationID != self.getOperationID():
            self.soundManager.playInstantSound(SOUNDS.OPERATION_NAV_CLICK)
        self.setOperationID(operationID)
        self.refresh()

    def showMissionByVehicleType(self, operationChain):
        finalQuests = self.getOperation().getFinalQuests().values()
        finalQuest = findFirst(lambda q: q.getQuestClassifier().classificationAttr == operationChain, finalQuests)
        showPersonalMissionsChain(finalQuest.getOperationID(), finalQuest.getChainID())

    @decorators.adisp_process('updating')
    def buyMissionsByVehicleType(self, operationChain):
        finalQuests = self.getOperation().getFinalQuests().values()
        finalQuest = findFirst(lambda q: q.getQuestClassifier().classificationAttr == operationChain, finalQuests)
        result = yield quests.PMPawn(finalQuest).request()
        if result and result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)

    def _populate(self):
        super(PersonalMissionsAwardsView, self)._populate()
        self._eventsCache.onSyncCompleted += self.__onQuestsUpdated
        self._eventsCache.onProgressUpdated += self.__onQuestsUpdated
        self.refresh()
        self.__updateHeader()

    def _dispose(self):
        self._eventsCache.onSyncCompleted -= self.__onQuestsUpdated
        self._eventsCache.onProgressUpdated -= self.__onQuestsUpdated
        self.__mainAwardsFormatter = None
        self.__addAwardsFormatter = None
        super(PersonalMissionsAwardsView, self)._dispose()
        return

    def __getAwardsVO(self):
        if self.getBranch() == PM_BRANCH.REGULAR:
            bgIconSource = RES_ICONS.MAPS_ICONS_PERSONALMISSIONS_AWARDS_VIEW_BG
        else:
            bgIconSource = RES_ICONS.MAPS_ICONS_PERSONALMISSIONS_AWARDS_VIEW_BG_PM2
        vo = {'vehicleAward': self.__getVehicleAwardVO(),
         'additionalAwards': self.__getAdditionalAwards(),
         'mainAwards': self.__getMainAwards(),
         'backBtnLabel': PERSONAL_MISSIONS.HEADER_BACKBTN_LABEL,
         'backBtnDescrLabel': PERSONAL_MISSIONS.HEADER_BACKBTN_DESCRLABEL_OPERATION,
         'bgIconSource': bgIconSource}
        return vo

    def __onQuestsUpdated(self, *args):
        self.refresh()
        self.__updateHeader()

    def __getVehicleAward(self):
        return self.getOperation().getVehicleBonus()

    def __getVehicleAwardVO(self):
        slots = []
        finalQuestsMap = {}
        for q in self.getOperation().getFinalQuests().itervalues():
            finalQuestsMap[q.getMajorTag()] = q

        if not finalQuestsMap:
            return {}
        for tokenID, tokenIcon in _TOKEN_SLOTS[self.getBranch()]:
            finalQuest = finalQuestsMap.get(tokenID)
            isCompleted = finalQuest.isCompleted()
            slots.append(self.__getVehiclePartSlot(tokenID, tokenIcon, isCompleted, self._eventsCache.getPersonalMissions().mayPawnQuest(finalQuest), finalQuest.getPawnCost()))

        vehicleId = _FRAME_NAME[self.getOperationID() - 1]
        return {'vehicleSlotData': {'vehicleId': vehicleId,
                             'vehicleImg': RES_ICONS.getPersonalMissionVehicleImg(vehicleId),
                             'vehicleSmallImg': RES_ICONS.getPersonalMissionVehicleSmallImg(vehicleId),
                             'pathImg': RES_ICONS.getPersonalMissionVehiclePathsImg(vehicleId),
                             'pathSmallImg': RES_ICONS.getPersonalMissionVehiclePathsSmallImg(vehicleId)},
         'slots': slots}

    def __getVehiclePartSlot(self, tokenType, iconSource, isCollected, canUnlock, unlockCost):
        allianceIcon = ''
        if tokenType in ALLIANCES_TAGS_ORDER:
            allianceIcon = RES_ICONS.getAlliance17x19Icon(tokenType)
        slotData = {'tokenType': tokenType,
         'iconSource': iconSource,
         'isCollected': isCollected,
         'canUnlock': canUnlock,
         'allianceIcon': allianceIcon,
         'unlockBtnLabel': makeHtmlString('html_templates:lobby/quests/personalMission', 'unlockBtnLabel', {'branch': self.getBranch(),
                            'value': unlockCost}),
         'tooltipData': {'isSpecial': True,
                         'specialAlias': TOOLTIPS_CONSTANTS.PERSONAL_MISSIONS_TANKMODULE,
                         'specialArgs': [self.getOperationID(), tokenType]}}
        return slotData

    def __getAdditionalAwards(self):
        return {'title': text_styles.highlightText(PERSONAL_MISSIONS.PERSONALMISSIONAWARDVIEW_BOTTOMTABS_AWARDS_ADDITIONALAWARDS),
         'awards': self.__addAwardsFormatter.getFormattedBonuses(self.getOperation(), AWARDS_SIZES.BIG)}

    def __getMainAwards(self):
        return {'title': text_styles.highlightText(PERSONAL_MISSIONS.AWARDSVIEW_MAINAWARDS_TITLE),
         'awards': self.__mainAwardsFormatter.getFormattedBonuses(self.getOperation(), AWARDS_SIZES.BIG)}

    def __updateHeader(self):
        vehicle = self.__getVehicleAward()
        operationVO = {'level': MENU.levels_roman(vehicle.level),
         'title': self.getOperation().getShortUserName(),
         'description': PERSONAL_MISSIONS.AWARDSVIEW_DESCRIPTION,
         'vehIcon': getTypeBigIconPath(vehicle.type, vehicle.isElite)}
        self.as_setHeaderDataS(operationVO)
