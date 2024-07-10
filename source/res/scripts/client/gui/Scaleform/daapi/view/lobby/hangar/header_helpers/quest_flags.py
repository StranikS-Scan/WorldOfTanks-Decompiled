# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/header_helpers/quest_flags.py
import logging
import constants
from gui.impl import backport
from gui.impl.gen import R
from gui.limited_ui.lui_rules_storage import LuiRules
from gui.Scaleform.daapi.view.lobby.hangar.header_helpers.base_flags import IQuestsFlag
from gui.Scaleform.daapi.view.lobby.hangar.header_helpers.flag_helpers import getActiveQuestLabel, headerQuestFormatterVo, wrapQuestGroup, LabelState
from gui.Scaleform.daapi.view.lobby.missions.regular.missions_page import setHideDoneFilter
from gui.Scaleform.genConsts.HANGAR_HEADER_QUESTS import HANGAR_HEADER_QUESTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.server_events.events_constants import RANKED_DAILY_GROUP_ID
from gui.server_events.events_dispatcher import showMissionsElen, showMissionsMarathon, showMissionsCategories, showMissionsMapboxProgression
from gui.shared.formatters import icons
from gui.shared.personality import ServicesLocator
from helpers import dependency
from helpers.i18n import makeString
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.event_boards_controllers import IEventBoardController
from skeletons.gui.game_control import IComp7Controller, IFestivityController, ILimitedUIController, IMapboxController, IMarathonEventsController, IQuestsController, IRankedBattlesController
_logger = logging.getLogger(__name__)

class BaseQuestFlag(IQuestsFlag):
    __slots__ = ()
    _QUEST_TYPE = None

    @classmethod
    def isFlagSuitable(cls, questType):
        return questType == cls._QUEST_TYPE


class BattleQuestsFlag(BaseQuestFlag):
    __slots__ = ()
    _QUEST_TYPE = HANGAR_HEADER_QUESTS.QUEST_TYPE_COMMON
    _festivityController = dependency.descriptor(IFestivityController)
    _limitedUIController = dependency.descriptor(ILimitedUIController)
    _questController = dependency.descriptor(IQuestsController)

    @classmethod
    def formatQuests(cls, vehicle, params):
        if vehicle is None or not cls._limitedUIController.isRuleCompleted(LuiRules.BATTLE_MISSIONS):
            return
        else:
            quests = cls._getQuests(vehicle)
            totalCount = len(quests)
            completedQuests = len([ q for q in quests if q.isCompleted() ])
            festivityFlagData = cls._festivityController.getHangarQuestsFlagData()
            if totalCount > 0:
                commonQuestsIcon = festivityFlagData.icon or RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_QUESTS_AVAILABLE
                label, questType = cls._getLabelAndFlagType(totalCount, completedQuests)
            else:
                commonQuestsIcon = festivityFlagData.iconDisabled or RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_QUESTS_DISABLED
                label, questType = '', cls._QUEST_TYPE
            quests = [headerQuestFormatterVo(totalCount > 0, commonQuestsIcon, label, questType, flag=festivityFlagData.flagBackground, tooltip=TOOLTIPS_CONSTANTS.QUESTS_PREVIEW, isTooltipSpecial=True)]
            return wrapQuestGroup(HANGAR_HEADER_QUESTS.QUEST_GROUP_COMMON, '', quests)

    @classmethod
    def showQuestsInfo(cls, questType, questID):
        setHideDoneFilter()
        showMissionsCategories(missionID=questID)

    @classmethod
    def _getLabelAndFlagType(cls, totalCount, completedQuests):
        if completedQuests != totalCount:
            label = getActiveQuestLabel(totalCount, completedQuests)
        else:
            label = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_QUESTS_ALL_DONE)
        return (label, cls._QUEST_TYPE)

    @classmethod
    def _getQuests(cls, vehicle):
        return cls._questController.getCurrentModeQuestsForVehicle(vehicle)


class Comp7QuestsFlag(BattleQuestsFlag):
    __slots__ = ()
    __comp7Controller = dependency.descriptor(IComp7Controller)

    @classmethod
    def _getQuests(cls, vehicle):
        quests = super(cls, Comp7QuestsFlag)._getQuests(vehicle)
        return [ quest for quest in quests if quest.hasBonusType(constants.ARENA_BONUS_TYPE.COMP7) ]


