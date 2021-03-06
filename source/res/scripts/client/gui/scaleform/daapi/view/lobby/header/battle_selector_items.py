# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/header/battle_selector_items.py
import logging
from uilogging.deprecated.decorators import loggerTarget, loggerEntry
from uilogging.deprecated.mode_selector.constants import MS_LOG_KEYS
from uilogging.deprecated.mode_selector.decorators import logChangeMode
from uilogging.deprecated.mode_selector.loggers import ModeSelectorUILogger
from adisp import process
from gui.prb_control.entities.base.ctx import PrbAction
from account_helpers import isDemonstrator
from constants import PREBATTLE_TYPE, QUEUE_TYPE, ACCOUNT_ATTR
from gui import GUI_SETTINGS
from gui.prb_control.dispatcher import g_prbLoader
from gui.battle_royale.constants import BattleRoyalePerfProblems
from gui.Scaleform.locale.MENU import MENU
from gui.prb_control.prb_getters import areSpecBattlesHidden
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.prb_control.settings import SELECTOR_BATTLE_TYPES
from gui.ranked_battles.constants import PrimeTimeStatus
from gui.shared.formatters import text_styles, icons
from gui.shared.utils import SelectorBattleTypesUtils as selectorUtils
from helpers import time_utils, dependency, int2roman
from gui.shared.utils.functions import makeTooltip
from skeletons.gui.game_control import IRankedBattlesController, IBattleRoyaleController, IBattleRoyaleTournamentController, IWeekendBrawlController
from skeletons.gui.lobby_context import ILobbyContext
from gui.clans.clan_helpers import isStrongholdsEnabled
from gui.Scaleform.genConsts.RANKEDBATTLES_CONSTS import RANKEDBATTLES_CONSTS
from gui.impl import backport
from gui.impl.gen import R
from skeletons.gui.server_events import IEventsCache
from battle_selector_item import SelectorItem
from battle_selector_event_progression_providers import EventProgressionDataProvider
from battle_selector_event_progression_item import EventProgressionItem
from gui.prb_control import prbEntityProperty
_logger = logging.getLogger(__name__)
_R_HEADER_BUTTONS = R.strings.menu.headerButtons
_R_BATTLE_TYPES = R.strings.menu.headerButtons.battle.types
_R_BATTLE_MENU = R.strings.menu.headerButtons.battle.menu
_R_ICONS = R.images.gui.maps.icons
_R_BR_TOURNAMENT_BUTTON = R.strings.battle_royale.tournament.fightButton

