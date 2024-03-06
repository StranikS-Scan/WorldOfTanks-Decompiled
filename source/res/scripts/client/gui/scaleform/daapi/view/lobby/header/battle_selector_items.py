# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/header/battle_selector_items.py
from __future__ import absolute_import
from builtins import object
from future.utils import viewvalues
from functools import total_ordering
from itertools import chain
import logging
import typing
from battle_royale.gui.constants import BattleRoyalePerfProblems
from CurrentVehicle import g_currentVehicle
from account_helpers import isDemonstrator
from account_helpers import isDemonstratorExpert
from adisp import adisp_process
from constants import PREBATTLE_TYPE, QUEUE_TYPE, ACCOUNT_ATTR
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.view.lobby.mapbox import mapbox_helpers
from gui.Scaleform.locale.MENU import MENU
from gui.clans.clan_helpers import isStrongholdsEnabled
from gui.game_control.epic_meta_game_ctrl import EPIC_PERF_GROUP
from gui.impl import backport
from gui.impl.gen import R
from gui.periodic_battles.models import PrimeTimeStatus
from gui.prb_control import prbEntityProperty
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.comp7 import comp7_prb_helpers
from gui.prb_control.prb_getters import areSpecBattlesHidden
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.prb_control.settings import SELECTOR_BATTLE_TYPES
from gui.shared.formatters import text_styles, icons
from gui.shared.utils import SelectorBattleTypesUtils as selectorUtils
from gui.shared.utils.functions import makeTooltip
from helpers import time_utils, dependency, int2roman
from skeletons.gui.game_control import IRankedBattlesController, IBattleRoyaleController, IBattleRoyaleTournamentController, IMapboxController, IMapsTrainingController, IEpicBattleMetaGameController, IEventBattlesController, IComp7Controller, IBootcampController, IWinbackController
from skeletons.gui.lobby_context import ILobbyContext
if typing.TYPE_CHECKING:
    from skeletons.gui.game_control import ISeasonProvider
    cycleStrGetter = typing.Callable[[ISeasonProvider, str, typing.Optional[typing.Callable[[int], str]]], str]
    tillTimeStrGetter = typing.Callable[[int], str]
_logger = logging.getLogger(__name__)
_R_HEADER_BUTTONS = R.strings.menu.headerButtons
_R_BATTLE_TYPES = R.strings.menu.headerButtons.battle.types
_R_BATTLE_MENU = R.strings.menu.headerButtons.battle.menu
_R_ICONS = R.images.gui.maps.icons
_R_BR_TOURNAMENT_BUTTON = R.strings.battle_royale.tournament.fightButton
_HIGHLIGHT_ORANGE_LINKAGE = 'BGAnimOrangeUI'

@total_ordering
class SelectorItem(object):
    __slots__ = ('_label', '_data', '_order', '_selectorType', '_isVisible', '_isExtra', '_isSelected', '_isNew', '_isDisabled', '_isLocked')
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, label, data, order, selectorType=None, isVisible=True, isExtra=False):
        super(SelectorItem, self).__init__()
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

    def __hash__(self):
        return hash(self._order)

    def __eq__(self, other):
        return self._order == other.getOrder()

    def __lt__(self, other):
        return self._order < other.getOrder()

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

    def getHighlightLinkage(self):
        return (_HIGHLIGHT_ORANGE_LINKAGE, '', '')

    @property
    def squadIcon(self):
        return backport.image(_R_ICONS.battleTypes.c_40x40.dyn('squad')())

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
        return any((state.isInUnit(prbType) for prbType in PREBATTLE_TYPE.SQUAD_PREBATTLES))

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

    def isShowActiveModeState(self):
        return False

    def isIgnoreSelectorNewbieRuleInMode(self):
        return False

    def getFormattedLabel(self):
        return text_styles.middleTitle(self.getLabel())

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

    @adisp_process
    def _doSelect(self, dispatcher):
        yield dispatcher.doSelectAction(PrbAction(self.getData()))


class _SelectorExtraItem(SelectorItem):

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


class _MapsTrainingItem(SelectorItem):
    mapsTrainingController = dependency.descriptor(IMapsTrainingController)

    def isRandomBattle(self):
        return True

    def setLocked(self, value):
        self._isLocked = value
        if self._isLocked:
            self._isDisabled = True
            self._isSelected = False

    def _update(self, state):
        self._isVisible = True
        if self.mapsTrainingController.isMapsTrainingEnabled:
            self._isDisabled = state.hasLockedState
            self._isSelected = state.isQueueSelected(QUEUE_TYPE.MAPS_TRAINING)
            return
        self._isDisabled = True
        self._isSelected = False

    @adisp_process
    def _doSelect(self, dispatcher):
        isSuccess = yield dispatcher.doSelectAction(PrbAction(self.getData()))
        if isSuccess:
            if self._isNew:
                selectorUtils.setBattleTypeAsKnown(self._selectorType)
            self.mapsTrainingController.showMapsTrainingPage()


