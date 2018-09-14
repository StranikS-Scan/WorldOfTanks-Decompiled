# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/header/battle_selector_items.py
import BigWorld
from account_helpers import isDemonstrator
from adisp import process
from constants import PREBATTLE_TYPE, QUEUE_TYPE, ACCOUNT_ATTR, IS_TUTORIAL_ENABLED
from debug_utils import LOG_WARNING, LOG_ERROR
from gui import GUI_SETTINGS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui import game_control
from gui.prb_control import areSpecBattlesHidden
from gui.prb_control.context import PrebattleAction
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, SELECTOR_BATTLE_TYPES, FUNCTIONAL_EXIT
from gui.shared import g_eventsCache, g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.fortifications import isFortificationEnabled, isSortieEnabled
from gui.shared.utils import SelectorBattleTypesUtils as selectorUtils
_SMALL_ICON_PATH = '../maps/icons/battleTypes/40x40/{0}.png'
_LARGER_ICON_PATH = '../maps/icons/battleTypes/64x64/{0}.png'

class _SelectorItem(object):
    __slots__ = ('_label', '_data', '_tooltip', '_order', '_isSelected', '_isNew', '_isDisabled', '_isLocked', '_isVisible', '_selectorType')

    def __init__(self, label, data, tooltip, order, selectorType = None, _isVisible = True):
        super(_SelectorItem, self).__init__()
        self._label = label
        self._data = data
        self._tooltip = tooltip
        self._order = order
        self._isSelected = False
        self._isNew = False
        self._isLocked = False
        self._isDisabled = True
        self._isVisible = _isVisible
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
        return False

    def isDemoButtonDisabled(self):
        return True

    def isRandomBattle(self):
        return False

    def isInSquad(self, state):
        return state.isInPrebattle(PREBATTLE_TYPE.SQUAD)

    def setLocked(self, value):
        self._isLocked = value
        if self._isLocked:
            self._isDisabled = False
            self._isSelected = False

    def getVO(self):
        return {'label': self._label,
         'data': self._data,
         'disabled': self._isDisabled,
         'tooltip': self._tooltip,
         'icon': self.getLargerIcon(),
         'active': self._isSelected,
         'isNew': self._isNew}

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
            dispatcher.doSelectAction(PrebattleAction(self._data))
        else:
            LOG_ERROR('Prebattle dispatcher is not defined')
        return

    def _update(self, state):
        raise NotImplementedError


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

    def _update(self, state):
        self._isDisabled = state.hasLockedState
        self._isSelected = not state.hasModalEntity or state.isInPrebattle(PREBATTLE_TYPE.SQUAD)


class _HistoricalItem(_SelectorItem):

    def isRandomBattle(self):
        return True

    def isInSquad(self, state):
        return False

    def _update(self, state):
        if g_eventsCache.getHistoricalBattles():
            self._isSelected = state.isInPreQueue(QUEUE_TYPE.HISTORICAL)
            self._isDisabled = state.hasLockedState
        else:
            self._isSelected = False
            self._isDisabled = True
        self._isVisible = not self._isDisabled


class _CommandItem(_SelectorItem):

    def isRandomBattle(self):
        return True

    def isInSquad(self, state):
        return False

    def _update(self, state):
        self._isSelected = state.isInUnit(PREBATTLE_TYPE.UNIT)
        self._isDisabled = state.hasLockedState


class _CompanyItem(_SelectorItem):

    def isRandomBattle(self):
        return True

    def isInSquad(self, state):
        return False

    def _update(self, state):
        self._isSelected = state.isInPrebattle(PREBATTLE_TYPE.COMPANY)
        self._isDisabled = state.hasLockedState


class _FortItem(_SelectorItem):

    def isRandomBattle(self):
        return True

    def isInSquad(self, state):
        return False

    def _update(self, state):
        isEnabled = isFortificationEnabled()
        if isEnabled:
            self._isSelected = state.isInUnit(PREBATTLE_TYPE.SORTIE) or state.isInUnit(PREBATTLE_TYPE.FORT_BATTLE)
            self._isDisabled = not isSortieEnabled() or state.hasLockedState
        else:
            self._isSelected = False
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

    def isFightButtonForcedDisabled(self):
        return g_eventDispatcher.isTrainingLoaded()

    def getFightButtonLabel(self, state, playerInfo):
        return MENU.HEADERBUTTONS_BATTLE

    def _update(self, state):
        self._isSelected = state.isInPrebattle(PREBATTLE_TYPE.TRAINING)
        self._isDisabled = state.hasLockedState