class MapboxQuestsFlag(BaseQuestFlag):
    __slots__ = ()
    _QUEST_TYPE = HANGAR_HEADER_QUESTS.QUEST_TYPE_MAPBOX
    __mapboxController = dependency.descriptor(IMapboxController)

    @classmethod
    def formatQuests(cls, vehicle, params):
        if vehicle is None:
            return
        else:
            data = cls.__mapboxController.getProgressionData()
            if data is not None and cls.__mapboxController.isActive():
                completed = data.totalBattles
                if completed is None:
                    _logger.error('battles played is None')
                    return
                total = max(data.rewards)
                if completed < total:
                    label = makeString(MENU.hangarHeaderMapboxProgressionLabel(LabelState.ACTIVE), total=completed)
                else:
                    label = icons.makeImageTag(RES_ICONS.MAPS_ICONS_MISSIONS_ICONS_CHECK_GREEN_XS)
                progressionIcon = backport.image(R.images.gui.maps.icons.quests.headerFlagIcons.mapbox())
                flag = backport.image(R.images.gui.maps.icons.library.hangarFlag.flag_green())
            else:
                flag = backport.image(R.images.gui.maps.icons.library.hangarFlag.flag_gray())
                progressionIcon = backport.image(R.images.gui.maps.icons.quests.headerFlagIcons.mapbox_disabled())
                label = ''
            quests = [headerQuestFormatterVo(data is not None, progressionIcon, label, cls._QUEST_TYPE, flag=flag, tooltip=TOOLTIPS_CONSTANTS.MAPBOX_PROGRESSION_PREVIEW, isTooltipSpecial=True)]
            return wrapQuestGroup(HANGAR_HEADER_QUESTS.QUEST_GROUP_PERSONAL, '', quests)

    @classmethod
    def showQuestsInfo(cls, _, __):
        showMissionsMapboxProgression()


class RankedQuestsFlag(BaseQuestFlag):
    __slots__ = ()
    _QUEST_TYPE = HANGAR_HEADER_QUESTS.QUEST_GROUP_RANKED_DAILY
    __rankedController = dependency.descriptor(IRankedBattlesController)

    @classmethod
    def formatQuests(cls, vehicle, params):
        quests = cls.__rankedController.getDailyBattleQuests()
        label = ''
        totalCount = len(quests)
        completedQuests = len([ q for q in quests.itervalues() if q.isCompleted() ])
        commonQuestsIcon = R.images.gui.maps.icons.library.outline.quests_disabled()
        if totalCount > 0:
            commonQuestsIcon = R.images.gui.maps.icons.library.outline.quests_available()
            diff = totalCount - completedQuests
            isLeagues = cls.__rankedController.isAccountMastered()
            isAnyPrimeNow = cls.__rankedController.hasAvailablePrimeTimeServers()
            isAnyPrimeLeftTotal = cls.__rankedController.hasPrimeTimesTotalLeft()
            isAnyPrimeLeftNextDay = cls.__rankedController.hasPrimeTimesNextDayLeft()
            if not isAnyPrimeLeftTotal or not isLeagues:
                label = icons.makeImageTag(backport.image(R.images.gui.maps.icons.library.CancelIcon_1()))
            elif diff > 0:
                if isAnyPrimeNow:
                    label = backport.text(R.strings.menu.hangar_header.battle_quests_label.active(), total=diff)
                else:
                    label = icons.makeImageTag(backport.image(R.images.gui.maps.icons.library.CancelIcon_1()))
            elif not isAnyPrimeLeftNextDay:
                label = icons.makeImageTag(backport.image(R.images.gui.maps.icons.library.ConfirmIcon_1()))
            else:
                label = icons.makeImageTag(backport.image(R.images.gui.maps.icons.library.time_icon()))
        questsVo = [headerQuestFormatterVo(enable=totalCount > 0, icon=backport.image(commonQuestsIcon), label=label, questType=cls._QUEST_TYPE, flag=backport.image(R.images.gui.maps.icons.library.hangarFlag.flag_ranked()), tooltip=TOOLTIPS_CONSTANTS.RANKED_QUESTS_PREVIEW, isTooltipSpecial=True)]
        return wrapQuestGroup(cls._QUEST_TYPE, '', questsVo)

    @classmethod
    def showQuestsInfo(cls, _, __):
        showMissionsCategories(groupID=RANKED_DAILY_GROUP_ID)