class _DisabledSelectorItem(SelectorItem):

    def update(self, state):
        pass

    def _update(self, state):
        pass

    def select(self):
        _logger.warning('That routine can not be invoked')


class _RandomQueueItem(SelectorItem):
    _winbackController = dependency.descriptor(IWinbackController)

    def isRandomBattle(self):
        return True

    def isDemoButtonDisabled(self):
        return False

    def setLocked(self, value):
        self._isLocked = value
        if self._isLocked:
            self._isDisabled = True
            self._isSelected = False

    def isVisible(self):
        return not self._winbackController.isModeAvailable()

    def _update(self, state):
        self._isDisabled = state.hasLockedState
        self._isSelected = state.isQueueSelected(QUEUE_TYPE.RANDOMS)
        self._isVisible = self.isVisible()


class _WinbackQueueItem(_RandomQueueItem):

    def isDemoButtonDisabled(self):
        return True

    def isInSquad(self, state):
        return False

    def isShowActiveModeState(self):
        return self._winbackController.isModeAvailable()

    def isVisible(self):
        return self._winbackController.isModeAvailable()

    def isShowNewIndicator(self):
        return False

    def _update(self, state):
        self._isDisabled = state.hasLockedState
        self._isSelected = state.isQueueSelected(QUEUE_TYPE.WINBACK) and not self._isLocked
        self._isVisible = self.isVisible()


class _CommandItem(SelectorItem):

    def isRandomBattle(self):
        return True

    def isInSquad(self, state):
        return False

    def _update(self, state):
        isCommandBattleEnabled = self.lobbyContext.getServerSettings().isCommandBattleEnabled()
        self._isSelected = state.isInUnit(PREBATTLE_TYPE.UNIT) or state.isInUnit(PREBATTLE_TYPE.E_SPORT_COMMON)
        self._isDisabled = state.hasLockedState or not isCommandBattleEnabled
        self._isVisible = isCommandBattleEnabled


class _StrongholdsItem(SelectorItem):

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


class _SpecBattleItem(SelectorItem):
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
        if state.isInSpecialPrebattle() or self.__battleRoyaleTournamentController.isSelected():
            self._isSelected = True
            self._isDisabled = state.hasLockedState
        else:
            self._isSelected = False
            self._isDisabled = areSpecBattlesHidden()


class _TrainingItem(SelectorItem):

    def getFightButtonLabel(self, state, playerInfo):
        return backport.text(_R_HEADER_BUTTONS.battle())

    def _update(self, state):
        settings = self.lobbyContext.getServerSettings()
        self._isSelected = state.isInLegacy(PREBATTLE_TYPE.TRAINING)
        self._isDisabled = state.hasLockedState
        self._isVisible = settings is not None and settings.isTrainingBattleEnabled()
        return


class _EpicTrainingItem(SelectorItem):

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


class _EventBattlesItem(SelectorItem):
    __eventBattlesCtrl = dependency.descriptor(IEventBattlesController)

    def isRandomBattle(self):
        return True

    def isShowActiveModeState(self):
        return self.__eventBattlesCtrl.isEnabled()

    def _update(self, state):
        self._isDisabled = state.hasLockedState
        self._isSelected = state.isQueueSelected(QUEUE_TYPE.EVENT_BATTLES)
        self._isVisible = self.__eventBattlesCtrl.isEnabled()


