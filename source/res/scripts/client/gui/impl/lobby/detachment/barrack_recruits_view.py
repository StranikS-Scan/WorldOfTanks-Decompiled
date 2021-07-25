# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/barrack_recruits_view.py
import logging
import nations
from crew2 import settings_globals
from gui.impl.lobby.detachment.navigation_view_settings import NavigationViewSettings
from gui.impl.lobby.detachment.tooltips.mobilization_tooltip import MobilizationTooltip
from gui.shared import event_dispatcher
from items import ITEM_TYPES
from sound_constants import BARRACKS_SOUND_SPACE
from async import async, await
from gui.impl.backport import BackportContextMenuWindow
from gui.impl.lobby.detachment.context_menu.context_menu_helper import getContextMenuData
from frameworks.wulf import ViewFlags, ViewSettings
from gui import GUI_NATIONS_ORDER_INDEX, SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.auxiliary.detachment_helper import fillRecruitModel
from gui.impl.dialogs import dialogs
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.barrack_recruits_view_model import BarrackRecruitsViewModel
from gui.impl.gen.view_models.views.lobby.detachment.common.filter_status_model import FilterStatusModel
from gui.impl.gen.view_models.views.lobby.detachment.common.recruit_model import RecruitModel
from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel
from gui.impl.lobby.detachment.list_filter_mixin import FiltersMixin, FilterContext
from gui.impl.lobby.detachment.navigation_view_impl import NavigationViewImpl
from gui.impl.lobby.detachment.popovers import getNationSettings, getRecruitRoleSettings, getVehicleTypeSettings
from gui.impl.lobby.detachment.popovers.filters.recruit_filters import popoverCriteria, defaultRecruitPopoverFilter, defaultRecruitToggleFilter, toggleCriteria, ORDER
from gui.impl.lobby.detachment.popovers.toggle_filter_popover_view import ToggleFilterPopoverViewStatus
from gui.shared.gui_items.Tankman import Tankman, ROLE_NAMES
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER_INDICES, getUserName, VEHICLE_CLASS_NAME_BY_TYPE
from gui.shared.gui_items.processors.tankman import TankmanRestore
from gui.shared.utils import decorators
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.game_control import IRestoreController
from skeletons.gui.shared import IItemsCache
from uilogging.detachment.loggers import DetachmentToggleLogger
from uilogging.detachment.constants import GROUP
_logger = logging.getLogger(__name__)
_SUF_PNG = '.png'
_RECRUIT_DESCR_FORMATTER = '{}, {} {}'
AUTO_SCROLL_DISABLE = -1

