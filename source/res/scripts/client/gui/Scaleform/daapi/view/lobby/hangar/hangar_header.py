# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/hangar_header.py
import constants
from shared_utils import first
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.view.lobby.server_events import events_helpers
from gui.Scaleform.daapi.view.meta.HangarHeaderMeta import HangarHeaderMeta
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.christmas.christmas_controller import g_christmasCtrl
from gui.server_events.events_dispatcher import showEventsWindow
from gui.shared.formatters import text_styles
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.server_events import IEventsCache

class WIDGET_PQ_STATE(object):
    """ State of the personal quests overall relatively to current vehicle.
    """
    DISABLED = 'disabled'
    UNAVAILABLE = 'unavailable'
    AVAILABLE = 'available'
    IN_PROGRESS = 'inprogress'
    AWARD = 'award'
    UNSUITABLE = (DISABLED, UNAVAILABLE)
    NOT_SELECTED = (DISABLED, UNAVAILABLE, AVAILABLE)


class WIDGET_BQ_STATE(object):
    """ State of the battle quests overall relatively to current vehicle.
    """
    AVAILABLE = 'available'
    DISABLED = 'disabled'


class LABEL_STATE(object):
    """ State of the counter label on the flag.
    """
    ACTIVE = 'active'
    EMPTY = 'empty'
    INACTIVE = 'inactive'


def _getBattleQuestsTooltip(state, **ctx):
    return makeTooltip(TOOLTIPS.battleQuestsTooltipHeader(state), _ms(TOOLTIPS.battleQuestsTooltipBody(state), **ctx))


def _getPersonalQuestsTooltip(state, **ctx):
    return makeTooltip(_ms(TOOLTIPS.personalQuestsTooltipHeader(state), **ctx), _ms(TOOLTIPS.personalQuestsTooltipBody(state), **ctx))


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
        if not tile.isUnlocked():
            continue
        for chainID, chain in tile.getQuests().iteritems():
            if tile.getChainVehicleClass(chainID) != vehicleType:
                continue
            for quest in chain.itervalues():
                if vehicleLvl < quest.getVehMinLevel():
                    continue
                if state == WIDGET_PQ_STATE.DISABLED:
                    state = WIDGET_PQ_STATE.UNAVAILABLE
                if quest.canBeSelected() and state in WIDGET_PQ_STATE.UNSUITABLE:
                    state = WIDGET_PQ_STATE.AVAILABLE
                if quest.isInProgress():
                    return (WIDGET_PQ_STATE.IN_PROGRESS,
                     quest,
                     chain,
                     tile)
                if quest.needToGetReward():
                    return (WIDGET_PQ_STATE.AWARD,
                     quest,
                     chain,
                     tile)

    return (state,
     None,
     None,
     None)


def _findBattleQuestsState(eventsCache, vehicle):
    """ Find state of BQs with relation to current vehicle.
    
    Here we simply iterate over all battle quests looking for the ones
    that can be accomplished on the current vehicle.
    
    :param eventsCache: instance of gui.server_events._EventsCache
    :param vehicle: instance of gui_items.Vehicle
    
    :return: tuple (WIDGET_BQ_STATE, applicable quests)
    """

    def filterFunc(quest):
        return quest.getType() not in constants.EVENT_TYPE.SHARED_QUESTS and not quest.isCompleted() and quest.isAvailableForVehicle(vehicle)[0]

    quests = eventsCache.getQuests(filterFunc)
    quests = sorted(quests.itervalues(), events_helpers.questsSortFunc)
    totalCount = len(quests)
    if totalCount > 0:
        return (WIDGET_BQ_STATE.AVAILABLE, quests)
    else:
        return (WIDGET_BQ_STATE.DISABLED, quests)


