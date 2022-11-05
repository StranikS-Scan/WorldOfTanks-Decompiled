# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mode_selector/items/base_item.py
from abc import ABCMeta, abstractmethod
import typing
import Event
from frameworks.wulf import WindowLayer
from gui import GUI_SETTINGS
from gui.battle_pass.battle_pass_helpers import getFormattedTimeLeft
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_card_types import ModeSelectorCardTypes
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_normal_card_model import ModeSelectorNormalCardModel
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_reward_model import ModeSelectorRewardModel
from gui.impl.lobby.mode_selector.items.items_constants import CustomModeName, COLUMN_SETTINGS, DEFAULT_PRIORITY, DEFAULT_COLUMN, ModeSelectorRewardID
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared.event_dispatcher import showBrowserOverlayView
from helpers import dependency, i18n, time_utils
from skeletons.gui.game_control import IBootcampController, IUISpamController
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from typing import Callable, Optional, Type, Union
    from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_card_model import ModeSelectorCardModel
    from gui.Scaleform.daapi.view.lobby.header.battle_selector_items import _SelectorItem
    from gui.impl.gen_utils import DynAccessor
_rMode = R.strings.mode_selector.mode
_INFO_PAGE_KEY_TEMPLATE = 'infoPage%s'

def formatSeasonLeftTime(currentSeason):
    return getFormattedTimeLeft(max(0, currentSeason.getEndDate() - time_utils.getServerUTCTime())) if currentSeason else ''


def getInfoPageKey(modeName):
    return _INFO_PAGE_KEY_TEMPLATE % (modeName[0].upper() + modeName[1:])


class ModeSelectorItem(object):
    __metaclass__ = ABCMeta
    __slots__ = ('_viewModel', '_initialized', '_priority', '_preferredColumn')
    _VIEW_MODEL = None
    _CARD_VISUAL_TYPE = ModeSelectorCardTypes.DEFAULT
    _bootcamp = dependency.descriptor(IBootcampController)
    _uiSpamController = dependency.descriptor(IUISpamController)

    def __init__(self):
        super(ModeSelectorItem, self).__init__()
        self._initialized = False
        viewModelClass = self._VIEW_MODEL
        if viewModelClass is None:
            raise SoftException('_VIEW_MODEL is missing!')
        self._viewModel = viewModelClass()
        self._preferredColumn = DEFAULT_COLUMN
        self._priority = DEFAULT_PRIORITY
        return

    @property
    def viewModel(self):
        return self._viewModel

    @property
    @abstractmethod
    def modeName(self):
        raise NotImplementedError

    @property
    def preferredColumn(self):
        return self._preferredColumn

    @property
    def priority(self):
        return self._priority

    @property
    def isSelectable(self):
        return False

    @property
    def isVisible(self):
        return True

    @property
    def disabledTooltipText(self):
        return backport.text(R.strings.tooltips.mode_selector.unavailable.bootcamp()) if self._bootcamp.isInBootcamp() else self._getDisabledTooltipText()

    def getFactory(self):

        def factory():
            return self.__class__()

        return factory

    def handleClick(self):
        pass

    def initialize(self):
        if self._initialized:
            return
        self._onInitializing()
        self._initialized = True

    def dispose(self):
        if not self._initialized:
            return
        else:
            self._onDisposing()
            self._viewModel = None
            self._initialized = False
            return

    def checkHeaderNavigation(self):
        return True

    def handleInfoPageClick(self):
        url = self._urlProcessing(GUI_SETTINGS.lookup(getInfoPageKey(self.modeName)))
        showBrowserOverlayView(url, VIEW_ALIAS.WEB_VIEW_TRANSPARENT, hiddenLayers=(WindowLayer.MARKER, WindowLayer.VIEW, WindowLayer.WINDOW))

    def _onInitializing(self):
        self.viewModel.setIsDisabled(self._isDisabled())
        self.viewModel.setIsNew(self._isNewLabelVisible())
        self.viewModel.setIsInfoIconVisible(self._isInfoIconVisible())
        self.viewModel.setModeName(self.modeName)
        self.viewModel.setType(self._CARD_VISUAL_TYPE)

    def _isInfoIconVisible(self):
        return GUI_SETTINGS.lookup(getInfoPageKey(self.modeName)) is not None

    def _isNewLabelVisible(self):
        isInBootcamp = self._bootcamp.isInBootcamp()
        isNewbie = self._uiSpamController.shouldBeHidden('ModeSelectorWidgetsBtnHint')
        return self._getIsNew() and not isInBootcamp and not isNewbie

    def _isDisabled(self):
        return self._getIsDisabled() or self._bootcamp.isInBootcamp()

    def _onDisposing(self):
        pass

    def _getDisabledTooltipText(self):
        return backport.text(R.strings.tooltips.mode_selector.unavailable.techProblems())

    def _getIsDisabled(self):
        return False

    def _getIsNew(self):
        return False

    def _getPositionByModeName(self):
        return COLUMN_SETTINGS.get(self.modeName, (DEFAULT_COLUMN, DEFAULT_PRIORITY))

    def _urlProcessing(self, url):
        return url