class ElenQuestsFlag(BaseQuestFlag):
    __slots__ = ()
    _QUEST_TYPE = HANGAR_HEADER_QUESTS.QUEST_TYPE_EVENT
    __eventsController = dependency.descriptor(IEventBoardController)
    __connectionMgr = dependency.descriptor(IConnectionManager)

    @classmethod
    def formatQuests(cls, vehicle, params):
        if vehicle is None:
            return
        else:
            eventsData = cls.__eventsController.getEventsSettingsData()
            hangarFlagData = cls.__eventsController.getHangarFlagData()
            isElenEnabled = ServicesLocator.lobbyContext.getServerSettings().isElenEnabled()
            dataError = eventsData is None or hangarFlagData is None
            if dataError or not isElenEnabled or not eventsData.hasActiveEvents() or hangarFlagData.isSpecialAccount():
                return
            isRegistered = False
            currentEvent = eventsData.getEventForVehicle(vehicle.intCD)
            if currentEvent is not None and currentEvent.isStarted() and not currentEvent.isFinished():
                eventId = currentEvent.getEventID()
                isRegistered = hangarFlagData.isRegistered(eventId)
                hasAnotherActiveEvents = eventsData.hasAnotherActiveEvents(eventId)
                regIsFinished = currentEvent.isRegistrationFinished()
                notValidEvent = regIsFinished and not isRegistered or hangarFlagData.wasCanceled(eventId)
                if notValidEvent and not hasAnotherActiveEvents:
                    return
                if notValidEvent and hasAnotherActiveEvents:
                    enable = False
                else:
                    enable = True
            else:
                if not eventsData.hasActiveEventsByState(hangarFlagData.getHangarFlags()):
                    return
                eventId = None
                enable = False
            if enable:
                eventQuestsTooltip = TOOLTIPS_CONSTANTS.EVENT_QUESTS_PREVIEW
                eventQuestsTooltipIsSpecial = True
                wrongBattleType, wrongSquadState = cls.__eventsController.isElenQuestsStatusWrong(currentEvent)
                noserver = not currentEvent.isAvailableServer(cls.__connectionMgr.peripheryID)
                hasWarning = wrongBattleType or noserver or wrongSquadState
                registrationWillExpiredSoon = currentEvent.isRegistrationFinishSoon()
                endSoonWarning = currentEvent.isEndSoon() and not hasWarning and isRegistered
                if registrationWillExpiredSoon and not isRegistered or endSoonWarning:
                    eventQuestsLabel = icons.makeImageTag(RES_ICONS.MAPS_ICONS_EVENTBOARDS_FLAGICONS_TIME_ICON)
                elif hasWarning and isRegistered:
                    eventQuestsLabel = icons.makeImageTag(RES_ICONS.MAPS_ICONS_EVENTBOARDS_FLAGICONS_ALERT_ICON)
                else:
                    eventQuestsLabel = icons.makeImageTag(RES_ICONS.MAPS_ICONS_EVENTBOARDS_FLAGICONS_ICON_FLAG)
                if isRegistered:
                    eventQuestsIcon = RES_ICONS.MAPS_ICONS_EVENTBOARDS_FLAGICONS_CUP_ICON
                else:
                    eventQuestsIcon = RES_ICONS.MAPS_ICONS_EVENTBOARDS_FLAGICONS_CROSS
            else:
                if not eventsData.hasActiveEvents():
                    return
                eventQuestsTooltip = TOOLTIPS.HANGAR_ELEN_BOTTOM_NOEVENTS
                eventQuestsTooltipIsSpecial = False
                eventQuestsLabel = '--'
                eventQuestsIcon = RES_ICONS.MAPS_ICONS_EVENTBOARDS_FLAGICONS_CUP_DISABLE_ICON
            quests = [headerQuestFormatterVo(enable, eventQuestsIcon, eventQuestsLabel, cls._QUEST_TYPE, questID=eventId, isReward=True, tooltip=eventQuestsTooltip, isTooltipSpecial=eventQuestsTooltipIsSpecial)]
            return wrapQuestGroup(HANGAR_HEADER_QUESTS.QUEST_GROUP_EVENTS, '', quests)

    @classmethod
    def showQuestsInfo(cls, questType, questID):
        showMissionsElen(questID)


class MarathonQuestsFlag(BaseQuestFlag):
    __slots__ = ()
    _QUEST_TYPE = HANGAR_HEADER_QUESTS.QUEST_TYPE_MARATHON
    __marathonsCtrl = dependency.descriptor(IMarathonEventsController)

    @classmethod
    def isFlagSuitable(cls, questType):
        return cls._QUEST_TYPE in questType

    @classmethod
    def formatQuests(cls, vehicle, params):
        if vehicle is None:
            return
        else:
            marathons = cls.__marathonsCtrl.getMarathons()
            if not marathons:
                return
            result = []
            isGroupped = params.get('isGrouped', True)
            for index, marathonEvent in enumerate(marathons):
                flagVO = marathonEvent.getMarathonFlagState(vehicle)
                if flagVO['visible']:
                    quest = headerQuestFormatterVo(flagVO['enable'], flagVO['flagHeaderIcon'], '', ''.join((cls._QUEST_TYPE, str(index))), flag=flagVO['flagMain'], stateIcon=flagVO['flagStateIcon'], questID=marathonEvent.prefix, tooltip=flagVO['tooltip'], isTooltipSpecial=flagVO['enable'])
                    if not isGroupped:
                        wrappedGroup = wrapQuestGroup(''.join((HANGAR_HEADER_QUESTS.QUEST_GROUP_MARATHON, str(index))), '', [quest])
                    result.append(quest if isGroupped else wrappedGroup)

            return wrapQuestGroup(HANGAR_HEADER_QUESTS.QUEST_GROUP_MARATHON, RES_ICONS.MAPS_ICONS_QUESTS_HEADERFLAGICONS_MARATHONS, result) if result and isGroupped else result

    @classmethod
    def showQuestsInfo(cls, questType, questID):
        marathonPrefix = questID or cls.__marathonsCtrl.getPrimaryMarathon()
        showMissionsMarathon(marathonPrefix)
