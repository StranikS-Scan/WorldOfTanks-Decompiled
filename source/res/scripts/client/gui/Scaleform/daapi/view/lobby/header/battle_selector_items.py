# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/header/battle_selector_items.py
from adisp import process
from gui.prb_control.entities.base.ctx import PrbAction
from account_helpers import isDemonstrator
from constants import PREBATTLE_TYPE, QUEUE_TYPE, ACCOUNT_ATTR
from debug_utils import LOG_WARNING, LOG_ERROR
from gui import GUI_SETTINGS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.prb_getters import areSpecBattlesHidden
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.prb_control.settings import SELECTOR_BATTLE_TYPES
from gui.shared.formatters import text_styles
from gui.shared.utils import SelectorBattleTypesUtils as selectorUtils
from helpers import i18n, time_utils, dependency
from skeletons.gui.game_control import IFalloutController, IRankedBattlesController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from gui.clans.clan_helpers import isStrongholdsEnabled
from gui.ranked_battles.ranked_helpers import getRankedBattlesUrl
_SMALL_ICON_PATH = '../maps/icons/battleTypes/40x40/{0}.png'
_LARGER_ICON_PATH = '../maps/icons/battleTypes/64x64/{0}.png'

class _SelectorItem(object):
    __slots__ = ('_label', '_data', '_order', '_isSelected', '_isNew', '_isDisabled', '_isLocked', '_isVisible', '_selectorType')
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, label, data, order, selectorType=None, isVisible=True):
        super(_SelectorItem, self).__init__()
        self._label = label
        self._data = data
        self._order = order
        self._isSelected = False
        self._isNew = False
        self._isLocked = False
        self._isDisabled = True
        self._isVisible = isVisible
        self._selectorType = selectorType

    def __cmp__(self, other):
        return cmp(self.getOrder(), other.getOrder())

    def getLabel(self):
        return self._label

    def getData(self):
        return self._data

    def isSelected(self):
        return self._isSelected

    def isDisabled(self):
        return self._isDisabled

    def isVisible(self):
        return self._isVisible

    def getSmallIcon(self):
        return _SMALL_ICON_PATH.format(self._data)

    def getLargerIcon(self):
        return _LARGER_ICON_PATH.format(self._data)

    def getFightButtonLabel(self, state, playerInfo):
        label = MENU.HEADERBUTTONS_BATTLE
        if not playerInfo.isCreator and state.isReadyActionSupported():
            if playerInfo.isReady:
                label = MENU.HEADERBUTTONS_NOTREADY
            else:
                label = MENU.HEADERBUTTONS_READY
        return label

    def isFightButtonForcedDisabled(self):
        return self._isLocked

    def isDemoButtonDisabled(self):
        return True

    def isRandomBattle(self):
        return False

    def isInSquad(self, state):
        return state.isInUnit(PREBATTLE_TYPE.SQUAD) or state.isInUnit(PREBATTLE_TYPE.FALLOUT) or state.isInUnit(PREBATTLE_TYPE.EVENT)

    def setLocked(self, value):
        self._isLocked = value
        if self._isLocked:
            self._isDisabled = True
            self._isSelected = False
            self._isVisible = False

    def isSelectorBtnEnabled(self):
        return self._isLocked or not self._isDisabled

    def getVO(self):
        return {'label': self.getFormattedLabel(),
         'data': self._data,
         'disabled': self._isDisabled,
         'icon': self.getLargerIcon(),
         'active': self._isSelected,
         'isNew': self._isNew,
         'specialBgIcon': ''}

    def getFormattedLabel(self):
        return text_styles.middleTitle(i18n.makeString(self._label))

    def getOrder(self):
        return self._order

    def update(self, state):
        if self._selectorType is not None:
            self._isNew = not selectorUtils.isKnownBattleType(self._selectorType)
        if not self._isLocked:
            self._update(state)
        return

    def select(self):
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is not None:
            self._doSelect(dispatcher)
        else:
            LOG_ERROR('Prebattle dispatcher is not defined')
        return

    def _update(self, state):
        raise NotImplementedError

    @process
    def _doSelect(self, dispatcher):
        yield dispatcher.doSelectAction(PrbAction(self._data))


class _DisabledSelectorItem(_SelectorItem):

    def update(self, state):
        pass

    def select(self):
        LOG_WARNING('That routine can not be invoked')


class _RandomQueueItem(_SelectorItem):

    def isRandomBattle(self):
        return True

    def isDemoButtonDisabled(self):
        return False

    def setLocked(self, value):
        self._isLocked = value
        if self._isLocked:
            self._isDisabled = True
            self._isSelected = False

    def _update(self, state):
        self._isDisabled = state.hasLockedState
        self._isSelected = state.isQueueSelected(QUEUE_TYPE.RANDOMS)