class _SelectorItem(object):
    __slots__ = ('_label', '_data', '_order', '_selectorType', '_isVisible', '_isExtra', '_isSelected', '_isNew', '_isDisabled', '_isLocked')
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, label, data, order, selectorType=None, isVisible=True, isExtra=False):
        super(_SelectorItem, self).__init__()
        self._label = label
        self._data = data
        self._order = order
        self._isSelected = False
        self._isNew = False
        self._isLocked = False
        self._isDisabled = True
        self._isVisible = isVisible
        self._isExtra = isExtra
        self._selectorType = selectorType

    def __cmp__(self, other):
        return cmp(self.getOrder(), other.getOrder())

    def getLabel(self):
        return self._label

    def getData(self):
        return self._data

    def isSelected(self):
        return self._isSelected

    def getSelectorType(self):
        return self._selectorType

    def isDisabled(self):
        return self._isDisabled

    def isVisible(self):
        return self._isVisible

    def isExtra(self):
        return self._isExtra

    def getSmallIcon(self):
        return backport.image(_R_ICONS.battleTypes.c_40x40.dyn(self._data)())

    def getLargerIcon(self):
        return backport.image(_R_ICONS.battleTypes.c_64x64.dyn(self._data)())

    def getSpecialBGIcon(self):
        pass

    def getFightButtonLabel(self, state, playerInfo):
        label = _R_HEADER_BUTTONS.battle
        if not playerInfo.isCreator and state.isReadyActionSupported():
            label = _R_HEADER_BUTTONS.notReady if playerInfo.isReady else _R_HEADER_BUTTONS.ready
        return backport.text(label())

    def isLocked(self):
        return self._isLocked

    def isDemoButtonDisabled(self):
        return True

    def isRandomBattle(self):
        return False

    def isInSquad(self, state):
        return state.isInUnit(PREBATTLE_TYPE.SQUAD) or state.isInUnit(PREBATTLE_TYPE.EVENT) or state.isInUnit(PREBATTLE_TYPE.EPIC) or state.isInUnit(PREBATTLE_TYPE.WEEKEND_BRAWL)

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
         'isNew': self.isShowNewIndicator(),
         'specialBgIcon': self.getSpecialBGIcon()}

    def isShowNewIndicator(self):
        return self._isNew

    def getFormattedLabel(self):
        return text_styles.middleTitle(self._label)

    def getOrder(self):
        return self._order

    def update(self, state):
        if self._selectorType is not None:
            self._isNew = not selectorUtils.isKnownBattleType(self._selectorType)
        if not self.isLocked():
            self._update(state)
        return

    def select(self):
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is not None:
            self._doSelect(dispatcher)
        else:
            _logger.error('Prebattle dispatcher is not defined')
        return

    def _update(self, state):
        raise NotImplementedError

    @process
    def _doSelect(self, dispatcher):
        yield dispatcher.doSelectAction(PrbAction(self.getData()))


class _SelectorExtraItem(_SelectorItem):

    def __init__(self, label, data, order, selectorType=None, isVisible=True):
        super(_SelectorExtraItem, self).__init__(label, data, order, selectorType, isVisible, isExtra=True)

    def getVO(self):
        vo = super(_SelectorExtraItem, self).getVO()
        vo.update({'mainLabel': self.getMainLabel(),
         'infoLabel': self.getInfoLabel()})
        return vo

    def getMainLabel(self):
        raise NotImplementedError

    def getInfoLabel(self):
        raise NotImplementedError

    def _update(self, state):
        raise NotImplementedError


class _DisabledSelectorItem(_SelectorItem):

    def update(self, state):
        pass

    def _update(self, state):
        pass

    def select(self):
        _logger.warning('That routine can not be invoked')


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
        isCommandBattleEnabled = self.lobbyContext.getServerSettings().isCommandBattleEnabled()
        self._isSelected = state.isInUnit(PREBATTLE_TYPE.UNIT) or state.isInUnit(PREBATTLE_TYPE.E_SPORT_COMMON)
        self._isDisabled = state.hasLockedState or not isCommandBattleEnabled
        self._isVisible = isCommandBattleEnabled


class _StrongholdsItem(_SelectorItem):

    def isRandomBattle(self):
        return True

    def isInSquad(self, state):
        return False

    def _update(self, state):
        self._isSelected = state.isInUnit(PREBATTLE_TYPE.STRONGHOLD)
        if isStrongholdsEnabled() or self._isSelected:
            self._isDisabled = state.hasLockedState
        else:
            self._isDisabled = True


class _SpecBattleItem(_SelectorItem):
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    __battleRoyaleTournamentController = dependency.descriptor(IBattleRoyaleTournamentController)

    @prbEntityProperty
    def prbEntity(self):
        return None

    def getFightButtonLabel(self, state, playerInfo):
        if self.__battleRoyaleTournamentController.isSelected():
            label = _R_BR_TOURNAMENT_BUTTON.ready
            if self.prbEntity.isInQueue():
                label = _R_BR_TOURNAMENT_BUTTON.notReady
            return backport.text(label())
        return super(_SpecBattleItem, self).getFightButtonLabel(state, playerInfo)

    def _update(self, state):
        if state.isInSpecialPrebattle():
            self._isSelected = True
            self._isDisabled = state.hasLockedState
        elif self.__battleRoyaleTournamentController.isSelected():
            self._isDisabled = False
            self._isSelected = True
        else:
            self._isSelected = False
            self._isDisabled = areSpecBattlesHidden()


