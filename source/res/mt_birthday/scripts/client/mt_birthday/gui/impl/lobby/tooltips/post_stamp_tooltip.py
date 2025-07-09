# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/lobby/tooltips/post_stamp_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from helpers import dependency
from mt_birthday.gui.impl.gen.view_models.views.lobby.tooltips.post_stamp_tooltip_model import PostStampTooltipModel
from gui.impl.pub import ViewImpl
from mt_birthday.skeletons.mt_birthday_controller import ITanksBirthdayController

class PostStampTooltip(ViewImpl):
    __tankBirthdayController = dependency.descriptor(ITanksBirthdayController)
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.mt_birthday.lobby.tooltips.PostStampTooltip(), model=PostStampTooltipModel())
        super(PostStampTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(PostStampTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as vm:
            vm.setCurrencyCount(self.__tankBirthdayController.getStampCount())