class _CommandItem(_SelectorItem):

    def isRandomBattle(self):
        return True

    def isInSquad(self, state):
        return False

    def _update(self, state):
        self._isSelected = state.isInUnit(PREBATTLE_TYPE.UNIT) or state.isInUnit(PREBATTLE_TYPE.E_SPORT_COMMON)
        self._isDisabled = state.hasLockedState


class _StrongholdsItem(_SelectorItem):

    def isRandomBattle(self):
        return True

    def isInSquad(self, state):
        return False

    def _update(self, state):
        self._isSelected = state.isInUnit(PREBATTLE_TYPE.EXTERNAL)
        if isStrongholdsEnabled() or self._isSelected:
            self._isDisabled = state.hasLockedState
        else:
            self._isDisabled = True


class _SpecBattleItem(_SelectorItem):

    def _update(self, state):
        if state.isInSpecialPrebattle():
            self._isSelected = True
            self._isDisabled = state.hasLockedState
        else:
            self._isSelected = False
            self._isDisabled = areSpecBattlesHidden()


class _TrainingItem(_SelectorItem):

    def getFightButtonLabel(self, state, playerInfo):
        return MENU.HEADERBUTTONS_BATTLE

    def _update(self, state):
        self._isSelected = state.isInLegacy(PREBATTLE_TYPE.TRAINING)
        self._isDisabled = state.hasLockedState


class _BattleTutorialItem(_SelectorItem):

    def isRandomBattle(self):
        return True

    def _update(self, state):
        self._isSelected = state.isInPreQueue(QUEUE_TYPE.TUTORIAL)
        self._isDisabled = state.hasLockedState


class _FalloutItem(_SelectorItem):
    falloutCtrl = dependency.descriptor(IFalloutController)

    def isRandomBattle(self):
        return True

    def _update(self, state):
        self._isSelected = state.isInFallout()
        self._isDisabled = state.hasLockedState
        self._isVisible = self.falloutCtrl.isAvailable()

    def getVO(self):
        vo = super(_FalloutItem, self).getVO()
        vo['specialBgIcon'] = RES_ICONS.MAPS_ICONS_BUTTONS_FALLOUTSELECTORRENDERERBGEVENT
        return vo


class _SandboxItem(_SelectorItem):

    def isRandomBattle(self):
        return True

    def _update(self, state):
        self._isDisabled = state.hasLockedState
        self._isSelected = state.isQueueSelected(queueType=QUEUE_TYPE.SANDBOX)
        self._isVisible = self.lobbyContext.getServerSettings().isSandboxEnabled()


class _BattleSelectorItems(object):

    def __init__(self, items):
        super(_BattleSelectorItems, self).__init__()
        self.__items = {item._data:item for item in items}
        self.__isDemonstrator = False
        self.__isDemoButtonEnabled = False

    def init(self):
        pass

    def fini(self):
        self.__items.clear()
        self.__isDemonstrator = False
        self.__isDemoButtonEnabled = False

    def update(self, state):
        selected = self.__items[self._getDefaultPAN()]
        for item in self.__items.itervalues():
            item.update(state)
            if item.isSelected():
                selected = item

        if self.__isDemonstrator:
            self.__isDemoButtonEnabled = not selected.isDemoButtonDisabled()
        return selected

    def validateAccountAttrs(self, attrs):
        self.__isDemonstrator = isDemonstrator(attrs)
        locked = not attrs & ACCOUNT_ATTR.RANDOM_BATTLES
        for item in self.__items.itervalues():
            if item.isRandomBattle():
                item.setLocked(locked)

    def select(self, action):
        if action in self.__items:
            self.__items[action].select()
        else:
            LOG_ERROR('Can not invoke action', action)

    def getVOs(self):
        return (map(lambda item: item.getVO(), filter(lambda item: item.isVisible(), sorted(self.__items.itervalues()))), self.__isDemonstrator, self.__isDemoButtonEnabled)

    def getItems(self):
        return self.__items

    def _getDefaultPAN(self):
        return _DEFAULT_PAN

    def isSelected(self, action):
        if action in self.__items:
            return self.__items[action].isSelected()
        LOG_ERROR('Action not found', action)
        return False


class _SquadSelectorItems(_BattleSelectorItems):

    def _getDefaultPAN(self):
        return _DEFAULT_SQUAD_PAN