class _TrainingItem(_SelectorItem):

    def getFightButtonLabel(self, state, playerInfo):
        return backport.text(_R_HEADER_BUTTONS.battle())

    def _update(self, state):
        self._isSelected = state.isInLegacy(PREBATTLE_TYPE.TRAINING)
        self._isDisabled = state.hasLockedState


class _EpicTrainingItem(_SelectorItem):

    def getFightButtonLabel(self, state, playerInfo):
        return backport.text(_R_HEADER_BUTTONS.battle())

    def _update(self, state):
        settings = self.lobbyContext.getServerSettings()
        self._isSelected = state.isInLegacy(PREBATTLE_TYPE.EPIC_TRAINING)
        self._isDisabled = state.hasLockedState
        self._isVisible = settings is not None and settings.frontline.isEpicTrainingEnabled
        return

    def getFormattedLabel(self):
        title = super(_EpicTrainingItem, self).getFormattedLabel()
        descr = text_styles.main(backport.text(R.strings.menu.headerButtons.battle.types.epicTraining.descr()))
        return '{}\n{}'.format(title, descr)

    def select(self):
        super(_EpicTrainingItem, self).select()
        selectorUtils.setBattleTypeAsKnown(self._selectorType)


class _BattleTutorialItem(_SelectorItem):

    def isRandomBattle(self):
        return True

    def _update(self, state):
        self._isSelected = state.isInPreQueue(QUEUE_TYPE.TUTORIAL)
        self._isDisabled = state.hasLockedState


class _SandboxItem(_SelectorItem):

    def isRandomBattle(self):
        return True

    def _update(self, state):
        self._isDisabled = state.hasLockedState
        self._isSelected = state.isQueueSelected(queueType=QUEUE_TYPE.SANDBOX)
        self._isVisible = self.lobbyContext.getServerSettings().isSandboxEnabled()


class _WeekendBrawlItem(_SelectorItem):
    wBrawlController = dependency.descriptor(IWeekendBrawlController)

    def isRandomBattle(self):
        return True

    def getSpecialBGIcon(self):
        return backport.image(_R_ICONS.buttons.selectorRendererBGEvent()) if self.wBrawlController.isModeActive() else ''

    def select(self):
        super(_WeekendBrawlItem, self).select()
        selectorUtils.setBattleTypeAsKnown(self._selectorType)

    def _update(self, state):
        self._isSelected = state.isQueueSelected(QUEUE_TYPE.WEEKEND_BRAWL)
        self._isDisabled = state.hasLockedState
        self._isVisible = self.wBrawlController.isModeActive()


class _BaseSelectorItems(object):

    def __init__(self, items, extraItems=None):
        super(_BaseSelectorItems, self).__init__()
        self.__items = {item.getData():item for item in items}
        self.__extraItems = {item.getData():item for item in extraItems} if extraItems else dict()
        self.__isDemonstrator = False
        self.__isDemoButtonEnabled = False

    def init(self):
        pass

    def fini(self):
        self.__items.clear()
        self.__extraItems.clear()
        self.__isDemonstrator = False
        self.__isDemoButtonEnabled = False

    @property
    def allItems(self):
        return self.__items.values() + self.__extraItems.values()

    def update(self, state):
        selected = self.__items[self._getDefaultPAN()]
        for item in self.__items.itervalues():
            item.update(state)
            if item.isSelected():
                selected = item

        for item in self.__extraItems.itervalues():
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

    def select(self, action, onlyActive=False):
        if action in self.__items:
            item = self.__items[action]
            if not onlyActive or item.isVisible() and not item.isDisabled():
                item.select()
        elif action in self.__extraItems:
            item = self.__extraItems[action]
            if not onlyActive or item.isVisible() and not item.isDisabled():
                item.select()
        else:
            for _, value in self.__extraItems.items():
                if action in value.getData():
                    value.select()
                    return

            _logger.error('Can not invoke action: %s', action)

    def getVOs(self):

        def getVisibleVOs(items):
            return [ item.getVO() for item in sorted(items.itervalues()) if item.isVisible() ]

        return (getVisibleVOs(self.__items),
         getVisibleVOs(self.__extraItems),
         self.__isDemonstrator,
         self.__isDemoButtonEnabled)

    def getItems(self):
        return self.__items

    def _getDefaultPAN(self):
        return _DEFAULT_PAN

    def isSelected(self, action):
        if action in self.__items:
            return self.__items[action].isSelected()
        if action in self.__extraItems:
            return self.__extraItems[action].isSelected()
        _logger.error('Action not found: %s', action)
        return False


