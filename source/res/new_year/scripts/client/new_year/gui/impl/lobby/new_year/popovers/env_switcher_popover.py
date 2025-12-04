# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/popovers/env_switcher_popover.py
from new_year.gui.impl.lobby.new_year.tooltips.ny_common_tooltip import NyCommonTooltip, getCommonTooltipArgsFromEvent
from new_year.gui.impl.gen.view_models.views.lobby.new_year.popovers.env_switcher_popover_model import EnvSwitcherPopoverModel
from new_year.skeletons.new_year import INewYearEnvironmentSwitchController
from frameworks.wulf import ViewSettings
from gui.impl.pub import PopOverViewImpl
from helpers import dependency
from gui.impl.gen import R

class EnvSwitcherPopover(PopOverViewImpl):
    __slots__ = ('__isInHangar',)
    __nyEnvSwitcherController = dependency.descriptor(INewYearEnvironmentSwitchController)

    def __init__(self, isInHangar):
        settings = ViewSettings(layoutID=R.views.new_year.lobby.new_year.popovers.EnvSwitcherPopover(), model=EnvSwitcherPopoverModel())
        self.__isInHangar = isInHangar
        super(EnvSwitcherPopover, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EnvSwitcherPopover, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return NyCommonTooltip(*getCommonTooltipArgsFromEvent(event)) if contentID == R.views.new_year.lobby.new_year.tooltips.CommonTooltip() else super(EnvSwitcherPopover, self).createToolTipContent(event, contentID)

    def _getEvents(self):
        return ((self.viewModel.switcherComponent.onSwitch, self.__onSwitchState), (self.__nyEnvSwitcherController.onEnvironmentSwitched, self.__updateEnvironmentSwitcher))

    def _onLoading(self, *args, **kwargs):
        super(EnvSwitcherPopover, self)._onLoading(*args, **kwargs)
        self.viewModel.setIsInHangar(self.__isInHangar)
        self.__updateEnvironmentSwitcher()

    def __onSwitchState(self, args):
        env = args.values()[0]
        self.__nyEnvSwitcherController.switchDayNightMode(env)
        self.__nyEnvSwitcherController.notifyTipShouldClose()

    def __updateEnvironmentSwitcher(self):
        with self.viewModel.switcherComponent.transaction() as tx:
            tx.setState(self.__nyEnvSwitcherController.userEnvState)
            tx.setMode(self.__nyEnvSwitcherController.currentDayNightMode)
            tx.setArrowDegree(self.__nyEnvSwitcherController.getTimeAngle())
