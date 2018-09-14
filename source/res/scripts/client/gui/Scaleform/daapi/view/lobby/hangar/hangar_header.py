# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/hangar_header.py
import constants
from CurrentVehicle import g_currentVehicle
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.server_events import old_events_helpers
from gui.Scaleform.daapi.view.meta.HangarHeaderMeta import HangarHeaderMeta
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.server_events import events_helpers
from gui.server_events.events_dispatcher import showEventsWindow, showMissionsForCurrentVehicle
from gui.shared.formatters import text_styles, icons
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from helpers.i18n import makeString as _ms
from shared_utils import first
from skeletons.gui.shared import IItemsCache
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.game_control import IQuestsController
from gui.Scaleform.daapi.view.lobby.missions import missions_page

class WIDGET_PQ_STATE(object):
    """ State of the personal quests overall relatively to current vehicle.
    """
    DISABLED = 0
    UNAVAILABLE = 1
    COMPLETED = 2
    DONE = 4
    AVAILABLE = 8
    IN_PROGRESS = 16
    AWARD = 32


class LABEL_STATE(object):
    """ State of the counter label on the flag.
    """
    ACTIVE = 'active'
    EMPTY = 'empty'
    INACTIVE = 'inactive'
    ALL_DONE = 'all_done'


def _findPersonalQuestsState(eventsCache, vehicle):
    """ Find state of PQs with relation to current vehicle.
    
    Here we iterate over all personal quests looking for the most
    suitable state.
    
    In three states (DISABLED, UNAVAILABLE, AVAILABLE) we continue to
    search for a better option, once we encounter quest in state of
    progress or in state of having an available award, we stop immediately.
    
    :param eventsCache: instance of gui.server_events._EventsCache
    :param vehicle: instance of gui_items.Vehicle
    
    :return: tuple (WIDGET_PQ_STATE, quest, quest's chain, quest's tile)
    """
    state = WIDGET_PQ_STATE.DISABLED
    vehicleLvl = vehicle.level
    vehicleType = vehicle.type
    for tile in eventsCache.potapov.getTiles().itervalues():
        for chainID, chain in tile.getQuests().iteritems():
            if tile.getChainVehicleClass(chainID) != vehicleType:
                continue
            for quest in chain.itervalues():
                if vehicleLvl < quest.getVehMinLevel():
                    continue
                if quest.isFullCompleted(isRewardReceived=True):
                    state |= WIDGET_PQ_STATE.DONE
                    continue
                if quest.isMainCompleted(isRewardReceived=True):
                    state |= WIDGET_PQ_STATE.COMPLETED
                    if not quest.isInProgress():
                        continue
                state |= WIDGET_PQ_STATE.UNAVAILABLE
                if quest.canBeSelected():
                    state |= WIDGET_PQ_STATE.AVAILABLE
                if quest.isInProgress():
                    return (state | WIDGET_PQ_STATE.IN_PROGRESS,
                     quest,
                     chain,
                     tile)
                if quest.needToGetReward():
                    return (state | WIDGET_PQ_STATE.AWARD,
                     quest,
                     chain,
                     tile)

    return (state,
     None,
     None,
     None)


