# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/new_year_extra_slot_level_up_view.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NY_EXTRA_SLOT_LAST_LEVEL_SHOWN
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_extra_slot_level_up_view_model import NewYearExtraSlotLevelUpViewModel
from gui.impl.pub import ViewImpl, WindowImpl
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency
from ny_common.VehBranchConfig import BRANCH_SLOT_TYPE
from shared_utils import findFirst
from skeletons.new_year import INewYearController

class NewYearExtraSlotLevelUpView(ViewImpl):
    __slots__ = ('__maxLevel',)
    __nyController = dependency.descriptor(INewYearController)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.model = NewYearExtraSlotLevelUpViewModel()
        super(NewYearExtraSlotLevelUpView, self).__init__(settings)
        self.__maxLevel = None
        return

    @property
    def viewModel(self):
        return super(NewYearExtraSlotLevelUpView, self).getViewModel()

    def _onLoading(self):
        super(NewYearExtraSlotLevelUpView, self)._onLoading()
        slot = findFirst(lambda s: s.getSlotType() == BRANCH_SLOT_TYPE.EXTRA, self.__nyController.getVehicleBranch().getVehicleSlots())
        allLevels = slot.getVehicleLevelsRange()
        minLevel = min(allLevels)
        self.__maxLevel = max(allLevels)
        with self.viewModel.transaction() as vm:
            vm.setMinLevel(minLevel)
            vm.setMaxLevel(self.__maxLevel)

    def _onLoaded(self, *args, **kwargs):
        self.getParentWindow().bringToFront()
        AccountSettings.setUIFlag(NY_EXTRA_SLOT_LAST_LEVEL_SHOWN, self.__maxLevel)


class NewYearExtraSlotLevelUpWindow(WindowImpl):
    __slots__ = ('__blur',)

    def __init__(self, parent=None):
        super(NewYearExtraSlotLevelUpWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=NewYearExtraSlotLevelUpView(R.views.lobby.new_year.ExtraSlotLevelUpView()), parent=parent, layer=WindowLayer.OVERLAY)
        self.__blur = CachedBlur(enabled=True, ownLayer=self.layer, blurAnimRepeatCount=4)

    def _finalize(self):
        self.__blur.fini()
        super(NewYearExtraSlotLevelUpWindow, self)._finalize()