@loggerTarget(logKey=MS_LOG_KEYS.BATTLE_TYPES, loggerCls=ModeSelectorUILogger)
class _BattleSelectorItems(_BaseSelectorItems):

    @loggerEntry
    def init(self):
        return super(_BattleSelectorItems, self).init()

    @logChangeMode
    def update(self, state):
        return super(_BattleSelectorItems, self).update(state)


class _SquadSelectorItems(_BaseSelectorItems):

    def _getDefaultPAN(self):
        return _DEFAULT_SQUAD_PAN


class _SquadItem(SelectorItem):

    def __init__(self, label, data, order, selectorType=None, isVisible=True):
        super(_SquadItem, self).__init__(label, data, order, selectorType, isVisible)
        self._isDisabled = False
        self._isSelected = False
        self._isVisible = True
        self._isDescription = True
        self._prebattleType = None
        return

    def getFormattedLabel(self):
        title = text_styles.middleTitle(backport.text(R.strings.menu.headerButtons.battle.types.dyn(self._data)()))
        if self._isDescription:
            description = text_styles.main(backport.text(R.strings.menu.headerButtons.battle.types.dyn(self._data).description()))
            return ''.join((title, '\n', description))
        return title

    def getVO(self):
        vo = super(_SquadItem, self).getVO()
        vo['tooltip'] = self._createTooltip()
        return vo

    def _createTooltip(self):
        return makeTooltip(backport.text(R.strings.platoon.headerButton.tooltips.dyn(self._data).header()), backport.text(R.strings.platoon.headerButton.tooltips.dyn(self._data).body()))

    def getPrebattleType(self):
        return self._prebattleType

    @property
    def squadIcon(self):
        return backport.image(_R_ICONS.battleTypes.c_40x40.squad())


class _SimpleSquadItem(_SquadItem):

    def _update(self, state):
        self._isSelected = state.isInUnit(PREBATTLE_TYPE.SQUAD)
        self._isDisabled = state.hasLockedState and not state.isInUnit(PREBATTLE_TYPE.SQUAD)
        self._isVisible = not state.isInPreQueue(queueType=QUEUE_TYPE.BATTLE_ROYALE)


class _SpecialSquadItem(_SquadItem):

    def __init__(self, label, data, order, selectorType=None, isVisible=False):
        super(_SpecialSquadItem, self).__init__(label, data, order, selectorType, isVisible)
        self._isDisabled = False
        self._isSelected = False
        self._isVisible = isVisible
        self._isSpecialBgIcon = False

    def getVO(self):
        vo = super(_SpecialSquadItem, self).getVO()
        if self._isSpecialBgIcon:
            vo['specialBgIcon'] = backport.image(R.images.gui.maps.icons.lobby.eventPopoverBtnBG())
        return vo

    def _update(self, state):
        self._isSelected = state.isInUnit(self._prebattleType)
        self._isDisabled = state.hasLockedState and not state.isInUnit(self._prebattleType)