class _BattleSelectorItems(object):
    _winbackController = dependency.descriptor(IWinbackController)

    def __init__(self, items, extraItems=None):
        super(_BattleSelectorItems, self).__init__()
        self.__items = {item.getData():item for item in items}
        self.__extraItems = {item.getData():item for item in extraItems} if extraItems else {}
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
        return chain(viewvalues(self.__items), viewvalues(self.__extraItems))

    def update(self, state):
        selected = self.__items[self._getDefaultPAN()]
        for item in viewvalues(self.__items):
            item.update(state)
            if item.isSelected():
                selected = item

        for item in viewvalues(self.__extraItems):
            item.update(state)
            if item.isSelected():
                selected = item

        if self.__isDemonstrator:
            if not g_currentVehicle.item:
                self.__isDemoButtonEnabled = False
            else:
                self.__isDemoButtonEnabled = not selected.isDemoButtonDisabled()
        return selected

    def validateAccountAttrs(self, attrs):
        self.__isDemonstrator = isDemonstrator(attrs) or isDemonstratorExpert(attrs)
        locked = not attrs & ACCOUNT_ATTR.RANDOM_BATTLES
        for item in viewvalues(self.__items):
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
            for value in self.__extraItems.values():
                if action in value.getData():
                    value.select()
                    return

            _logger.error('Can not invoke action: %s', action)

    def getVOs(self):

        def getVisibleVOs(items):
            return [ item.getVO() for item in sorted(viewvalues(items)) if item.isVisible() ]

        return (getVisibleVOs(self.__items),
         getVisibleVOs(self.__extraItems),
         self.__isDemonstrator,
         self.__isDemoButtonEnabled)

    def getItems(self):
        return self.__items

    def _getDefaultPAN(self):
        return PREBATTLE_ACTION_NAME.WINBACK if self._winbackController.isModeAvailable() else _DEFAULT_PAN

    def isSelected(self, action):
        if action in self.__items:
            return self.__items[action].isSelected()
        if action in self.__extraItems:
            return self.__extraItems[action].isSelected()
        _logger.error('Action not found: %s', action)
        return False

    def hasNew(self):
        return any((item.isShowNewIndicator() and item.isVisible() and not item.isDisabled() for item in self.allItems))

    def hasAnyActiveModeState(self):
        return any((item.isShowActiveModeState() and item.isVisible() for item in self.allItems))

    @property
    def isDemoButtonEnabled(self):
        return self.__isDemoButtonEnabled

    @property
    def isDemonstrator(self):
        return self.__isDemonstrator


class _SquadSelectorItems(_BattleSelectorItems):

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


class SpecialSquadItem(_SquadItem):

    def __init__(self, label, data, order, selectorType=None, isVisible=False):
        super(SpecialSquadItem, self).__init__(label, data, order, selectorType, isVisible)
        self._isDisabled = False
        self._isSelected = False
        self._isVisible = isVisible
        self._isSpecialBgIcon = False

    def getVO(self):
        vo = super(SpecialSquadItem, self).getVO()
        if self._isSpecialBgIcon:
            vo['specialBgIcon'] = backport.image(R.images.gui.maps.icons.lobby.eventPopoverBtnBG())
        return vo

    def _update(self, state):
        self._isSelected = state.isInUnit(self._prebattleType)
        self._isDisabled = state.hasLockedState and not state.isInUnit(self._prebattleType)


class _EventSquadItem(SpecialSquadItem):
    __eventBattlesCtrl = dependency.descriptor(IEventBattlesController)

    def __init__(self, label, data, order, selectorType=None, isVisible=True):
        super(_EventSquadItem, self).__init__(label, data, order, selectorType, isVisible)
        self._prebattleType = PREBATTLE_TYPE.EVENT
        self._isVisible = self.__eventBattlesCtrl.isEnabled()
        self._isSpecialBgIcon = True
        self._isDescription = False

    @property
    def squadIcon(self):
        return backport.image(_R_ICONS.battleTypes.c_40x40.eventSquad())


class _BattleRoyaleSquadItem(SpecialSquadItem):
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


class _MapboxSquadItem(SpecialSquadItem):
    __mapboxCtrl = dependency.descriptor(IMapboxController)

    def __init__(self, label, data, order, selectorType=None, isVisible=True):
        super(_MapboxSquadItem, self).__init__(label, data, order, selectorType, isVisible)
        primeTimeStatus, _, _ = self.__mapboxCtrl.getPrimeTimeStatus()
        self._prebattleType = PREBATTLE_TYPE.MAPBOX
        self._isVisible = self.__mapboxCtrl.isEnabled() and self.__mapboxCtrl.isInPrimeTime()
        self._isDisabled = self._isDisabled or primeTimeStatus != PrimeTimeStatus.AVAILABLE

    def _update(self, state):
        super(_MapboxSquadItem, self)._update(state)
        self._isSelected = self.__mapboxCtrl.isMapboxMode()
        primeTimeStatus, _, _ = self.__mapboxCtrl.getPrimeTimeStatus()
        self._isVisible = self.__mapboxCtrl.isEnabled() and self.__mapboxCtrl.isInPrimeTime() and state.isInPreQueue(queueType=QUEUE_TYPE.MAPBOX)
        self._isDisabled = self._isDisabled or primeTimeStatus != PrimeTimeStatus.AVAILABLE

    @property
    def squadIcon(self):
        return backport.image(_R_ICONS.battleTypes.c_40x40.mapboxSquad())


