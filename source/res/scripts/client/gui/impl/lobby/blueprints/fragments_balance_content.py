# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/blueprints/fragments_balance_content.py
import logging
import nations
from blueprints.BlueprintTypes import BlueprintTypes
from frameworks.wulf import ViewSettings
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.gen import R
from gui.impl.gen.view_models.views.common_balance_content_model import CommonBalanceContentModel
from gui.impl.gen.view_models.views.lobby.blueprints.fragment_item_model import FragmentItemModel
from gui.impl.gen.view_models.views.lobby.blueprints.blueprint_screen_tooltips import BlueprintScreenTooltips
from gui.impl.pub import ViewImpl
from gui.impl.backport import createTooltipData, BackportTooltipWindow
from gui.shared.utils.requesters.blueprints_requester import getNationalFragmentCD
from helpers import dependency
from skeletons.gui.shared import IItemsCache
logger = logging.getLogger(__name__)

class FragmentsBalanceContent(ViewImpl):
    __itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__vehicle',)

    def __init__(self, vehicleCD):
        settings = ViewSettings(R.views.lobby.blueprints.fragments_balance_content.FragmentsBalanceContent())
        settings.model = CommonBalanceContentModel()
        super(FragmentsBalanceContent, self).__init__(settings)
        self.__vehicle = self.__itemsCache.items.getItemByCD(vehicleCD)

    @property
    def viewModel(self):
        return super(FragmentsBalanceContent, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            fragmentCD = int(event.getArgument('fragmentCD'))
            tooltipData = self.__getTooltipData(tooltipId, fragmentCD)
            if tooltipData is None:
                return
            window = BackportTooltipWindow(tooltipData, self.getParentWindow())
            if window is not None:
                window.load()
            return window
        else:
            return super(FragmentsBalanceContent, self).createToolTip(event)

    def _initialize(self, *args, **kwargs):
        super(FragmentsBalanceContent, self)._initialize(*args, **kwargs)
        intelligenceFragments, nationalFragments = self.__getFragmentCount()
        nationName = self.__vehicle.nationName if self.__vehicle is not None else ''
        if not nationName:
            logger.warning('Can not get a vehicle object and nation name')
        g_clientUpdateManager.addCallbacks({'blueprints': self.__onUpdateBlueprints})
        with self.viewModel.transaction() as model:
            item = FragmentItemModel()
            item.setValue(self.gui.systemLocale.getNumberFormat(intelligenceFragments))
            item.setIcon(R.images.gui.maps.icons.blueprints.fragment.small.intelligence())
            item.setFragmentCD(BlueprintTypes.INTELLIGENCE_DATA)
            model.currency.addViewModel(item)
            item = FragmentItemModel()
            item.setValue(self.gui.systemLocale.getNumberFormat(nationalFragments))
            item.setIcon(R.images.gui.maps.icons.blueprints.fragment.small.dyn(nationName)())
            nationId = nations.INDICES.get(nationName, nations.NONE_INDEX)
            nationTooltipData = getNationalFragmentCD(nationId)
            item.setFragmentCD(nationTooltipData)
            model.currency.addViewModel(item)
            model.currency.invalidate()
        return

    def _finalize(self):
        self.__vehicle = None
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(FragmentsBalanceContent, self)._finalize()
        return

    def __onUpdateBlueprints(self, _):
        self.__updateModel()

    def __updateModel(self):
        intelligenceFragments, nationalFragments = self.__getFragmentCount()
        with self.viewModel.transaction() as model:
            intelItem = model.currency.getItem(0)
            intelItem.setValue(self.gui.systemLocale.getNumberFormat(intelligenceFragments))
            nationalItem = model.currency.getItem(1)
            nationalItem.setValue(self.gui.systemLocale.getNumberFormat(nationalFragments))
            model.currency.invalidate()

    def __getFragmentCount(self):
        nationFragmentCount = 0
        if self.__vehicle is None:
            logger.warning('Can not get a vehicle compact descriptor')
        else:
            nationFragmentCount = self.__itemsCache.items.blueprints.getNationalFragments(self.__vehicle.intCD)
        intelligenceFragmentCount = self.__itemsCache.items.blueprints.getIntelligenceData()
        return (intelligenceFragmentCount, nationFragmentCount)

    def __getTooltipData(self, ttId, fragmentCD):
        return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BLUEPRINT_FRAGMENT_INFO, specialArgs=[fragmentCD]) if ttId == BlueprintScreenTooltips.TOOLTIP_BLUEPRINT else None