class _EventSquadItem(_SpecialSquadItem):
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, label, data, order, selectorType=None, isVisible=True):
        super(_EventSquadItem, self).__init__(label, data, order, selectorType, isVisible)
        self._prebattleType = PREBATTLE_TYPE.EVENT
        self._isVisible = self.__eventsCache.isEventEnabled()
        self._isSpecialBgIcon = True
        self._isDescription = False

    @property
    def squadIcon(self):
        return backport.image(_R_ICONS.battleTypes.c_40x40.eventSquad())


class _BattleRoyaleSquadItem(_SpecialSquadItem):
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)

    def __init__(self, label, data, order, selectorType=None, isVisible=True):
        super(_BattleRoyaleSquadItem, self).__init__(label, data, order, selectorType, isVisible)
        primeTimeStatus, _, _ = self.__battleRoyaleController.getPrimeTimeStatus()
        self._prebattleType = PREBATTLE_TYPE.BATTLE_ROYALE
        self._isVisible = self.__battleRoyaleController.isEnabled() and self.__battleRoyaleController.isInPrimeTime()
        self._isDisabled = self._isDisabled or primeTimeStatus != PrimeTimeStatus.AVAILABLE

    def _update(self, state):
        super(_BattleRoyaleSquadItem, self)._update(state)
        self._isSelected = state.isQueueSelected(QUEUE_TYPE.BATTLE_ROYALE)
        primeTimeStatus, _, _ = self.__battleRoyaleController.getPrimeTimeStatus()
        self._isVisible = self.__battleRoyaleController.isEnabled() and self.__battleRoyaleController.isInPrimeTime() and state.isInPreQueue(queueType=QUEUE_TYPE.BATTLE_ROYALE)
        self._isDisabled = self._isDisabled or primeTimeStatus != PrimeTimeStatus.AVAILABLE

    def getSpecialBGIcon(self):
        return backport.image(_R_ICONS.lobby.eventPopoverBtnBG())

    @property
    def squadIcon(self):
        return backport.image(_R_ICONS.battleTypes.c_40x40.royaleSquad())


class _RankedItem(_SelectorItem):
    rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, label, data, order, selectorType=None, isVisible=True):
        super(_RankedItem, self).__init__(label, data, order, selectorType, isVisible)
        self.__hasPastSeason = False

    def isRandomBattle(self):
        return True

    def getFormattedLabel(self):
        battleTypeName = super(_RankedItem, self).getFormattedLabel()
        availabilityStr = self.__getAvailabilityStr()
        return battleTypeName if availabilityStr is None else '{}\n{}'.format(battleTypeName, availabilityStr)

    def getSpecialBGIcon(self):
        return backport.image(_R_ICONS.buttons.selectorRendererBGEvent()) if self.rankedController.isAvailable() else ''

    def select(self):
        if self.rankedController.isAvailable():
            super(_RankedItem, self).select()
        elif self.__hasPastSeason:
            ctx = {'selectedItemID': RANKEDBATTLES_CONSTS.RANKED_BATTLES_RANKS_ID}
            if self.rankedController.isYearLBEnabled() and self.rankedController.isYearGap():
                ctx = {'selectedItemID': RANKEDBATTLES_CONSTS.RANKED_BATTLES_YEAR_RATING_ID}
            self.rankedController.showRankedBattlePage(ctx)
        selectorUtils.setBattleTypeAsKnown(self._selectorType)

    def _update(self, state):
        self._isSelected = state.isInPreQueue(QUEUE_TYPE.RANKED)
        self.__hasPastSeason = self.rankedController.getPreviousSeason() is not None
        isDisabled = self.rankedController.isFrozen() and self.rankedController.getCurrentSeason() is not None
        self._isDisabled = state.hasLockedState or isDisabled
        self._isVisible = self.rankedController.isEnabled()
        return

    def __getAvailabilityStr(self):
        if self._isVisible and self.rankedController.hasAnySeason():
            resShortCut = R.strings.menu.headerButtons.battle.types.ranked
            currentSeason = self.rankedController.getCurrentSeason()
            if currentSeason is not None:
                if self.rankedController.isUnset():
                    return backport.text(resShortCut.availability.notSet())
                if self.rankedController.isFrozen():
                    return backport.text(resShortCut.availability.frozen())
                seasonName = currentSeason.getUserName() or currentSeason.getNumber()
                return backport.text(resShortCut.availability.season(), season=seasonName)
            nextSeason = self.rankedController.getNextSeason()
            if nextSeason is not None:
                timeStamp = time_utils.makeLocalServerTime(nextSeason.getStartDate())
                date = backport.getShortDateFormat(timeStamp)
                time = backport.getShortTimeFormat(timeStamp)
                return backport.text(resShortCut.availability.until(), date=date, time=time)
            if self.rankedController.isYearGap():
                return backport.text(resShortCut.availability.yearEnded())
            return backport.text(resShortCut.availability.ended())
        else:
            return