class _Comp7SquadItem(SpecialSquadItem):
    __controller = dependency.descriptor(IComp7Controller)

    def __init__(self, label, data, order, selectorType=None, isVisible=True):
        super(_Comp7SquadItem, self).__init__(label, data, order, selectorType, isVisible)
        primeTimeStatus, _, _ = self.__controller.getPrimeTimeStatus()
        self._prebattleType = PREBATTLE_TYPE.COMP7
        self._isVisible = self.__controller.isEnabled() and self.__controller.isInPrimeTime()
        self._isDisabled = self._isDisabled or primeTimeStatus != PrimeTimeStatus.AVAILABLE

    def _update(self, state):
        super(_Comp7SquadItem, self)._update(state)
        self._isSelected = state.isQueueSelected(QUEUE_TYPE.COMP7)
        primeTimeStatus, _, _ = self.__controller.getPrimeTimeStatus()
        self._isVisible = self.__controller.isEnabled() and self.__controller.isInPrimeTime() and state.isInPreQueue(queueType=QUEUE_TYPE.COMP7)
        self._isDisabled = self._isDisabled or primeTimeStatus != PrimeTimeStatus.AVAILABLE

    @property
    def squadIcon(self):
        return backport.image(_R_ICONS.battleTypes.c_40x40.comp7Squad())


class _RankedItem(SelectorItem):
    rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, label, data, order, selectorType=None, isVisible=True):
        super(_RankedItem, self).__init__(label, data, order, selectorType, isVisible)
        self.__hasPastSeason = False

    def isRandomBattle(self):
        return True

    def isShowActiveModeState(self):
        return self.rankedController.isAvailable()

    def getFormattedLabel(self):
        battleTypeName = super(_RankedItem, self).getFormattedLabel()
        availabilityStr = self.__getAvailabilityStr()
        return battleTypeName if availabilityStr is None else '{}\n{}'.format(battleTypeName, availabilityStr)

    def getSpecialBGIcon(self):
        return backport.image(_R_ICONS.buttons.selectorRendererBGEvent()) if self.rankedController.isAvailable() else ''

    def select(self):
        self.rankedController.doActionOnEntryPointClick()
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
    __bootcampController = dependency.descriptor(IBootcampController)

    def __init__(self, label, data, order, selectorType=None, isVisible=True):
        super(_BattleRoyaleItem, self).__init__(label, data, order, selectorType, isVisible)
        self._isVisible = self.__getIsVisible()
        self.__isFrozen = False

    def isRandomBattle(self):
        return True

    def isShowActiveModeState(self):
        _, isBrCycle = self.__battleRoyaleController.getCurrentCycleInfo()
        return isBrCycle and self.__battleRoyaleController.isEnabled()

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

    @adisp_process
    def _doSelect(self, dispatcher):
        currentSeason = self.__battleRoyaleController.getCurrentSeason()
        if currentSeason is None:
            self.__battleRoyaleController.openURL()
            return
        else:
            isActiveCycle = self.__battleRoyaleController.getCurrentCycleInfo()[1]
            nextCycle = currentSeason.getNextByTimeCycle(time_utils.getCurrentLocalServerTimestamp())
            if isActiveCycle or nextCycle:
                self.__battleRoyaleController.setDefaultHangarEntryPoint()
                yield dispatcher.doSelectAction(PrbAction(self._data))
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
                seasonResID = R.strings.battle_royale.season.num(currentSeason.getSeasonID())
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
        season = self.__battleRoyaleController.getCurrentSeason() or self.__battleRoyaleController.getNextSeason()
        return season is not None and not self.__bootcampController.isInBootcamp()


