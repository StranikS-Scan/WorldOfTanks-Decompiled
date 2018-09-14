# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/header/battle_selector_items.py
import BigWorld
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.game_control import getFalloutCtrl
from helpers import i18n, time_utils
from account_helpers import isDemonstrator
from constants import PREBATTLE_TYPE, QUEUE_TYPE, ACCOUNT_ATTR
from debug_utils import LOG_WARNING, LOG_ERROR
from gui import GUI_SETTINGS
from gui.Scaleform.locale.MENU import MENU
from gui.LobbyContext import g_lobbyContext
from gui.prb_control.prb_getters import areSpecBattlesHidden
from gui.prb_control.context import PrebattleAction
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.prb_control.settings import SELECTOR_BATTLE_TYPES
from gui.prb_control.formatters.windows import SwitchPeripheryCompanyCtx
from gui.server_events import g_eventsCache
from gui.shared.formatters import text_styles
from gui.shared.formatters import time_formatters
from gui.shared.fortifications import isFortificationEnabled, isSortieEnabled
from gui.shared.utils import SelectorBattleTypesUtils as selectorUtils
_SMALL_ICON_PATH = '../maps/icons/battleTypes/40x40/{0}.png'
_LARGER_ICON_PATH = '../maps/icons/battleTypes/64x64/{0}.png'

class _SelectorItem(object):
    __slots__ = ('_label', '_data', '_order', '_isSelected', '_isNew', '_isDisabled', '_isLocked', '_isVisible', '_selectorType')

    def __init__(self, label, data, order, selectorType = None, isVisible = True):
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
        return False

    def isDemoButtonDisabled(self):
        return True

    def isRandomBattle(self):
        return False

    def isInSquad(self, state):
        return state.isInUnit(PREBATTLE_TYPE.SQUAD)

    def setLocked(self, value):
        self._isLocked = value
        if self._isLocked:
            self._isDisabled = False
            self._isSelected = False

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
        self._isSelected = state.isQueueSelected(QUEUE_TYPE.RANDOMS)


class _CommandItem(_SelectorItem):

    def isRandomBattle(self):
        return True

    def isInSquad(self, state):
        return False

    def _update(self, state):
        self._isSelected = state.isInUnit(PREBATTLE_TYPE.UNIT) or state.isInUnit(PREBATTLE_TYPE.CLUBS)
        self._isDisabled = state.hasLockedState


class _CompanyItem(_SelectorItem):

    def isRandomBattle(self):
        return True

    def isInSquad(self, state):
        return False

    def getFormattedLabel(self):
        battleTypeName = super(_CompanyItem, self).getFormattedLabel()
        availabilityStr = self.__getAvailabilityStr()
        if availabilityStr is None:
            return battleTypeName
        else:
            return '%s\n%s' % (battleTypeName, availabilityStr)

    def select(self):
        battle = g_eventsCache.getCompanyBattles()
        if battle.isRunning():
            if battle.needToChangePeriphery():
                g_eventDispatcher.showSwitchPeripheryWindow(ctx=SwitchPeripheryCompanyCtx())
            else:
                super(_CompanyItem, self).select()

    def _update(self, state):
        self._isSelected = state.isInPrebattle(PREBATTLE_TYPE.COMPANY)
        battle = g_eventsCache.getCompanyBattles()
        self._isDisabled = not (battle.isRunning() and battle.isValid())

    @staticmethod
    def _getDateTimeString(timeValue):
        return '{0:>s} {1:>s}'.format(BigWorld.wg_getShortDateFormat(timeValue), BigWorld.wg_getShortTimeFormat(timeValue))

    def __getAvailabilityStr(self):
        battle = g_eventsCache.getCompanyBattles()
        if not battle.isValid():
            return
        else:
            startTimeLeft = battle.getCreationTimeLeft()
            finishTimeLeft = battle.getDestroyingTimeLeft()
            if startTimeLeft is not None and startTimeLeft > 0:
                if startTimeLeft < time_utils.ONE_DAY:
                    return text_styles.alert(i18n.makeString(MENU.HEADERBUTTONS_BATTLE_AVAILABLESINCESOON, time=text_styles.stats(time_formatters.getTimeDurationStr(startTimeLeft, True))))
                else:
                    return text_styles.stats(i18n.makeString(MENU.HEADERBUTTONS_BATTLE_AVAILABLESINCE, datetime=self._getDateTimeString(battle.startTime)))
            elif finishTimeLeft is not None and finishTimeLeft > 0:
                if finishTimeLeft < time_utils.ONE_DAY:
                    return text_styles.success(i18n.makeString(MENU.HEADERBUTTONS_BATTLE_AVAILABLEUNTILSOON, time=text_styles.stats(time_formatters.getTimeDurationStr(finishTimeLeft, True))))
                else:
                    return text_styles.success(i18n.makeString(MENU.HEADERBUTTONS_BATTLE_AVAILABLEUNTIL, datetime=self._getDateTimeString(battle.finishTime)))
            return


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

    def _update(self, state):
        self._isSelected = state.isInPreQueue(QUEUE_TYPE.TUTORIAL)
        self._isDisabled = state.hasLockedState


