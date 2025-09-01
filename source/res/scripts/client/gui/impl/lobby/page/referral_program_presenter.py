# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/page/referral_program_presenter.py
from __future__ import absolute_import
from gui.impl.gen.view_models.views.lobby.page.footer.referral_program_model import ReferralProgramModel
from gui.impl.pub.view_component import ViewComponent
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from gui.shared.events import ReferralProgramEvent
from helpers import dependency
from skeletons.gui.game_control import IReferralProgramController

class ReferralProgramPresenter(ViewComponent[ReferralProgramModel]):
    __referralCtrl = dependency.descriptor(IReferralProgramController)

    def __init__(self):
        super(ReferralProgramPresenter, self).__init__(model=ReferralProgramModel)

    @property
    def viewModel(self):
        return super(ReferralProgramPresenter, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ReferralProgramPresenter, self)._onLoading(*args, **kwargs)
        self.__updateModel()

    def _getEvents(self):
        return ((self.__referralCtrl.onReferralStateChanged, self.__onReferralStateChanged), (self.__referralCtrl.onReferralProgramUpdated, self.__updateModel), (self.viewModel.onClick, self.__onClick))

    def __onReferralStateChanged(self):
        self.viewModel.setEnabled(self.__referralCtrl.isEnabled)

    def __onClick(self):
        g_eventBus.handleEvent(ReferralProgramEvent(ReferralProgramEvent.SHOW_REFERRAL_PROGRAM_WINDOW), scope=EVENT_BUS_SCOPE.LOBBY)

    def __updateModel(self, *_):
        with self.viewModel.transaction() as model:
            model.setFirstIndication(self.__referralCtrl.isFirstIndication())
            model.setNewReferralSeason(self.__referralCtrl.isNewReferralSeason)
            model.setBubbleCount(self.__referralCtrl.getBubbleCount())
            model.setEnabled(self.__referralCtrl.isEnabled)
