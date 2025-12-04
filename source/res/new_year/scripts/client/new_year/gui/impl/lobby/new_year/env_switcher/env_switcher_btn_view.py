# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/env_switcher/env_switcher_btn_view.py
from new_year.gui.impl.lobby.new_year.tooltips.ny_common_tooltip import NyCommonTooltip, getCommonTooltipArgsFromEvent
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.env_switcher_btn_view_model import EnvSwitcherBtnViewModel
from new_year.gui.impl.lobby.new_year.popovers.env_switcher_popover import EnvSwitcherPopover
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from new_year.skeletons.new_year import INewYearEnvironmentSwitchController
from frameworks.wulf import ViewFlags, ViewSettings, WindowLayer
from gui.impl.pub import ViewImpl, PopOverWindow
from helpers import dependency
from gui.impl.gen import R

class EnvSwitcherBtnInject(InjectComponentAdaptor):

    def _makeInjectView(self):
        return EnvSwitcherBtnView()


class EnvSwitcherBtnView(ViewImpl):
    __nyEnvSwitcherController = dependency.descriptor(INewYearEnvironmentSwitchController)

    def __init__(self):
        settings = ViewSettings(layoutID=R.views.new_year.lobby.new_year.EnvSwitcherBtnView(), flags=ViewFlags.VIEW, model=EnvSwitcherBtnViewModel())
        super(EnvSwitcherBtnView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EnvSwitcherBtnView, self).getViewModel()

    def createPopOver(self, event):
        if event.contentID == R.views.new_year.lobby.new_year.popovers.EnvSwitcherPopover():
            self.__nyEnvSwitcherController.notifyTipShouldClose()
            content = EnvSwitcherPopover(isInHangar=True)
            window = PopOverWindow(event, content, self.getParentWindow(), WindowLayer.TOP_WINDOW)
            window.load()
            return window
        return super(EnvSwitcherBtnView, self).createPopOver(event)

    def createToolTipContent(self, event, contentID):
        return NyCommonTooltip(*getCommonTooltipArgsFromEvent(event)) if contentID == R.views.new_year.lobby.new_year.tooltips.CommonTooltip() else super(EnvSwitcherBtnView, self).createToolTipContent(event, contentID)
