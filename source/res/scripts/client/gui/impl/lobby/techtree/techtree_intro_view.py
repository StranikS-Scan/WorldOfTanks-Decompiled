# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/techtree/techtree_intro_view.py
from urlparse import urlparse
from collections import defaultdict
import nations
from account_helpers.settings_core.settings_constants import GuiSettingsBehavior
from helpers import dependency
from account_helpers import AccountSettings
from account_helpers.AccountSettings import GUI_START_BEHAVIOR
from blueprints.BlueprintTypes import BlueprintTypes
from blueprints.FragmentTypes import getFragmentType
from gui import GUI_SETTINGS, GUI_NATIONS
from gui.impl.pub import ViewImpl, WindowImpl
from frameworks.wulf import ViewFlags, WindowFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.backport import backport_system_locale
from gui.impl.gen.view_models.views.lobby.techtree.techtree_intro_view_model import TechtreeIntroViewModel
from gui.impl.gen.view_models.views.lobby.blueprints.fragment_item_model import FragmentItemModel
from gui.shared import g_eventBus, events
from gui.shared.utils.requesters.blueprints_requester import getNationalFragmentCD, getFragmentNationID
from skeletons.account_helpers.settings_core import ISettingsCore
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.Waiting import Waiting

class TechTreeIntroView(ViewImpl):
    __settingsCore = dependency.descriptor(ISettingsCore)
    __slots__ = ('__nationalBlueprints', '__universalBlueprints')

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.techtree.TechTreeIntro())
        settings.model = TechtreeIntroViewModel()
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.args = args
        settings.kwargs = kwargs
        super(TechTreeIntroView, self).__init__(settings)
        self.__nationalBlueprints = defaultdict(int)
        self.__universalBlueprints = 0

    @property
    def viewModel(self):
        return super(TechTreeIntroView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            fragmentCD = int(event.getArgument('fragmentCD'))
            args = [fragmentCD]
            if tooltipId in (TOOLTIPS_CONSTANTS.BLUEPRINT_FRAGMENT_INFO, TOOLTIPS_CONSTANTS.BLUEPRINT_INFO):
                window = BackportTooltipWindow(createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=args), self.getParentWindow())
                window.load()
                return window
        return super(TechTreeIntroView, self).createToolTip(event)

    def _initialize(self, *args, **kwargs):
        super(TechTreeIntroView, self)._initialize(args, kwargs)
        self.viewModel.onAcceptBtnClick += self.__onAcceptBtnClick
        self.viewModel.onLinkClick += self.__onLinkClick

    def _finalize(self):
        self.viewModel.onAcceptBtnClick -= self.__onAcceptBtnClick
        self.viewModel.onLinkClick -= self.__onLinkClick
        super(TechTreeIntroView, self)._finalize()

    def _onLoading(self, *args, **kwargs):
        Waiting.show('loadPage')
        super(TechTreeIntroView, self)._onLoading(*args, **kwargs)
        self.__proccesRawBlueprints(kwargs.get('convertedBlueprints', {}))
        with self.viewModel.transaction() as tx:
            tx.setLinkLabel(self.__getLinkLabel())
            blueprintModels = tx.getBlueprints()
            if self.__universalBlueprints > 0:
                blueprintModels.addViewModel(self.__getModelForUniversalFragment(self.__universalBlueprints))
            for nationName in GUI_NATIONS:
                if self.__nationalBlueprints[nationName] > 0:
                    blueprintModels.addViewModel(self.__getModelForNationalFragment(nationName, self.__nationalBlueprints[nationName]))

            blueprintModels.invalidate()

    def _onLoaded(self, *args, **kwargs):
        super(TechTreeIntroView, self)._onLoaded(*args, **kwargs)
        Waiting.hide('loadPage')
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        settings = self.__settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
        settings[GuiSettingsBehavior.TECHTREE_INTRO_SHOWED] = True
        self.__settingsCore.serverSettings.setSectionSettings(GUI_START_BEHAVIOR, settings)

    def __onAcceptBtnClick(self):
        self.destroyWindow()

    def __onLinkClick(self):
        g_eventBus.handleEvent(events.OpenLinkEvent(events.OpenLinkEvent.TECHTREE_UPDATE_NEWS))

    def __proccesRawBlueprints(self, blueprintsRaw):
        for blueprintCD in blueprintsRaw:
            fragmentType = getFragmentType(blueprintCD)
            if fragmentType == BlueprintTypes.INTELLIGENCE_DATA:
                self.__universalBlueprints += blueprintsRaw[blueprintCD]
            if fragmentType == BlueprintTypes.NATIONAL:
                nationID = getFragmentNationID(blueprintCD)
                nationName = nations.MAP.get(nationID, nations.NONE_INDEX)
                self.__nationalBlueprints[nationName] += blueprintsRaw[blueprintCD]

    def __getModelForNationalFragment(self, nationName, value):
        item = FragmentItemModel()
        item.setFragmentCD(getNationalFragmentCD(nations.INDICES[nationName]))
        item.setValue(backport_system_locale.getIntegralFormat(value))
        item.setIcon(R.images.gui.maps.icons.blueprints.fragment.medium.dyn(nationName)())
        item.setSpecialIcon(R.images.gui.maps.icons.blueprints.fragment.big.dyn(nationName)())
        return item

    def __getModelForUniversalFragment(self, value):
        item = FragmentItemModel()
        item.setFragmentCD(BlueprintTypes.INTELLIGENCE_DATA)
        item.setValue(backport_system_locale.getIntegralFormat(value))
        item.setIcon(R.images.gui.maps.icons.blueprints.fragment.medium.intelligence())
        item.setSpecialIcon(R.images.gui.maps.icons.blueprints.fragment.big.intelligence())
        return item

    def __getLinkLabel(self):
        url = GUI_SETTINGS.techTreeUpdateNewsURL
        return urlparse(url).netloc if url else ''


class TechTreeIntroWindow(WindowImpl):

    def __init__(self, convertedBlueprints, parent=None):
        super(TechTreeIntroWindow, self).__init__(wndFlags=WindowFlags.WINDOW, parent=parent, content=TechTreeIntroView(convertedBlueprints=convertedBlueprints))