class HangarHeader(HangarHeaderMeta):
    """ This class is responsible for displaying current vehicle information
    and battle/personal quests widgets (those two flags on top of hangar).
    """
    _itemsCache = dependency.descriptor(IItemsCache)
    _eventsCache = dependency.descriptor(IEventsCache)
    _questController = dependency.descriptor(IQuestsController)

    def __init__(self):
        super(HangarHeader, self).__init__()
        self._currentVehicle = None
        self._personalQuestID = None
        return

    def showPersonalQuests(self):
        showEventsWindow(eventID=self._personalQuestID, eventType=constants.EVENT_TYPE.POTAPOV_QUEST, doResetNavInfo=self._personalQuestID is None)
        return

    def showCommonQuests(self):
        missions_page.setHideDoneFilter()
        showMissionsForCurrentVehicle()

    def showBeginnerQuests(self):
        showEventsWindow(eventID=self._battleQuestId, eventType=constants.EVENT_TYPE.TUTORIAL)

    def update(self, *args):
        self._personalQuestID = None
        if self._currentVehicle.isPresent():
            vehicle = self._currentVehicle.item
            if self._questController.isNewbiePlayer():
                tutorialChapters = self._getTutorialChapters()
            else:
                tutorialChapters = None
            headerVO = {'tankType': '{}_elite'.format(vehicle.type) if vehicle.isElite else vehicle.type,
             'tankInfo': text_styles.concatStylesToMultiLine(text_styles.promoSubTitle(vehicle.shortUserName), text_styles.stats(MENU.levels_roman(vehicle.level))),
             'isPremIGR': vehicle.isPremiumIGR,
             'isVisible': True,
             'isBeginner': bool(tutorialChapters)}
            if tutorialChapters:
                headerVO.update(self.__getBeginnerQuestsVO(tutorialChapters))
            else:
                headerVO.update(self.__getBattleQuestsVO(vehicle))
                headerVO.update(self.__getPersonalQuestsVO(vehicle))
        else:
            headerVO = {'isVisible': False}
        self.as_setDataS(headerVO)
        return

    def _populate(self):
        super(HangarHeader, self)._populate()
        self._currentVehicle = g_currentVehicle
        self._eventsCache.onSyncCompleted += self.update
        self._eventsCache.onProgressUpdated += self.update
        g_clientUpdateManager.addCallbacks({'inventory.1': self.update,
         'stats.tutorialsCompleted': self.update})

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self._eventsCache.onSyncCompleted -= self.update
        self._eventsCache.onProgressUpdated -= self.update
        self._currentVehicle = None
        self._personalQuestID = None
        super(HangarHeader, self)._dispose()
        return

    def _getTutorialChapters(self):
        completed = self._itemsCache.items.stats.tutorialsCompleted
        questsDescriptor = old_events_helpers.getTutorialEventsDescriptor()
        chapters = []
        if questsDescriptor is not None:
            for chapter in questsDescriptor:
                chapterStatus = chapter.getChapterStatus(questsDescriptor, completed)
                if chapterStatus != events_helpers.EVENT_STATUS.NOT_AVAILABLE and chapterStatus != events_helpers.EVENT_STATUS.COMPLETED:
                    chapters.append(chapter)

        return chapters

    def __getBeginnerQuestsVO(self, chapters):
        chapter = first(chapters)
        self._battleQuestId = chapter.getID()
        return {'beginnerQuestsLabel': str(len(chapters)),
         'beginnerQuestsIcon': RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_BEGINNER,
         'beginnerQuestsTooltip': makeTooltip(chapter.getTitle(), chapter.getDescription()),
         'beginnerQuestsEnable': True}

    def __getBattleQuestsVO(self, vehicle):
        """ Get part of VO responsible for battle quests flag.
        """
        quests = self._questController.getQuestForVehicle(vehicle)
        totalCount = len(quests)
        completedQuests = len([ q for q in quests if q.isCompleted() ])
        if totalCount > 0:
            if completedQuests != totalCount:
                label = _ms(MENU.hangarHeaderBattleQuestsLabel(LABEL_STATE.ACTIVE), total=totalCount - completedQuests)
            else:
                label = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_QUESTS_ALL_DONE)
            commonQuestsIcon = RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_QUESTS_AVAILABLE
        else:
            commonQuestsIcon = RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_QUESTS_DISABLED
            label = ''
        return {'commonQuestsLabel': label,
         'commonQuestsIcon': commonQuestsIcon,
         'commonQuestsTooltip': TOOLTIPS_CONSTANTS.QUESTS_PREVIEW,
         'commonQuestsEnable': totalCount > 0}

    def __getPersonalQuestsVO(self, vehicle):
        """ Get part of VO responsible for personal quests flag.
        """
        pqState, quest, chain, tile = _findPersonalQuestsState(self._eventsCache, vehicle)
        enable = True
        if pqState & WIDGET_PQ_STATE.AWARD:
            icon = RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_REWARD
            labelState = LABEL_STATE.ACTIVE
            tooltip = makeTooltip(_ms(TOOLTIPS.HANGAR_HEADER_PERSONALQUESTS_AWARD_HEADER, tileName=tile.getUserName()), _ms(TOOLTIPS.HANGAR_HEADER_PERSONALQUESTS_AWARD_BODY, chainName=_ms(MENU.classesShort(tile.getChainMajorTag(quest.getChainID())))))
        elif pqState & WIDGET_PQ_STATE.IN_PROGRESS:
            icon = RES_ICONS.vehicleTypeOutline(vehicle.type)
            labelState = LABEL_STATE.ACTIVE
            tooltip = TOOLTIPS_CONSTANTS.PERSONAL_QUESTS_PREVIEW
        elif pqState & WIDGET_PQ_STATE.AVAILABLE:
            icon = RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_PLUS
            labelState = LABEL_STATE.EMPTY
            tooltip = TOOLTIPS.HANGAR_HEADER_PERSONALQUESTS_AVAILABLE
        elif pqState & WIDGET_PQ_STATE.COMPLETED:
            icon = RES_ICONS.vehicleTypeOutline(vehicle.type)
            labelState = LABEL_STATE.ALL_DONE
            if pqState & WIDGET_PQ_STATE.UNAVAILABLE:
                tooltip = TOOLTIPS.HANGAR_HEADER_PERSONALQUESTS_UNAVAILABLE
            else:
                tooltip = TOOLTIPS.HANGAR_HEADER_PERSONALQUESTS_COMPLETED
        elif pqState & WIDGET_PQ_STATE.DONE:
            icon = RES_ICONS.vehicleTypeInactiveOutline(vehicle.type)
            labelState = LABEL_STATE.INACTIVE
            tooltip = TOOLTIPS.HANGAR_HEADER_PERSONALQUESTS_DONE
            enable = False
        else:
            icon = RES_ICONS.vehicleTypeInactiveOutline(vehicle.type)
            labelState = LABEL_STATE.INACTIVE
            tooltip = TOOLTIPS.HANGAR_HEADER_PERSONALQUESTS_DISABLED
            enable = False
        if all((quest, chain, tile)):
            self._personalQuestID = quest.getID()
            ctx = {'current': len(filter(lambda q: q.isCompleted(), chain.itervalues())),
             'total': len(chain)}
        else:
            self._personalQuestID = None
            ctx = {'icon': icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_QUESTS_ALL_DONE)}
        res = {'personalQuestsLabel': _ms(MENU.hangarHeaderPersonalQuestsLabel(labelState), **ctx),
         'personalQuestsIcon': icon,
         'personalQuestsEnable': enable,
         'isPersonalReward': bool(pqState & WIDGET_PQ_STATE.AWARD),
         'personalQuestsTooltip': tooltip,
         'personalQuestsTooltipIsSpecial': bool(pqState & WIDGET_PQ_STATE.IN_PROGRESS)}
        return res