class _MapboxItem(SelectorItem):
    __mapboxCtrl = dependency.descriptor(IMapboxController)
    __bootcampController = dependency.descriptor(IBootcampController)

    def __init__(self, label, data, order, selectorType=None, isVisible=True):
        super(_MapboxItem, self).__init__(label, data, order, selectorType, isVisible)
        self._isVisible = self.__getIsVisible()
        self.__isFrozen = False

    def isRandomBattle(self):
        return True

    def isShowActiveModeState(self):
        return self.__mapboxCtrl.isActive() and self.__mapboxCtrl.isInPrimeTime()

    def getVO(self):
        vo = super(_MapboxItem, self).getVO()
        if self.__mapboxCtrl.isActive() and self.__mapboxCtrl.isInPrimeTime():
            vo['specialBgIcon'] = backport.image(R.images.gui.maps.icons.buttons.selectorRendererBGEvent())
        return vo

    def getFormattedLabel(self):
        battleTypeName = super(_MapboxItem, self).getFormattedLabel()
        availabilityStr = self.__getScheduleStr()
        return battleTypeName if availabilityStr is None else '%s\n%s' % (battleTypeName, availabilityStr)

    @adisp_process
    def _doSelect(self, dispatcher):
        currentSeason = self.__mapboxCtrl.getCurrentSeason()
        if currentSeason is not None:
            if self.__mapboxCtrl.getCurrentOrNextActiveCycleNumber(currentSeason):
                yield dispatcher.doSelectAction(PrbAction(self._data))
        return

    def _update(self, state):
        isNow = self.__mapboxCtrl.isInPrimeTime()
        isEnabled = self.__mapboxCtrl.isEnabled()
        self.__isFrozen = self.__mapboxCtrl.isFrozen() or not isEnabled
        self._isVisible = self.__getIsVisible()
        if not isEnabled or not isNow:
            self._isLocked = True
        self._isDisabled = state.hasLockedState or not isEnabled or self.__mapboxCtrl.getCurrentCycleID() is None
        self._isSelected = state.isQueueSelected(QUEUE_TYPE.MAPBOX)
        return

    def __getScheduleStr(self):
        return text_styles.main(backport.text(R.strings.menu.headerButtons.battle.types.mapbox.extra.frozen())) if self.__isFrozen else _getSeasonInfoStr(self.__mapboxCtrl, SELECTOR_BATTLE_TYPES.MAPBOX, timeLeftStrGetter=mapbox_helpers.getTillTimeString)

    def __getIsVisible(self):
        hasActualSeason = (self.__mapboxCtrl.getCurrentSeason() or self.__mapboxCtrl.getNextSeason()) is not None
        return not self.__bootcampController.isInBootcamp() and self.__mapboxCtrl.isEnabled() and hasActualSeason


class EpicBattleItem(SelectorItem):
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)

    def __init__(self, label, data, order, selectorType=None, isVisible=True):
        super(EpicBattleItem, self).__init__(label, data, order, selectorType, isVisible)
        self._isDisabled = not self.__epicController.isEnabled()

    def isShowActiveModeState(self):
        return self.__epicController.isEnabled() and self.__epicController.isCurrentCycleActive()

    def getFormattedLabel(self):
        battleTypeName = text_styles.middleTitle(self.getLabel())
        availabilityStr = self.__getPerformanceAlarmStr() or self.__getScheduleStr()
        return battleTypeName if availabilityStr is None else '{}\n{}'.format(battleTypeName, availabilityStr)

    def isRandomBattle(self):
        return True

    @adisp_process
    def _doSelect(self, dispatcher):
        currentSeason = self.__epicController.getCurrentSeason()
        isActiveCycle = False
        if currentSeason is not None:
            isActiveCycle = self.__epicController.getCurrentCycleInfo()[1]
            nextCycle = currentSeason.getNextByTimeCycle(time_utils.getCurrentLocalServerTimestamp())
            if isActiveCycle or nextCycle:
                yield dispatcher.doSelectAction(PrbAction(self._data))
        if self._isNew:
            selectorUtils.setBattleTypeAsKnown(self._selectorType)
        return

    def _update(self, state):
        self._isVisible = any((self.__epicController.getCurrentSeason(), self.__epicController.getNextSeason()))
        self._isDisabled = not self.__epicController.isEnabled() or state.hasLockedState
        self._isSelected = state.isQueueSelected(QUEUE_TYPE.EPIC)
        self.__epicController.storeCycle()
        if self._selectorType is not None:
            self._isNew = not selectorUtils.isKnownBattleType(self._selectorType)
        self._isLocked = not self.__epicController.isEnabled()
        return

    def __getScheduleStr(self):
        if self._isDisabled:
            return text_styles.error(backport.text(_R_BATTLE_TYPES.epic.extra.frozen()))
        else:
            currentSeason = self.__epicController.getCurrentSeason()
            if currentSeason:
                if currentSeason.hasActiveCycle(time_utils.getCurrentLocalServerTimestamp()):
                    scheduleStr = None
                else:
                    nextCycle = currentSeason.getNextCycleInfo(time_utils.getCurrentLocalServerTimestamp())
                    if nextCycle is None:
                        nextCycle = currentSeason.getNextByTimeCycle(time_utils.getCurrentLocalServerTimestamp())
                    if nextCycle:
                        nextCycleStartTime = backport.getDateTimeFormat(nextCycle.startDate)
                        scheduleStr = backport.text(_R_BATTLE_TYPES.epic.extra.startsAt(), time=nextCycleStartTime)
                    else:
                        scheduleStr = None
            else:
                nextSeason = self.__epicController.getNextSeason()
                nextCycle = nextSeason.getNextByTimeCycle(time_utils.getCurrentLocalServerTimestamp())
                if nextCycle:
                    startTime = backport.getDateTimeFormat(nextCycle.startDate)
                    scheduleStr = backport.text(_R_BATTLE_TYPES.epic.extra.startsAt(), time=startTime)
                else:
                    scheduleStr = None
            return text_styles.main(scheduleStr) if scheduleStr else None

    def __getPerformanceAlarmStr(self):
        currPerformanceGroup = self.__epicController.getPerformanceGroup()
        attentionText, iconPath = (None, None)
        if currPerformanceGroup == EPIC_PERF_GROUP.HIGH_RISK:
            attentionText = text_styles.error(backport.text(_R_BATTLE_MENU.attention.lowPerformance()))
            iconPath = backport.image(_R_ICONS.library.marker_blocked())
        elif currPerformanceGroup == EPIC_PERF_GROUP.MEDIUM_RISK:
            attentionText = text_styles.alert(backport.text(_R_BATTLE_MENU.attention.reducedPerformance()))
            iconPath = backport.image(_R_ICONS.library.alertIcon())
        return icons.makeImageTag(iconPath, vSpace=-3) + ' ' + attentionText if attentionText and iconPath else None