class _BattleRoyaleItem(SelectorItem):
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)

    def __init__(self, label, data, order, selectorType=None, isVisible=True):
        super(_BattleRoyaleItem, self).__init__(label, data, order, selectorType, isVisible)
        self._isVisible = self.__getIsVisible()
        self.__isFrozen = False

    def isRandomBattle(self):
        return True

    def getVO(self):
        vo = super(_BattleRoyaleItem, self).getVO()
        isEnabled = self.__battleRoyaleController.isEnabled()
        isActive = self.__battleRoyaleController.isActive()
        if isEnabled and isActive and self.__battleRoyaleController.getCurrentSeason() is not None:
            vo['specialBgIcon'] = backport.image(R.images.gui.maps.icons.buttons.selectorRendererBGEvent())
        return vo

    def getFormattedLabel(self):
        battleTypeName = super(_BattleRoyaleItem, self).getFormattedLabel()
        availabilityStr = self.__getPerformanceAlarmStr() or self.__getScheduleStr()
        return battleTypeName if availabilityStr is None else '%s\n%s' % (battleTypeName, availabilityStr)

    @process
    def _doSelect(self, dispatcher):
        currentSeason = self.__battleRoyaleController.getCurrentSeason()
        if currentSeason is not None:
            isActiveCycle = self.__battleRoyaleController.getCurrentCycleInfo()[1]
            nextCycle = currentSeason.getNextByTimeCycle(time_utils.getCurrentLocalServerTimestamp())
            if isActiveCycle or nextCycle:
                self.__battleRoyaleController.setDefaultHangarEntryPoint()
                isSuccess = yield dispatcher.doSelectAction(PrbAction(self._data))
                if isSuccess and self._isNew:
                    selectorUtils.setBattleTypeAsKnown(self._selectorType)
                else:
                    return
        self.__battleRoyaleController.openURL()
        return

    def _update(self, state):
        isNow = self.__battleRoyaleController.isInPrimeTime()
        isEnabled = self.__battleRoyaleController.isEnabled()
        self.__isFrozen = self.__battleRoyaleController.isFrozen() or not isEnabled
        self._isVisible = self.__getIsVisible()
        if not isEnabled or not isNow:
            self._isLocked = True
        self._isDisabled = state.hasLockedState or not isEnabled
        self._isSelected = state.isQueueSelected(QUEUE_TYPE.BATTLE_ROYALE)

    def __getScheduleStr(self):
        if self.__isFrozen:
            return backport.text(R.strings.menu.headerButtons.battle.types.battleRoyale.extra.frozen())
        else:
            currentSeason = self.__battleRoyaleController.getCurrentSeason()
            if currentSeason is not None and currentSeason.hasActiveCycle(time_utils.getCurrentLocalServerTimestamp()):
                seasonResID = R.strings.epic_battle.season.num(currentSeason.getSeasonID())
                seasonName = backport.text(seasonResID.name()) if seasonResID else None
                scheduleStr = backport.text(R.strings.menu.headerButtons.battle.types.battleRoyale.extra.currentCycle(), season=seasonName, cycle=int2roman(currentSeason.getCycleOrdinalNumber()))
                return text_styles.main(scheduleStr)
            currentOrNextSeason = currentSeason or self.__battleRoyaleController.getNextSeason()
            if currentOrNextSeason is not None:
                nextCycle = currentOrNextSeason.getNextByTimeCycle(time_utils.getCurrentLocalServerTimestamp())
                if nextCycle:
                    scheduleStr = backport.text(R.strings.menu.headerButtons.battle.types.battleRoyale.extra.startsAt(), time=backport.getDateTimeFormat(nextCycle.startDate))
                    return text_styles.main(scheduleStr)
            scheduleStr = backport.text(R.strings.menu.headerButtons.battle.types.battleRoyale.extra.finished())
            return text_styles.main(scheduleStr)

    def __getPerformanceAlarmStr(self):
        currPerformanceGroup = self.__battleRoyaleController.getPerformanceGroup()
        attentionText, iconPath = (None, None)
        if currPerformanceGroup == BattleRoyalePerfProblems.HIGH_RISK:
            attentionText = text_styles.error(backport.text(R.strings.menu.headerButtons.battle.menu.attention.lowPerformance()))
            iconPath = backport.image(R.images.gui.maps.icons.library.marker_blocked())
        elif currPerformanceGroup == BattleRoyalePerfProblems.MEDIUM_RISK:
            attentionText = text_styles.alert(backport.text(R.strings.menu.headerButtons.battle.menu.attention.reducedPerformance()))
            iconPath = backport.image(R.images.gui.maps.icons.library.alertIcon())
        return icons.makeImageTag(iconPath, vSpace=-3) + ' ' + attentionText if attentionText and iconPath else None

    def __getIsVisible(self):
        if self.__battleRoyaleController.isEnabled():
            return True
        else:
            season = self.__battleRoyaleController.getCurrentSeason() or self.__battleRoyaleController.getNextSeason()
            return season is not None