class _SimpleSquadItem(_SelectorItem):

    def __init__(self, label, data, order, selectorType=None, isVisible=True):
        super(_SimpleSquadItem, self).__init__(label, data, order, selectorType, isVisible)
        self._isDisabled = False
        self._isSelected = False
        self._isVisible = True

    def _update(self, state):
        self._isSelected = state.isInUnit(PREBATTLE_TYPE.SQUAD)
        self._isDisabled = state.hasLockedState and not state.isInUnit(PREBATTLE_TYPE.SQUAD)


class _EventSquadItem(_SelectorItem):

    def __init__(self, label, data, order, selectorType=None, isVisible=True):
        super(_EventSquadItem, self).__init__(label, data, order, selectorType, isVisible)
        self._isDisabled = False
        self._isSelected = False
        self._isVisible = True

    def _update(self, state):
        self._isSelected = state.isInUnit(PREBATTLE_TYPE.EVENT)
        self._isDisabled = state.hasLockedState and not state.isInUnit(PREBATTLE_TYPE.EVENT)

    def getVO(self):
        vo = super(_EventSquadItem, self).getVO()
        vo['specialBgIcon'] = RES_ICONS.MAPS_ICONS_LOBBY_EVENTPOPOVERBTNBG
        return vo


class _RankedItem(_SelectorItem):
    rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, label, data, order, selectorType=None, isVisible=True):
        super(_RankedItem, self).__init__(label, data, order, selectorType, isVisible)
        self.__ladderURL = getRankedBattlesUrl()
        self.__hasPastSeason = False

    def isRandomBattle(self):
        return True

    def getVO(self):
        vo = super(_RankedItem, self).getVO()
        if self.rankedController.isAvailable():
            vo['specialBgIcon'] = RES_ICONS.MAPS_ICONS_BUTTONS_FALLOUTSELECTORRENDERERBGEVENT
        return vo

    def getFormattedLabel(self):
        battleTypeName = super(_RankedItem, self).getFormattedLabel()
        availabilityStr = None
        if self.rankedController.hasSuitableVehicles():
            availabilityStr = self.__getAvailabilityStr()
        return battleTypeName if availabilityStr is None else '%s\n%s' % (battleTypeName, availabilityStr)

    def select(self):
        if not self.rankedController.hasSuitableVehicles():
            g_eventDispatcher.loadRankedUnreachable()
        else:
            if self.rankedController.isAvailable():
                super(_RankedItem, self).select()
            elif self.__hasPastSeason:
                self.rankedController.openWebLeaguePage()
            selectorUtils.setBattleTypeAsKnown(self._selectorType)

    def _update(self, state):
        self._isSelected = state.isInPreQueue(QUEUE_TYPE.RANKED)
        self.__hasPastSeason = self.rankedController.getPreviousSeason() is not None and self.__ladderURL is not None
        self._isDisabled = state.hasLockedState or not self.rankedController.isAvailable() and not self.__hasPastSeason
        self._isVisible = self.rankedController.isEnabled()
        return

    def __getAvailabilityStr(self):
        if self._isVisible and self.rankedController.hasAnySeason():
            if self.rankedController.isFrozen():
                return text_styles.main(i18n.makeString(MENU.HEADERBUTTONS_BATTLE_TYPES_RANKED_AVAILABILITY_FROZEN))
            currentSeason = self.rankedController.getCurrentSeason()
            if currentSeason is not None:
                return text_styles.main(i18n.makeString(MENU.HEADERBUTTONS_BATTLE_TYPES_RANKED_AVAILABILITY_SEASON, season=currentSeason.getUserName() or currentSeason.getNumber(), cycle=currentSeason.getCycleOrdinalNumber()))
            nextSeason = self.rankedController.getNextSeason()
            if nextSeason is not None:
                message = MENU.HEADERBUTTONS_BATTLE_TYPES_RANKED_AVAILABILITY_UNTIL
                time = time_utils.getDateTimeFormat(nextSeason.getStartDate())
                return text_styles.main(i18n.makeString(message, time=time))
            return text_styles.main(i18n.makeString(MENU.HEADERBUTTONS_BATTLE_TYPES_RANKED_AVAILABILITY_ENDED))
        else:
            return


_g_items = None
_g_squadItems = None
_DEFAULT_PAN = PREBATTLE_ACTION_NAME.RANDOM
_DEFAULT_SQUAD_PAN = PREBATTLE_ACTION_NAME.SQUAD