class _Comp7Item(SelectorItem):
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __bootcampController = dependency.descriptor(IBootcampController)

    def isInSquad(self, state):
        return state.isInUnit(PREBATTLE_TYPE.COMP7)

    def isRandomBattle(self):
        return True

    def select(self):
        comp7_prb_helpers.selectComp7()
        selectorUtils.setBattleTypeAsKnown(self._selectorType)

    def getFormattedLabel(self):
        battleTypeName = super(_Comp7Item, self).getFormattedLabel()
        scheduleStr = self.__getScheduleStr()
        label = '{}\n{}'.format(battleTypeName, scheduleStr) if scheduleStr else battleTypeName
        return label

    def getSpecialBGIcon(self):
        return backport.image(_R_ICONS.buttons.selectorRendererBGEvent()) if self.__comp7Controller.isAvailable() else ''

    def _update(self, state):
        self._isSelected = state.isQueueSelected(QUEUE_TYPE.COMP7)
        self._isVisible = self.__comp7Controller.isEnabled() and not self.__bootcampController.isInBootcamp()
        self._isDisabled = state.hasLockedState or self.__comp7Controller.isFrozen()

    @classmethod
    def __getScheduleStr(cls):
        previousSeason = cls.__comp7Controller.getPreviousSeason()
        currentSeason = cls.__comp7Controller.getCurrentSeason()
        nextSeason = cls.__comp7Controller.getNextSeason()
        if previousSeason is None and currentSeason is None and nextSeason is None:
            return ''
        else:
            return text_styles.main(backport.text(_R_HEADER_BUTTONS.battle.types.comp7.extra.frozen())) if cls.__comp7Controller.isFrozen() else _getSeasonInfoStr(cls.__comp7Controller, SELECTOR_BATTLE_TYPES.COMP7)


_g_items = None
_g_squadItems = None
_DEFAULT_PAN = PREBATTLE_ACTION_NAME.RANDOM
_DEFAULT_SQUAD_PAN = PREBATTLE_ACTION_NAME.SQUAD

def _addRandomBattleType(items):
    items.append(_RandomQueueItem(backport.text(_R_BATTLE_TYPES.standart()), PREBATTLE_ACTION_NAME.RANDOM, 0))


def _addComp7BattleType(items):
    items.append(_Comp7Item(MENU.HEADERBUTTONS_BATTLE_TYPES_COMP7, PREBATTLE_ACTION_NAME.COMP7, 1, SELECTOR_BATTLE_TYPES.COMP7))


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def _addRankedBattleType(items, lobbyContext=None):
    settings = lobbyContext.getServerSettings()
    visible = settings is not None and settings.rankedBattles.isEnabled
    items.append(_RankedItem(backport.text(_R_BATTLE_TYPES.ranked()), PREBATTLE_ACTION_NAME.RANKED, 2, SELECTOR_BATTLE_TYPES.RANKED, isVisible=visible))
    return


def _addRoyaleBattleType(items):
    items.append(_BattleRoyaleItem(MENU.HEADERBUTTONS_BATTLE_TYPES_BATTLEROYALE, PREBATTLE_ACTION_NAME.BATTLE_ROYALE, 3, SELECTOR_BATTLE_TYPES.BATTLE_ROYALE))