_g_items = None
_g_squadItems = None
_DEFAULT_PAN = PREBATTLE_ACTION_NAME.RANDOM
_DEFAULT_SQUAD_PAN = PREBATTLE_ACTION_NAME.SQUAD

@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def _createItems(lobbyContext=None):
    settings = lobbyContext.getServerSettings()
    isInRoaming = settings.roaming.isInRoaming()
    items = []
    _addRandomBattleType(items)
    _addWeekendBrawlBattleType(items)
    _addRankedBattleType(items, settings)
    _addCommandBattleType(items, settings)
    _addStrongholdsBattleType(items, isInRoaming)
    _addTrainingBattleType(items)
    _addEpicTrainingBattleType(items, settings)
    _addRoyaleBattleType(items)
    if GUI_SETTINGS.specPrebatlesVisible:
        _addSpecialBattleType(items)
    if settings is not None and settings.isSandboxEnabled() and not isInRoaming:
        _addSandboxType(items)
    extraItems = []
    _addEventProgressionItems(extraItems)
    return _BattleSelectorItems(items, extraItems)


def _addEventProgressionItems(extraItems):
    extraItems.append(EventProgressionItem(EventProgressionDataProvider()))


def _createSquadSelectorItems():
    items = []
    _addSimpleSquadType(items)
    _addBattleRoyaleSquadType(items)
    _addEventSquadType(items)
    return _SquadSelectorItems(items)


def _addRandomBattleType(items):
    items.append(_RandomQueueItem(backport.text(_R_BATTLE_TYPES.standart()), PREBATTLE_ACTION_NAME.RANDOM, 0))


def _addRankedBattleType(items, settings):
    visible = settings is not None and settings.rankedBattles.isEnabled
    items.append(_RankedItem(backport.text(_R_BATTLE_TYPES.ranked()), PREBATTLE_ACTION_NAME.RANKED, 1, SELECTOR_BATTLE_TYPES.RANKED, isVisible=visible))
    return