class _BattleTutorialItem(_SelectorItem):

    def select(self):
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is not None:
            self._doSelect(dispatcher)
        else:
            LOG_ERROR('Prebattle dispatcher is not defined')
        return

    def _update(self, state):
        self._isDisabled = state.hasLockedState

    @process
    def _doSelect(self, dispatcher):
        result = yield dispatcher.unlock(FUNCTIONAL_EXIT.BATTLE_TUTORIAL, True)
        if result:
            g_eventBus.handleEvent(events.TutorialEvent(events.TutorialEvent.RESTART, ctx={'reloadIfRun': True}), scope=EVENT_BUS_SCOPE.GLOBAL)


class _BattleSelectorItems(object):

    def __init__(self, items):
        super(_BattleSelectorItems, self).__init__()
        self.__items = dict(map(lambda item: (item._data, item), items))
        self.__isDemonstrator = False
        self.__isDemoButtonEnabled = False

    def init(self):
        pass

    def fini(self):
        self.__items.clear()
        self.__isDemonstrator = False
        self.__isDemoButtonEnabled = False

    def update(self, state):
        selected = self.__items[_DEFAULT_PAN]
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


_g_items = None
_PAN = PREBATTLE_ACTION_NAME
_DEFAULT_PAN = PREBATTLE_ACTION_NAME.JOIN_RANDOM_QUEUE

def _createItems():
    isInRoaming = game_control.g_instance.roaming.isInRoaming()
    items = [_RandomQueueItem(MENU.HEADERBUTTONS_BATTLE_TYPES_STANDART, _PAN.JOIN_RANDOM_QUEUE, TOOLTIPS.BATTLETYPES_STANDART, 0),
     (_DisabledSelectorItem if isInRoaming else _HistoricalItem)(MENU.HEADERBUTTONS_BATTLE_TYPES_HISTORICALBATTLES, PREBATTLE_ACTION_NAME.HISTORICAL, TOOLTIPS.BATTLETYPES_HISTORICAL, 1, SELECTOR_BATTLE_TYPES.HISTORICAL, False),
     _CommandItem(MENU.HEADERBUTTONS_BATTLE_TYPES_UNIT, PREBATTLE_ACTION_NAME.UNIT, TOOLTIPS.BATTLETYPES_UNIT, 2, SELECTOR_BATTLE_TYPES.UNIT),
     _CompanyItem(MENU.HEADERBUTTONS_BATTLE_TYPES_COMPANY, PREBATTLE_ACTION_NAME.COMPANY, TOOLTIPS.BATTLETYPES_COMPANY, 3),
     (_DisabledSelectorItem if isInRoaming else _FortItem)(MENU.HEADERBUTTONS_BATTLE_TYPES_FORT, PREBATTLE_ACTION_NAME.FORT, TOOLTIPS.BATTLETYPES_FORTIFICATION, 4, SELECTOR_BATTLE_TYPES.SORTIE),
     _TrainingItem(MENU.HEADERBUTTONS_BATTLE_TYPES_TRAINING, PREBATTLE_ACTION_NAME.TRAINING, TOOLTIPS.BATTLETYPES_TRAINING, 6)]
    if GUI_SETTINGS.specPrebatlesVisible:
        items.append(_SpecBattleItem(MENU.HEADERBUTTONS_BATTLE_TYPES_SPEC, PREBATTLE_ACTION_NAME.SPEC_BATTLE, TOOLTIPS.BATTLETYPES_SPEC, 5))
    isTutorialEnabled = IS_TUTORIAL_ENABLED
    player = BigWorld.player()
    if player is not None:
        serverSettings = getattr(player, 'serverSettings', {})
        if 'isTutorialEnabled' in serverSettings:
            isTutorialEnabled = serverSettings['isTutorialEnabled']
    if isTutorialEnabled:
        items.append((_DisabledSelectorItem if isInRoaming else _BattleTutorialItem)(MENU.HEADERBUTTONS_BATTLE_TYPES_BATTLETUTORIAL, PREBATTLE_ACTION_NAME.BATTLE_TUTORIAL, TOOLTIPS.BATTLETYPES_BATTLETUTORIAL, 7))
    return _BattleSelectorItems(items)


def create():
    global _g_items
    if _g_items is None:
        _g_items = _createItems()
    else:
        LOG_WARNING('Item already is created')
    return


def clear():
    global _g_items
    if _g_items:
        _g_items.fini()
        _g_items = None
    return


def getItems():
    raise _g_items or AssertionError('Items is empty')
    return _g_items