def _addMapboxBattleType(items):
    items.append(_MapboxItem(backport.text(_R_BATTLE_TYPES.mapbox()), PREBATTLE_ACTION_NAME.MAPBOX, 3, SELECTOR_BATTLE_TYPES.MAPBOX))


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def _addCommandBattleType(items, lobbyContext=None):
    settings = lobbyContext.getServerSettings()
    visible = settings is not None and settings.isCommandBattleEnabled()
    items.append(_CommandItem(backport.text(_R_BATTLE_TYPES.unit()), PREBATTLE_ACTION_NAME.E_SPORT, 4, SELECTOR_BATTLE_TYPES.UNIT, isVisible=visible))
    return


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def _addStrongholdsBattleType(items, lobbyContext=None):
    settings = lobbyContext.getServerSettings()
    isInRoaming = settings.roaming.isInRoaming()
    visible = isStrongholdsEnabled()
    items.append((_DisabledSelectorItem if isInRoaming else _StrongholdsItem)(backport.text(_R_BATTLE_TYPES.strongholds()), PREBATTLE_ACTION_NAME.STRONGHOLDS_BATTLES_LIST, 5, SELECTOR_BATTLE_TYPES.SORTIE, isVisible=visible))


def _addEpicBattleType(items):
    items.append(EpicBattleItem(MENU.HEADERBUTTONS_BATTLE_TYPES_EPIC, PREBATTLE_ACTION_NAME.EPIC, 6, SELECTOR_BATTLE_TYPES.EPIC))


def _addSpecialBattleType(items):
    items.append(_SpecBattleItem(backport.text(_R_BATTLE_TYPES.spec()), PREBATTLE_ACTION_NAME.SPEC_BATTLES_LIST, 7))


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def _addTrainingBattleType(items, lobbyContext=None):
    settings = lobbyContext.getServerSettings()
    visible = settings is not None and settings.isTrainingBattleEnabled()
    items.append(_TrainingItem(backport.text(_R_BATTLE_TYPES.training()), PREBATTLE_ACTION_NAME.TRAININGS_LIST, 8, isVisible=visible))
    return


def _addMapsTrainingBattleType(items):
    items.append(_MapsTrainingItem(backport.text(_R_BATTLE_TYPES.mapsTraining()), PREBATTLE_ACTION_NAME.MAPS_TRAINING, 9, SELECTOR_BATTLE_TYPES.MAPS_TRAINING))


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def _addEpicTrainingBattleType(items, lobbyContext=None):
    settings = lobbyContext.getServerSettings()
    visible = settings is not None and settings.frontline.isEpicTrainingEnabled
    items.append(_EpicTrainingItem(backport.text(_R_BATTLE_TYPES.epicTraining()), PREBATTLE_ACTION_NAME.EPIC_TRAINING_LIST, 12, SELECTOR_BATTLE_TYPES.EPIC, isVisible=visible))
    return


def _addWinbackBattleType(items):
    items.append(_WinbackQueueItem(backport.text(_R_BATTLE_TYPES.winback()), PREBATTLE_ACTION_NAME.WINBACK, 13, SELECTOR_BATTLE_TYPES.WINBACK))


def _addEventBattlesType(items):
    items.append(_EventBattlesItem('Event Battle', PREBATTLE_ACTION_NAME.EVENT_BATTLE, 2, SELECTOR_BATTLE_TYPES.EVENT))


BATTLES_SELECTOR_ITEMS = {PREBATTLE_ACTION_NAME.RANDOM: _addRandomBattleType,
 PREBATTLE_ACTION_NAME.WINBACK: _addWinbackBattleType,
 PREBATTLE_ACTION_NAME.RANKED: _addRankedBattleType,
 PREBATTLE_ACTION_NAME.E_SPORT: _addCommandBattleType,
 PREBATTLE_ACTION_NAME.STRONGHOLDS_BATTLES_LIST: _addStrongholdsBattleType,
 PREBATTLE_ACTION_NAME.TRAININGS_LIST: _addTrainingBattleType,
 PREBATTLE_ACTION_NAME.EPIC_TRAINING_LIST: _addEpicTrainingBattleType,
 PREBATTLE_ACTION_NAME.BATTLE_ROYALE: _addRoyaleBattleType,
 PREBATTLE_ACTION_NAME.MAPBOX: _addMapboxBattleType,
 PREBATTLE_ACTION_NAME.MAPS_TRAINING: _addMapsTrainingBattleType,
 PREBATTLE_ACTION_NAME.EPIC: _addEpicBattleType,
 PREBATTLE_ACTION_NAME.EVENT_BATTLE: _addEventBattlesType,
 PREBATTLE_ACTION_NAME.COMP7: _addComp7BattleType}

