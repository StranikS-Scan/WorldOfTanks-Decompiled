# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/dialogs/challenge/challenge_discount.py
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from gui import SystemMessages
from gui.SystemMessages import SM_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.dialogs.challenge.sub_views.challenge_discount_model import ChallengeDiscountModel
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.utils import decorators
from new_year.ny_processor import ApplyVehicleDiscountProcessor

class ChallengeDiscount(SubModelPresenter):
    __slots__ = ('__kwargs', '__vehicle', '__discountValue')

    def __init__(self, viewModel, parentView):
        super(ChallengeDiscount, self).__init__(viewModel, parentView)
        self.__kwargs = {}
        self.__vehicle = None
        self.__discountValue = None
        return

    @property
    def layoutID(self):
        return R.views.lobby.new_year.dialogs.challenge.sub_views.ChallengeDiscount()

    @property
    def viewModel(self):
        return self.getViewModel()

    def initialize(self, vehicle, discountValue, *args, **kwargs):
        super(ChallengeDiscount, self).initialize(args, kwargs)
        self.__vehicle = vehicle
        self.__discountValue = discountValue
        self.__kwargs = kwargs
        with self.viewModel.transaction() as tx:
            tx.vehicleInfo.setIsElite(vehicle.isElite)
            tx.vehicleInfo.setVehicleName(vehicle.shortUserName)
            tx.vehicleInfo.setVehicleType(vehicle.type)
            tx.setDiscountInPercent(discountValue)

    def _getEvents(self):
        events = super(ChallengeDiscount, self)._getEvents()
        return events + ((self.viewModel.onAccept, self.__onAccept), (self.viewModel.onCancel, self.parentView.onCancel))

    @decorators.adisp_process('newYear/applyVehicleDiscount')
    def __onAccept(self):
        self.parentView.onRequestProcessChange(True)
        result = yield ApplyVehicleDiscountProcessor(**self.__kwargs).request()
        if result.success:
            if self.__vehicle is not None and self.__discountValue is not None:
                SystemMessages.pushMessage(backport.text(R.strings.system_messages.newYear.applyVehicleDiscount.success(), discount=self.__discountValue, vehName=self.__vehicle.userName), priority=NotificationPriorityLevel.MEDIUM, type=result.sysMsgType)
            self.parentView.onAccept()
        elif result.userMsg:
            clientErrKey = result.auxData.get('clientErrKey')
            if not clientErrKey:
                clientErrKey = 'server'
            errorStr = backport.text(R.strings.ny.challenge.dialogs.discount.err.dyn(clientErrKey)())
            SystemMessages.pushMessage(result.userMsg, priority=NotificationPriorityLevel.MEDIUM, type=SM_TYPE.Error)
            self.viewModel.setErrorMessage(errorStr)
        self.parentView.onRequestProcessChange(False)
        return
