# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/lobby/banner/birthday_banner_view.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from helpers import dependency
from mt_birthday.gui.impl.gen.view_models.views.lobby.banner.birthday_banner_view_model import BirthdayBannerViewModel, StatusEnum
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from mt_birthday.gui.shared.event_dispatcher import showMainView
from mt_birthday.skeletons.mt_birthday_controller import ITanksBirthdayController

class BirthdayBannerView(ViewImpl):
    __tankBirthdayController = dependency.descriptor(ITanksBirthdayController)
    __slots__ = ('__isSingle',)

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.mt_birthday.lobby.banner.BirthdayBannerView())
        settings.flags = flags
        settings.model = BirthdayBannerViewModel()
        super(BirthdayBannerView, self).__init__(settings)
        self.__isSingle = True

    def _onLoading(self, *args, **kwargs):
        super(BirthdayBannerView, self)._onLoading(*args, **kwargs)
        self.__updateViewModel()

    def _getEvents(self):
        return ((self.viewModel.toBirthdayEvent, self.__onClick), (self.__tankBirthdayController.onEventSettingsUpdated, self.__onUpdate))

    def __onUpdate(self):
        self.__updateViewModel()

    @property
    def viewModel(self):
        return super(BirthdayBannerView, self).getViewModel()

    def setIsSingle(self, value):
        self.__isSingle = value
        self.__updateViewModel()

    def __onClick(self):
        if self.__tankBirthdayController.isEnabled():
            showMainView()

    def __getStatus(self):
        if self.__tankBirthdayController.isEnding():
            return StatusEnum.ENDING
        if self.__tankBirthdayController.isEnabled():
            return StatusEnum.ACTIVE
        return StatusEnum.DISABLED if self.__tankBirthdayController.isPaused() else None

    def __updateViewModel(self):
        if not self.__tankBirthdayController.isDisabled():
            with self.viewModel.transaction() as tx:
                tx.setIsAloneBanner(self.__isSingle)
                tx.setTimer(self.__tankBirthdayController.getLocalEndDate())
                tx.setStatus(self.__getStatus())
        else:
            self.destroy()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(BirthdayBannerView, self).createToolTip(event)
