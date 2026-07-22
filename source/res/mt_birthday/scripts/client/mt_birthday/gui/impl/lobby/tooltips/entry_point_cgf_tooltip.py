# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/lobby/tooltips/entry_point_cgf_tooltip.py
from gui.impl.gen import R
from frameworks.wulf import ViewSettings
from helpers import dependency
from mt_birthday.gui.impl.gen.view_models.views.lobby.tooltips.entry_point_cgf_tooltip_model import EntryPointCgfTooltipModel
from gui.impl.pub import ViewImpl
from mt_birthday.skeletons.mt_birthday_controller import ITanksBirthdayController

class EntryPointCgfTooltip(ViewImpl):
    __tankBirthdayController = dependency.descriptor(ITanksBirthdayController)
    __slots__ = ('__objectName',)

    def __init__(self, objectName):
        settings = ViewSettings(R.views.mt_birthday.lobby.tooltips.EntryPointCgfTooltip(), model=EntryPointCgfTooltipModel())
        self.__objectName = objectName
        super(EntryPointCgfTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EntryPointCgfTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(EntryPointCgfTooltip, self)._onLoading()
        self.viewModel.setCgfEntryPoint(self.__objectName)
        self.viewModel.setIsPaused(self.__tankBirthdayController.isPaused())