@dependency.replace_none_kwargs(eventsCache=IEventsCache, lobbyContext=ILobbyContext)
def _createItems(eventsCache=None, lobbyContext=None):
    settings = lobbyContext.getServerSettings()
    if lobbyContext is not None:
        isInRoaming = settings.roaming.isInRoaming()
    else:
        isInRoaming = False
    items = []
    _addRandomBattleType(items)
    _addRankedBattleType(items, settings)
    _addCommandBattleType(items)
    _addStrongholdsBattleType(items, isInRoaming)
    _addTrainingBattleType(items)
    if GUI_SETTINGS.specPrebatlesVisible:
        _addSpecialBattleType(items)
    if settings is not None and settings.isTutorialEnabled():
        _addTutorialBattleType(items, isInRoaming)
    if eventsCache is not None and eventsCache.isFalloutEnabled():
        _addFalloutBattleType(items)
    if settings is not None and settings.isSandboxEnabled() and not isInRoaming:
        _addSandboxType(items)
    return _BattleSelectorItems(items)


def _createSquadSelectorItems():
    items = []
    _addSimpleSquadType(items)
    _addEventSquadType(items)
    return _SquadSelectorItems(items)


def _addRandomBattleType(items):
    items.append(_RandomQueueItem(MENU.HEADERBUTTONS_BATTLE_TYPES_STANDART, PREBATTLE_ACTION_NAME.RANDOM, 0))


def _addRankedBattleType(items, settings):
    visible = settings is not None and settings.rankedBattles.isEnabled
    items.append(_RankedItem(MENU.HEADERBUTTONS_BATTLE_TYPES_RANKED, PREBATTLE_ACTION_NAME.RANKED, 1, SELECTOR_BATTLE_TYPES.RANKED, isVisible=visible))
    return


def _addCommandBattleType(items):
    items.append(_CommandItem(MENU.HEADERBUTTONS_BATTLE_TYPES_UNIT, PREBATTLE_ACTION_NAME.E_SPORT, 3, SELECTOR_BATTLE_TYPES.UNIT))


def _addStrongholdsBattleType(items, isInRoaming):
    items.append((_DisabledSelectorItem if isInRoaming else _StrongholdsItem)(MENU.HEADERBUTTONS_BATTLE_TYPES_STRONGHOLDS, PREBATTLE_ACTION_NAME.STRONGHOLDS_BATTLES_LIST, 4, SELECTOR_BATTLE_TYPES.UNIT))


def _addTrainingBattleType(items):
    items.append(_TrainingItem(MENU.HEADERBUTTONS_BATTLE_TYPES_TRAINING, PREBATTLE_ACTION_NAME.TRAININGS_LIST, 7))


def _addSpecialBattleType(items):
    items.append(_SpecBattleItem(MENU.HEADERBUTTONS_BATTLE_TYPES_SPEC, PREBATTLE_ACTION_NAME.SPEC_BATTLES_LIST, 6))


def _addTutorialBattleType(items, isInRoaming):
    items.append((_DisabledSelectorItem if isInRoaming else _BattleTutorialItem)(MENU.HEADERBUTTONS_BATTLE_TYPES_BATTLETUTORIAL, PREBATTLE_ACTION_NAME.BATTLE_TUTORIAL, 8))


def _addFalloutBattleType(items):
    items.append(_FalloutItem(MENU.HEADERBUTTONS_BATTLE_TYPES_FALLOUT, PREBATTLE_ACTION_NAME.FALLOUT, 2))


def _addSandboxType(items):
    items.append(_SandboxItem(MENU.HEADERBUTTONS_BATTLE_TYPES_BATTLETEACHING, PREBATTLE_ACTION_NAME.SANDBOX, 9))


def _addSimpleSquadType(items):
    label = text_styles.middleTitle(MENU.HEADERBUTTONS_BATTLE_TYPES_SIMPLESQUAD)
    items.append(_SimpleSquadItem(label, PREBATTLE_ACTION_NAME.SQUAD, 0))


def _addEventSquadType(items):
    label = text_styles.middleTitle(MENU.HEADERBUTTONS_BATTLE_TYPES_EVENTSQUAD)
    items.append(_EventSquadItem(label, PREBATTLE_ACTION_NAME.EVENT_SQUAD, 1))


def create():
    global _g_squadItems
    global _g_items
    if _g_items is None:
        _g_items = _createItems()
    if _g_squadItems is None:
        _g_squadItems = _createSquadSelectorItems()
    else:
        LOG_WARNING('Item already is created')
    return


def clear():
    global _g_squadItems
    global _g_items
    if _g_items:
        _g_items.fini()
        _g_items = None
    if _g_squadItems:
        _g_squadItems.fini()
        _g_squadItems = None
    return


def getItems():
    assert _g_items, 'Items is empty'
    return _g_items


def getSquadItems():
    assert _g_squadItems, 'Items is empty'
    return _g_squadItems