class _FalloutItem(_SelectorItem):

    def _update(self, state):
        falloutCtrl = getFalloutCtrl()
        self._isSelected = state.isQueueSelected(QUEUE_TYPE.EVENT_BATTLES)
        self._isDisabled = state.hasLockedState
        self._isVisible = falloutCtrl.isAvailable()

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
        self._isVisible = g_lobbyContext.getServerSettings().isSandboxEnabled()


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
_DEFAULT_PAN = PREBATTLE_ACTION_NAME.RANDOM_QUEUE

def _createItems():
    isInRoaming = g_lobbyContext.getServerSettings().roaming.isInRoaming()
    items = []
    _addRandomBattleType(items)
    _addCommandBattleType(items)
    _addSortieBattleType(items, isInRoaming)
    _addTrainingBattleType(items)
    if GUI_SETTINGS.specPrebatlesVisible:
        _addSpecialBattleType(items)
    _addCompanyBattleType(items)
    settings = g_lobbyContext.getServerSettings()
    if settings.isTutorialEnabled():
        _addTutorialBattleType(items, isInRoaming)
    if g_eventsCache.isEventEnabled():
        _addFalloutBattleType(items)
    if settings.isSandboxEnabled() and not isInRoaming:
        _addSandboxType(items)
    return _BattleSelectorItems(items)


def _addRandomBattleType(items):
    items.append(_RandomQueueItem(MENU.HEADERBUTTONS_BATTLE_TYPES_STANDART, PREBATTLE_ACTION_NAME.RANDOM_QUEUE, 0))


def _addCommandBattleType(items):
    items.append(_CommandItem(MENU.HEADERBUTTONS_BATTLE_TYPES_UNIT, PREBATTLE_ACTION_NAME.UNIT, 2, SELECTOR_BATTLE_TYPES.UNIT))


def _addSortieBattleType(items, isInRoaming):
    items.append((_DisabledSelectorItem if isInRoaming else _FortItem)(MENU.HEADERBUTTONS_BATTLE_TYPES_FORT, PREBATTLE_ACTION_NAME.FORT, 4, SELECTOR_BATTLE_TYPES.SORTIE))


def _addTrainingBattleType(items):
    items.append(_TrainingItem(MENU.HEADERBUTTONS_BATTLE_TYPES_TRAINING, PREBATTLE_ACTION_NAME.TRAINING, 6))


def _addSpecialBattleType(items):
    items.append(_SpecBattleItem(MENU.HEADERBUTTONS_BATTLE_TYPES_SPEC, PREBATTLE_ACTION_NAME.SPEC_BATTLE, 5))


def _addCompanyBattleType(items):
    items.append(_CompanyItem(MENU.HEADERBUTTONS_BATTLE_TYPES_COMPANY, PREBATTLE_ACTION_NAME.COMPANY, 3))


def _addTutorialBattleType(items, isInRoaming):
    items.append((_DisabledSelectorItem if isInRoaming else _BattleTutorialItem)(MENU.HEADERBUTTONS_BATTLE_TYPES_BATTLETUTORIAL, PREBATTLE_ACTION_NAME.BATTLE_TUTORIAL, 7))


def _addFalloutBattleType(items):
    items.append(_FalloutItem(MENU.HEADERBUTTONS_BATTLE_TYPES_FALLOUT, PREBATTLE_ACTION_NAME.FALLOUT, 1))


def _addSandboxType(items):
    items.append(_SandboxItem(MENU.HEADERBUTTONS_BATTLE_TYPES_BATTLETEACHING, PREBATTLE_ACTION_NAME.SANDBOX, 9))


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
