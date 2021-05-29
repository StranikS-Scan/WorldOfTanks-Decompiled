# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mode_selector/items/base_item.py
from abc import ABCMeta, abstractmethod
import typing
from gui import GUI_SETTINGS
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_card_types import ModeSelectorCardTypes
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_normal_card_model import ModeSelectorNormalCardModel
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_reward_model import ModeSelectorRewardModel
from gui.impl.lobby.mode_selector.items.constants import CustomModeName, COLUMN_SETTINGS, DEFAULT_PRIORITY, DEFAULT_COLUMN, ModeSelectorRewardID
from helpers import dependency, i18n
from skeletons.gui.game_control import IBootcampController
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from typing import Callable, Optional, Type, Union
    from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_card_model import ModeSelectorCardModel
    from gui.Scaleform.daapi.view.lobby.header.battle_selector_items import _SelectorItem
    from gui.impl.gen_utils import DynAccessor
_rMode = R.strings.mode_selector.mode
_INFO_PAGE_KEY_TEMPLATE = 'infoPage%s'

class ModeSelectorItem(object):
    __metaclass__ = ABCMeta
    __slots__ = ('_viewModel', '_initialized', '_infoPageKey', '_priority', '_preferredColumn')
    _VIEW_MODEL = None
    _CARD_VISUAL_TYPE = ModeSelectorCardTypes.DEFAULT
    _bootcamp = dependency.descriptor(IBootcampController)

    def __init__(self):
        super(ModeSelectorItem, self).__init__()
        self._initialized = False
        viewModelClass = self._VIEW_MODEL
        if viewModelClass is None:
            raise SoftException('_VIEW_MODEL is missing!')
        self._viewModel = viewModelClass()
        self._infoPageKey = None
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
            if self._viewModel is not None:
                self._viewModel.unbind()
                self._viewModel = None
            self._initialized = False
            return

    @property
    def infoPageKey(self):
        return self._infoPageKey

    def _onInitializing(self):
        isInBootcamp = self._bootcamp.isInBootcamp()
        self.viewModel.setIsDisabled(self._getIsDisabled() or isInBootcamp)
        self.viewModel.setIsNew(self._getIsNew() and not isInBootcamp)
        modeName = self.modeName
        self._infoPageKey = _INFO_PAGE_KEY_TEMPLATE % (modeName[0].upper() + modeName[1:])
        self.viewModel.setIsInfoIconVisible(GUI_SETTINGS.lookup(self._infoPageKey) is not None)
        self.viewModel.setModeName(modeName)
        self.viewModel.setType(self._CARD_VISUAL_TYPE)
        return

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


class ModeSelectorNormalCardItem(ModeSelectorItem):
    _VIEW_MODEL = ModeSelectorNormalCardModel

    @property
    def modeName(self):
        return CustomModeName.DEFAULT

    @property
    def calendarTooltipText(self):
        pass

    @property
    def viewModel(self):
        return super(ModeSelectorNormalCardItem, self).viewModel

    def _onInitializing(self):
        super(ModeSelectorNormalCardItem, self)._onInitializing()
        modeName = self.modeName
        if R.images.gui.maps.icons.mode_selector.mode.dyn(modeName).isValid():
            self.viewModel.setResourcesFolderName(modeName)
        self._preferredColumn, self._priority = self._getPositionByModeName()
        modeStrings = _rMode.dyn(modeName)
        if modeStrings.isValid():
            self.viewModel.setConditions(backport.text(modeStrings.dyn('condition')()))
            self.viewModel.setDescription(backport.text(modeStrings.dyn('description')()))

    def _addReward(self, rewardID, locParams=None, **params):
        if locParams is None:
            locParams = {}
        rewardIDValue = rewardID.value
        item = ModeSelectorRewardModel()
        item.setIconName(rewardIDValue)
        rReward = R.strings.mode_selector.reward.dyn(rewardIDValue)
        item.setName(rReward.name())
        item.setDescription(backport.text(rReward.description(), **locParams))
        if rewardID == ModeSelectorRewardID.VEHICLE:
            item.setVehicleLevel(params.get('level', ''))
            item.setVehicleType(params.get('type', ''))
        self.viewModel.getRewardList().addViewModel(item)
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