class HangarHeader(HangarHeaderMeta):
    """ This class is responsible for displaying current vehicle information
    and battle/personal quests widgets (those two flags on top of hangar).
    """
    _eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        super(HangarHeader, self).__init__()
        self._currentVehicle = None
        self._personalQuestID = None
        self._battleQuestId = None
        return

    def showPersonalQuests(self):
        showEventsWindow(eventID=self._personalQuestID, eventType=constants.EVENT_TYPE.POTAPOV_QUEST, doResetNavInfo=self._personalQuestID is None)
        return

    def showCommonQuests(self):
        showEventsWindow(eventID=self._battleQuestId, eventType=constants.EVENT_TYPE.BATTLE_QUEST)

    def update(self, *args):
        self._personalQuestID = None
        if self._currentVehicle.isPresent():
            vehicle = self._currentVehicle.item
            headerVO = {'tankType': '{}_elite'.format(vehicle.type) if vehicle.isElite else vehicle.type,
             'tankInfo': text_styles.concatStylesToMultiLine(text_styles.promoSubTitle(vehicle.shortUserName), text_styles.stats(MENU.levels_roman(vehicle.level))),
             'isPremIGR': vehicle.isPremiumIGR,
             'isVisible': True}
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

    def _dispose(self):
        self._eventsCache.onSyncCompleted -= self.update
        self._eventsCache.onProgressUpdated -= self.update
        self._currentVehicle = None
        self._personalQuestID = None
        super(HangarHeader, self)._dispose()
        return

    def __getBattleQuestsVO(self, vehicle):
        """
        Get part of VO responsible for battle quests flag.
        """
        bqState, quests = _findBattleQuestsState(self._eventsCache, vehicle)
        questsEnabled = bqState == WIDGET_BQ_STATE.AVAILABLE
        if questsEnabled:
            commonQuestsIcon = RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_QUESTS_AVAILABLE
            bgIconStr = RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_FLAG_BLUE
            if g_christmasCtrl.isEventInProgress():
                commonQuestsIcon = RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_FLAG_CHRISTMAS_ICON
                bgIconStr = RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_FLAG_CHRISTMAS
            labelState = LABEL_STATE.ACTIVE
            self._battleQuestId = first(quests).getID()
        else:
            if g_christmasCtrl.isEventInProgress():
                commonQuestsIcon = RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_FLAG_CHRISTMAS_ICON_DISABLED
            else:
                commonQuestsIcon = RES_ICONS.questsStateIconOutline(bqState)
            bgIconStr = RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_FLAG_GRAY
            labelState = LABEL_STATE.INACTIVE
            self._battleQuestId = None
        ctx = {'total': len(quests)}
        return {'commonQuestsLabel': _ms(MENU.hangarHeaderBattleQuestsLabel(labelState), **ctx),
         'commonQuestsIcon': commonQuestsIcon,
         'commonQuestsTooltip': _getBattleQuestsTooltip(bqState, **ctx),
         'commonQuestsEnable': questsEnabled,
         'commonQuestsBg': bgIconStr}

    def __getPersonalQuestsVO(self, vehicle):
        """ Get part of VO responsible for personal quests flag.
        """
        pqState, quest, chain, tile = _findPersonalQuestsState(self._eventsCache, vehicle)
        questsEnabled = pqState not in WIDGET_PQ_STATE.UNSUITABLE
        if pqState == WIDGET_PQ_STATE.AVAILABLE:
            icon = RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_PLUS
        elif pqState == WIDGET_PQ_STATE.AWARD:
            icon = RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_REWARD
        elif not questsEnabled:
            icon = RES_ICONS.vehicleTypeInactiveOutline(vehicle.type)
        else:
            icon = RES_ICONS.vehicleTypeOutline(vehicle.type)
        if not questsEnabled:
            labelState = LABEL_STATE.INACTIVE
        elif pqState == WIDGET_PQ_STATE.AVAILABLE:
            labelState = LABEL_STATE.EMPTY
        else:
            labelState = LABEL_STATE.ACTIVE
        ctx = {}
        if all((quest, chain, tile)):
            self._personalQuestID = quest.getID()
            chainType = tile.getChainMajorTag(quest.getChainID())
            ctx.update({'questName': quest.getUserName(),
             'description': '{}\n{}\n\n{}\n{}'.format(text_styles.standard(_ms(QUESTS.QUESTTASKDETAILSVIEW_MAINCONDITIONS)), quest.getUserMainCondition(), text_styles.standard(_ms(QUESTS.QUESTTASKDETAILSVIEW_ADDITIONALCONDITIONS)), quest.getUserAddCondition()),
             'current': len(filter(lambda q: q.isCompleted(), chain.itervalues())),
             'total': len(chain),
             'tileName': tile.getUserName(),
             'chainName': _ms(MENU.classesShort(chainType))})
        else:
            self._personalQuestID = None
        if questsEnabled:
            bgIconStr = RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_FLAG_RED
        else:
            bgIconStr = RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_FLAG_GRAY
        return {'personalQuestsLabel': _ms(MENU.hangarHeaderPersonalQuestsLabel(labelState), **ctx),
         'personalQuestsIcon': icon,
         'personalQuestsTooltip': _getPersonalQuestsTooltip(pqState, **ctx),
         'personalQuestsEnable': questsEnabled,
         'personalQuestsBg': bgIconStr}
