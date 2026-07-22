# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/lobby/tooltips/entry_point_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from helpers import dependency
from mt_birthday.gui.impl.gen.view_models.views.lobby.tooltips.entry_point_tooltip_model import EntryPointTooltipModel
from gui.impl.pub import ViewImpl
from mt_birthday.gui.birthday_helpers.birthday_model_helpers import fillProgression
from mt_birthday.skeletons.mt_birthday_controller import ITanksBirthdayController

class EntryPointTooltip(ViewImpl):
    __tankBirthdayController = dependency.descriptor(ITanksBirthdayController)
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.mt_birthday.lobby.tooltips.EntryPointTooltip(), model=EntryPointTooltipModel())
        super(EntryPointTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EntryPointTooltip, self).getViewModel()

    def _getEvents(self):
        return ((self.__tankBirthdayController.progression.onProgressionUpdated, self.__fillProgression),)

    def _onLoading(self, *args, **kwargs):
        super(EntryPointTooltip, self)._onLoading()
        self.__fillProgression()
        self.viewModel.setCurrencyCount(self.__tankBirthdayController.getStampCount())
        self.viewModel.setIsPaused(self.__tankBirthdayController.isPaused())

    def __fillProgression(self, *args, **kwargs):
        fillProgression(self.viewModel)