class BarrackRecruitsView(FiltersMixin, NavigationViewImpl):
    __slots__ = ('_tankmanCollection', '_ctx')
    _COMMON_SOUND_SPACE = BARRACKS_SOUND_SPACE
    __itemsCache = dependency.descriptor(IItemsCache)
    __restoreController = dependency.descriptor(IRestoreController)
    _defaultPopoverSetter = staticmethod(defaultRecruitPopoverFilter)
    _defaultToggleSetter = staticmethod(defaultRecruitToggleFilter)
    _popoverFilters = defaultRecruitPopoverFilter()
    _toggleFilters = defaultRecruitToggleFilter()
    uiLogger = DetachmentToggleLogger(GROUP.RECRUIT_BARRACKS)

    def __init__(self, layoutID, ctx=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = BarrackRecruitsViewModel()
        super(BarrackRecruitsView, self).__init__(settings, True, ctx=ctx)
        self._tankmanCollection = self.__itemsCache.items.getTankmen(self.__baseCreteria())
        self._ctx = {'currentCount': 0,
         'totalCount': 0}
        self._dismissTankmenIDs = set(self.__itemsCache.items.getTankmen(REQ_CRITERIA.TANKMAN.DISMISSED).iterkeys())
        self.__scrollToID = AUTO_SCROLL_DISABLE

    def createPopOverContent(self, event):
        ToggleFilterPopoverViewStatus.uiLogger.setGroup(self.uiLogger.group)
        return ToggleFilterPopoverViewStatus(R.strings.detachment.toggleFilterPopover.header(), R.strings.detachment.filterStatus.recruit(), FilterStatusModel.DIVIDER, (getVehicleTypeSettings(R.strings.tooltips.filterToggle.specialization.recruit.body()), getNationSettings(R.strings.tooltips.filterToggle.nation.recruit.body()), getRecruitRoleSettings()), self._changePopoverFilterCallback, self._activatePopoverViewCallback, BarrackRecruitsView._popoverFilters, self._ctx, customResetFunc=self._resetPopoverFilters)

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId == TOOLTIPS_CONSTANTS.TANKMAN:
                tmanInvID = int(event.getArgument('tmanInvId'))
                tman = self.__itemsCache.items.getTankman(tmanInvID)
                return backport.createAndLoadBackportTooltipWindow(self.getParentWindow(), isSpecial=True, tooltipId=TOOLTIPS_CONSTANTS.TANKMAN, specialArgs=[tmanInvID, True, tman.vehicleNativeDescr.type.compactDescr])
            if tooltipId == TOOLTIPS_CONSTANTS.TANKMAN_DEMOBILIZED_STATE:
                return backport.createAndLoadBackportTooltipWindow(self.getParentWindow(), isSpecial=True, tooltipId=TOOLTIPS_CONSTANTS.TANKMAN_DEMOBILIZED_STATE, specialArgs=[int(event.getArgument('tmanInvId'))])
        return super(BarrackRecruitsView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        return MobilizationTooltip() if event.contentID == R.views.lobby.detachment.tooltips.MobilizationTooltip() else super(BarrackRecruitsView, self).createToolTipContent(event, contentID)

    def createContextMenu(self, event):
        if event.contentID == R.views.common.BackportContextMenu():
            contextMenuData = getContextMenuData(event, self.__itemsCache)
            if contextMenuData is not None:
                window = BackportContextMenuWindow(contextMenuData, self.getParentWindow())
                window.load()
                return window
        return super(BarrackRecruitsView, self).createContextMenuContent(event)

    @property
    def viewModel(self):
        return super(BarrackRecruitsView, self).getViewModel()

    def _initModel(self, vm):
        super(BarrackRecruitsView, self)._initModel(vm)
        self._initFilters(vm, ORDER, FilterContext.RECRUIT)
        self.__fillViewModel(vm)

    def _addListeners(self):
        super(BarrackRecruitsView, self)._addListeners()
        self._subscribeFilterHandlers(self.viewModel)
        self.viewModel.onRestore += self.__onRestore
        self.viewModel.onMobilize += self.__onMobilize
        self.__restoreController.onTankmenBufferUpdated += self.__updateDemobilizeChanges
        g_clientUpdateManager.addCallbacks({'inventory.{}'.format(ITEM_TYPES.tankman): self.__onClientUpdate})

    def _removeListeners(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self._unsubscribeFilterHandlers(self.viewModel)
        self.viewModel.onRestore -= self.__onRestore
        self.viewModel.onMobilize -= self.__onMobilize
        self.__restoreController.onTankmenBufferUpdated -= self.__updateDemobilizeChanges
        super(BarrackRecruitsView, self)._removeListeners()

    def _fillList(self, model):
        recruits = self.__getRecruits()
        filteredCount = len(recruits)
        model.filtersModel.setCurrent(filteredCount)
        self._ctx['currentCount'] = filteredCount
        config = self.__itemsCache.items.shop.tankmenRestoreConfig
        recruitsListModel = model.recruits
        recruitsListModel.clearItems()
        for tankman in recruits:
            descr = _RECRUIT_DESCR_FORMATTER.format(ROLE_NAMES[tankman.role], VEHICLE_CLASS_NAME_BY_TYPE[tankman.vehicleNativeType], tankman.vehicleNativeDescr.type.shortUserString)
            restoreTime = tankman.dismissedAt + config.billableDuration if tankman.isDismissed else 0
            recruit = RecruitModel()
            fillRecruitModel(recruit, tankman, descr, restoreTime)
            recruitsListModel.addViewModel(recruit)
            if self.__scrollToID != AUTO_SCROLL_DISABLE and self.__scrollToID < tankman.invID:
                self.__scrollToID = tankman.invID

        model.setAutoScrollId(self.__scrollToID)
        self.__scrollToID = AUTO_SCROLL_DISABLE
        recruitsListModel.invalidate()

    def __onClientUpdate(self, *args, **kwargs):
        self._dismissTankmenIDs = set(self.__itemsCache.items.getTankmen(REQ_CRITERIA.TANKMAN.DISMISSED).iterkeys())
        self._tankmanCollection = self.__itemsCache.items.getTankmen(self.__baseCreteria())
        with self.viewModel.transaction() as model:
            self.__fillViewModel(model)

    def __updateDemobilizeChanges(self, *args, **kwargs):
        currentDismissTankmenIDs = set(self.__itemsCache.items.getTankmen(REQ_CRITERIA.TANKMAN.DISMISSED).iterkeys())
        if self._dismissTankmenIDs - currentDismissTankmenIDs:
            self.__onClientUpdate(*args, **kwargs)

    def __fillViewModel(self, model):
        model.setCurrentViewId(BarrackRecruitsViewModel.BARRACK_RECRUIT)
        model.setEndTimeConvert(settings_globals.g_conversion.endConversion)
        model.setMobilizeCount(len(self._tankmanCollection.filter(REQ_CRITERIA.TANKMAN.ACTIVE)))
        totalCount = len(self._tankmanCollection)
        model.filtersModel.setTotal(totalCount)
        self._ctx['totalCount'] = totalCount
        self._fillList(model)

    def __getRecruits(self):
        criteria = popoverCriteria(self._popoverFilters)
        criteria |= toggleCriteria([ f for f, active in self._toggleFilters.iteritems() if active ])
        tankmenCollection = self._tankmanCollection.filter(criteria)
        return sorted(tankmenCollection.itervalues(), key=_tankmanSortingValue)

    def __baseCreteria(self, init=REQ_CRITERIA.TANKMAN.ALL):
        baseCriteria = init
        baseCriteria |= ~REQ_CRITERIA.TANKMAN.NOT_REGULAR
        return baseCriteria

    @async
    def __onRestore(self, args=None):
        if args is None:
            _logger.debug('Incorrect js args. Please fix it')
            return
        else:
            invID = args.get('id')
            tankman = self.__itemsCache.items.getTankman(invID)
            if tankman is None:
                _logger.error('Attempt to dismiss tankman by invalid invID: %r', invID)
                return
            if tankman.isDismissed:
                sdr = yield await(dialogs.showRestoreRecruitDialogView(self.getParentWindow(), invID))
                result, args = sdr.result
                if result:
                    self.__scrollToID = invID
                    self._dismissTankmenIDs.discard(invID)
                    self.__restoreOperation(tankman)
            else:
                _logger.error('Tankman by invID: %r is not dismiss', invID)
            return

    def __onMobilize(self, args=None):
        navigationSettings = NavigationViewSettings(NavigationViewModel.MOBILIZATION, previousViewSettings=self._navigationViewSettings)
        event_dispatcher.showDetachmentMobilizationView(False, navigationViewSettings=navigationSettings)

    @decorators.process('updating')
    def __restoreOperation(self, tankman):
        result = yield TankmanRestore(tankman).request()
        SystemMessages.pushMessages(result)


def _tankmanSortingValue(tankman):
    nationOrder = GUI_NATIONS_ORDER_INDEX[nations.NAMES[tankman.nationID]]
    roleOrder = Tankman.TANKMEN_ROLES_ORDER[tankman.role]
    descr = tankman.descriptor
    xp = descr.totalXP()
    numSkills = len(descr.skills)
    vehTypeOrder = VEHICLE_TYPES_ORDER_INDICES[tankman.vehicleNativeType]
    vehUserName = getUserName(tankman.vehicleNativeDescr.type)
    return (tankman.isDismissed,
     nationOrder,
     roleOrder,
     -xp,
     -numSkills,
     vehTypeOrder,
     vehUserName)