def _addRoyaleBattleType(items):
    items.append(_BattleRoyaleItem(MENU.HEADERBUTTONS_BATTLE_TYPES_BATTLEROYALE, PREBATTLE_ACTION_NAME.BATTLE_ROYALE, 2, SELECTOR_BATTLE_TYPES.BATTLE_ROYALE))


def _addCommandBattleType(items, settings):
    visible = settings is not None and settings.isCommandBattleEnabled()
    items.append(_CommandItem(backport.text(_R_BATTLE_TYPES.unit()), PREBATTLE_ACTION_NAME.E_SPORT, 3, SELECTOR_BATTLE_TYPES.UNIT, isVisible=visible))
    return


def _addStrongholdsBattleType(items, isInRoaming):
    visible = isStrongholdsEnabled()
    items.append((_DisabledSelectorItem if isInRoaming else _StrongholdsItem)(backport.text(_R_BATTLE_TYPES.strongholds()), PREBATTLE_ACTION_NAME.STRONGHOLDS_BATTLES_LIST, 4, SELECTOR_BATTLE_TYPES.SORTIE, isVisible=visible))


def _addTrainingBattleType(items):
    items.append(_TrainingItem(backport.text(_R_BATTLE_TYPES.training()), PREBATTLE_ACTION_NAME.TRAININGS_LIST, 7))


def _addEpicTrainingBattleType(items, settings=None):
    visible = settings is not None and settings.frontline.isEpicTrainingEnabled
    items.append(_EpicTrainingItem(backport.text(_R_BATTLE_TYPES.epicTraining()), PREBATTLE_ACTION_NAME.EPIC_TRAINING_LIST, 10, SELECTOR_BATTLE_TYPES.EPIC, isVisible=visible))
    return


def _addSpecialBattleType(items):
    items.append(_SpecBattleItem(backport.text(_R_BATTLE_TYPES.spec()), PREBATTLE_ACTION_NAME.SPEC_BATTLES_LIST, 6))


def _addTutorialBattleType(items, isInRoaming):
    items.append((_DisabledSelectorItem if isInRoaming else _BattleTutorialItem)(backport.text(_R_BATTLE_TYPES.battleTutorial()), PREBATTLE_ACTION_NAME.BATTLE_TUTORIAL, 8))


def _addSandboxType(items):
    items.append(_SandboxItem(backport.text(_R_BATTLE_TYPES.battleTeaching()), PREBATTLE_ACTION_NAME.SANDBOX, 9))


def _addWeekendBrawlBattleType(items):
    items.append(_WeekendBrawlItem(backport.text(_R_BATTLE_TYPES.weekendBrawl()), PREBATTLE_ACTION_NAME.WEEKEND_BRAWL, 2, SELECTOR_BATTLE_TYPES.WEEKEND_BRAWL))


def _addSimpleSquadType(items):
    items.append(_SimpleSquadItem(text_styles.middleTitle(backport.text(_R_BATTLE_TYPES.simpleSquad())), PREBATTLE_ACTION_NAME.SQUAD, 0))


def _addBattleRoyaleSquadType(items):
    label = text_styles.middleTitle(backport.text(R.strings.menu.headerButtons.battle.types.battleRoyaleSquad()))
    items.append(_BattleRoyaleSquadItem(label, PREBATTLE_ACTION_NAME.BATTLE_ROYALE_SQUAD, 2))


def _addEventSquadType(items):
    items.append(_EventSquadItem(text_styles.middleTitle(backport.text(_R_BATTLE_TYPES.eventSquad())), PREBATTLE_ACTION_NAME.EVENT_SQUAD, 2))


def create():
    global _g_squadItems
    global _g_items
    if _g_items is None:
        _g_items = _createItems()
        _g_items.init()
    else:
        _logger.warning('Item already is created')
    if _g_squadItems is None:
        _g_squadItems = _createSquadSelectorItems()
        _g_squadItems.init()
    else:
        _logger.warning('Item already is created')
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
    return _g_items


def getSquadItems():
    return _g_squadItems