class ModeSelectorNormalCardItem(ModeSelectorItem):
    __slots__ = ('onCardChange',)
    _VIEW_MODEL = ModeSelectorNormalCardModel

    def __init__(self):
        super(ModeSelectorNormalCardItem, self).__init__()
        self.onCardChange = Event.Event()

    @property
    def modeName(self):
        return CustomModeName.DEFAULT

    @property
    def calendarTooltipText(self):
        pass

    @property
    def viewModel(self):
        return super(ModeSelectorNormalCardItem, self).viewModel

    @property
    def hasExtendedCalendarTooltip(self):
        return False

    def getExtendedCalendarTooltip(self, parentWindow):
        return []

    def _isNeedToHideCard(self):
        return False

    def _onInitializing(self):
        super(ModeSelectorNormalCardItem, self)._onInitializing()
        modeName = self.modeName
        if R.images.gui.maps.icons.mode_selector.mode.dyn(modeName).isValid():
            self.viewModel.setResourcesFolderName(modeName)
        self._preferredColumn, self._priority = self._getPositionByModeName()
        modeStrings = _rMode.dyn(modeName)
        if modeStrings.isValid():
            condition = modeStrings.dyn('condition')
            self.viewModel.setConditions(backport.text(condition()) if condition.exists() else '')
            description = modeStrings.dyn('description')
            self.viewModel.setDescription(backport.text(description()) if description.exists() else '')
            callToAction = modeStrings.dyn('callToAction')
            self.viewModel.setStatusActive(backport.text(callToAction()) if callToAction.exists() else '')

    def _addReward(self, rewardID, locParams=None, **params):
        if locParams is None:
            locParams = {}
        rewardIDValue = rewardID.value
        item = ModeSelectorRewardModel()
        item.setIconName(rewardIDValue)
        rReward = R.strings.mode_selector.reward.dyn(rewardIDValue)
        item.setName(rReward.name())
        item.setDescription(backport.text(rReward.description(), **locParams))
        item.setTooltipID(params.get('tooltipID', ''))
        if rewardID == ModeSelectorRewardID.VEHICLE:
            item.setVehicleLevel(params.get('level', ''))
            item.setVehicleType(params.get('type', ''))
        self.viewModel.getRewardList().addViewModel(item)
        return

    def _onDisposing(self):
        self.onCardChange.clear()
        self.onCardChange = None
        super(ModeSelectorNormalCardItem, self)._onDisposing()
        return


class ModeSelectorLegacyItem(ModeSelectorNormalCardItem):
    __slots__ = ('_legacySelectorItem',)

    def __init__(self, oldSelectorItem):
        super(ModeSelectorLegacyItem, self).__init__()
        self._legacySelectorItem = oldSelectorItem

    @property
    def modeName(self):
        return self._legacySelectorItem.getData()

    @property
    def isSelectable(self):
        return True

    @property
    def isVisible(self):
        return self._legacySelectorItem.isVisible()

    def getFactory(self):

        def factory():
            return self.__class__(self._legacySelectorItem)

        return factory

    def _getIsNew(self):
        return self._legacySelectorItem.isShowNewIndicator()

    def _getIsDisabled(self):
        return self._legacySelectorItem.isDisabled()

    def _onInitializing(self):
        super(ModeSelectorLegacyItem, self)._onInitializing()
        self.viewModel.setName(i18n.makeString(self._legacySelectorItem.getLabel()))
        self.viewModel.setPriority(self._legacySelectorItem.getOrder())