def _createItems():
    items = []
    for battleItem in viewvalues(BATTLES_SELECTOR_ITEMS):
        battleItem(items)

    if GUI_SETTINGS.specPrebatlesVisible:
        _addSpecialBattleType(items)
    return _BattleSelectorItems(items)


def _addSimpleSquadType(items):
    items.append(_SimpleSquadItem(text_styles.middleTitle(backport.text(_R_BATTLE_TYPES.simpleSquad())), PREBATTLE_ACTION_NAME.SQUAD, 0))


def _addComp7SquadType(items):
    items.append(_Comp7SquadItem(text_styles.middleTitle(backport.text(_R_BATTLE_TYPES.comp7Squad())), PREBATTLE_ACTION_NAME.COMP7_SQUAD, 1))


def _addBattleRoyaleSquadType(items):
    label = text_styles.middleTitle(backport.text(R.strings.menu.headerButtons.battle.types.battleRoyaleSquad()))
    items.append(_BattleRoyaleSquadItem(label, PREBATTLE_ACTION_NAME.BATTLE_ROYALE_SQUAD, 2))


def _addEventSquadType(items):
    items.append(_EventSquadItem(text_styles.middleTitle(backport.text(_R_BATTLE_TYPES.eventSquad())), PREBATTLE_ACTION_NAME.EVENT_SQUAD, 2))


def _addMapboxSquadType(items):
    items.append(_MapboxSquadItem(text_styles.middleTitle(backport.text(_R_BATTLE_TYPES.mapboxSquad())), PREBATTLE_ACTION_NAME.MAPBOX_SQUAD, 2))


BATTLES_SELECTOR_SQUAD_ITEMS = {PREBATTLE_ACTION_NAME.SQUAD: _addSimpleSquadType,
 PREBATTLE_ACTION_NAME.BATTLE_ROYALE_SQUAD: _addBattleRoyaleSquadType,
 PREBATTLE_ACTION_NAME.MAPBOX_SQUAD: _addMapboxSquadType,
 PREBATTLE_ACTION_NAME.EVENT_SQUAD: _addEventSquadType,
 PREBATTLE_ACTION_NAME.COMP7_SQUAD: _addComp7SquadType}

def _createSquadSelectorItems():
    items = []
    for battleSquadItem in BATTLES_SELECTOR_SQUAD_ITEMS.values():
        battleSquadItem(items)

    return _SquadSelectorItems(items)


def _getCycleEndsInStr(modeCtrl, modeName, timeLeftStrGetter=time_utils.getTillTimeString):
    modeStrBase = R.strings.menu.headerButtons.battle.types.dyn(modeName)
    scheduleStr = backport.text(modeStrBase.extra.endsIn(), timeLeft=timeLeftStrGetter(modeCtrl.getEventEndTimestamp()))
    return text_styles.main(scheduleStr)


def _getCycleStartsAtStr(modeCtrl, modeName, timeStrGetter=backport.getDateTimeFormat):
    currentOrNextSeason = modeCtrl.getCurrentSeason() or modeCtrl.getNextSeason()
    nextCycle = currentOrNextSeason.getNextByTimeCycle(time_utils.getCurrentLocalServerTimestamp())
    scheduleStr = backport.text(R.strings.menu.headerButtons.battle.types.dyn(modeName).extra.startsAt(), time=timeStrGetter(time_utils.makeLocalServerTime(nextCycle.startDate)))
    return text_styles.main(scheduleStr)


def _getTillTimeString(timeStamp):
    timeLeft = time_utils.getTimeDeltaFromNow(timeStamp)
    return backport.backport_time_utils.getTillTimeStringByRClass(timeLeft, R.strings.tooltips.tillTime)


def _getSeasonInfoStr(modeCtrl, modeName, activeCycleStrGetter=_getCycleEndsInStr, nextCycleStrGetter=_getCycleStartsAtStr, timeLeftStrGetter=_getTillTimeString):
    currentSeason = modeCtrl.getCurrentSeason()
    if currentSeason is not None and currentSeason.hasActiveCycle(time_utils.getCurrentLocalServerTimestamp()):
        return activeCycleStrGetter(modeCtrl, modeName, timeLeftStrGetter)
    else:
        currentOrNextSeason = currentSeason or modeCtrl.getNextSeason()
        if currentOrNextSeason is not None:
            nextCycle = currentOrNextSeason.getNextByTimeCycle(time_utils.getCurrentLocalServerTimestamp())
            if nextCycle is not None:
                return nextCycleStrGetter(modeCtrl, modeName, backport.getDateTimeFormat)
        scheduleStr = backport.text(R.strings.menu.headerButtons.battle.types.dyn(modeName).extra.finished())
        return text_styles.main(scheduleStr)


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
