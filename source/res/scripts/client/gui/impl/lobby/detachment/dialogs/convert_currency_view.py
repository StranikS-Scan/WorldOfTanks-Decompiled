# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/dialogs/convert_currency_view.py
from frameworks.wulf import ViewSettings
from gui.impl.auxiliary.detachment_helper import fillDetachmentShortInfoModel
from gui.impl.gen import R
from gui.impl.gen.view_models.common.format_resource_string_arg_model import FormatResourceStringArgModel
from gui.impl.gen.view_models.views.lobby.detachment.common.vehicle_model import VehicleModel
from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_short_info_model import DetachmentShortInfoModel
from gui.impl.lobby.detachment.dialogs.dialog_view_data import DialogViewData, DialogVehicleViewData, DialogCrewbookViewData, DialogRestoreDetachmentViewData, DialogRestoreRecruitViewData, DialogMatrixEditViewData
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView
from gui.impl.gen.view_models.views.lobby.detachment.dialogs.convert_currency_model import ConvertCurrencyModel
from helpers.dependency import descriptor
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.shared import IItemsCache

class ConvertCurrencyView(FullScreenDialogView):
    __slots__ = ('_ctx', '_viewData', 'viewType')
    _itemsCache = descriptor(IItemsCache)

    def __init__(self, ctx=None):
        self._ctx = ctx
        layout = self._getLayoutID()
        settings = ViewSettings(layout)
        settings.model = ConvertCurrencyModel()
        super(ConvertCurrencyView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ConvertCurrencyView, self).getViewModel()

    def _getLayoutID(self):
        return R.views.lobby.detachment.dialogs.ConvertCurrencyView()

    def _createViewData(self):
        self._viewData = DialogViewData(self._ctx)

    def _onLoading(self, *args, **kwargs):
        self._createViewData()
        self._updateModel()

    def _updateModel(self):
        with self.viewModel.transaction() as model:
            self._updateExtraData(model)
            model.setTitleBody(self._viewData.title)
            model.setAcceptButtonText(self._viewData.okBtnTitle)
            model.setCancelButtonText(self._viewData.cancelBtnTitle)
            model.setCredits(self._viewData.credits)
            model.setGolds(self._viewData.gold)
            model.setCrystals(self._viewData.crystals)
            model.setFreexp(self._viewData.freeExp)
            model.setGoldToCreditsExchangeRate(self._viewData.goldToCreditRate)
            model.setGoldToCreditsIsDiscount(self._viewData.goldToCreditDiscount > 0)
            model.setGoldToCreditsDiscountValue(self._viewData.goldToCreditDiscount)
            model.setNotEnoughCredits(self._viewData.needCredits)
            model.setIcon(self._viewData.icon)

    def _updateExtraData(self, model):
        pass


class ConvertCurrencyForRestoreDetachmentView(ConvertCurrencyView):
    _detachmentCache = descriptor(IDetachmentCache)

    def __init__(self, ctx=None):
        super(ConvertCurrencyForRestoreDetachmentView, self).__init__(ctx)
        self._result = None
        return

    def _addListeners(self):
        super(ConvertCurrencyForRestoreDetachmentView, self)._addListeners()
        model = self.viewModel
        model.onAccept += self._getExchangeGold

    def _removeListeners(self):
        super(ConvertCurrencyForRestoreDetachmentView, self)._removeListeners()
        model = self.viewModel
        model.onAccept -= self._getExchangeGold

    def _createViewData(self):
        self._viewData = DialogRestoreDetachmentViewData(self._ctx)

    def _updateExtraData(self, model):
        detachment = self._detachmentCache.getDetachment(self._ctx['detInvID'])
        detachmentInfoModel = DetachmentShortInfoModel()
        fillDetachmentShortInfoModel(detachmentInfoModel, detachment)
        model.getExtraData().addViewModel(detachmentInfoModel)
        model.setType(ConvertCurrencyModel.DETACHMENT)

    def _getExchangeGold(self, exchangeGold):
        self._result = exchangeGold
        self._onAccept()

    def _getAdditionalData(self):
        return self._result


class ConvertCurrencyForVehicleView(ConvertCurrencyView):
    __slots__ = ('_result',)

    def __init__(self, ctx=None):
        super(ConvertCurrencyForVehicleView, self).__init__(ctx)
        self._result = None
        return

    def _addListeners(self):
        super(ConvertCurrencyForVehicleView, self)._addListeners()
        model = self.viewModel
        model.onAccept += self._getExchangeGold

    def _removeListeners(self):
        super(ConvertCurrencyForVehicleView, self)._removeListeners()
        model = self.viewModel
        model.onAccept -= self._getExchangeGold

    def _createViewData(self):
        self._viewData = DialogVehicleViewData(self._ctx)

    def _updateExtraData(self, model):
        vehicle = VehicleModel()
        vehicle.setName(self._viewData.vehName)
        vehicle.setLevel(self._viewData.vehLvl)
        vehicle.setType(self._viewData.vehType)
        vehicle.setNation(self._viewData.vehNation)
        vehicle.setIsElite(True)
        model.getExtraData().addViewModel(vehicle)
        model.setType(ConvertCurrencyModel.VEHICLE)

    def _getExchangeGold(self, exchangeGold):
        self._result = exchangeGold
        self._onAccept()

    def _getAdditionalData(self):
        return self._result


class ConvertCurrencyForCrewbookView(ConvertCurrencyView):

    def __init__(self, ctx=None):
        super(ConvertCurrencyForCrewbookView, self).__init__(ctx)
        self._result = None
        return

    def _addListeners(self):
        super(ConvertCurrencyForCrewbookView, self)._addListeners()
        model = self.viewModel
        model.onAccept += self._getExchangeGold

    def _removeListeners(self):
        model = self.viewModel
        model.onAccept -= self._getExchangeGold
        super(ConvertCurrencyForCrewbookView, self)._removeListeners()

    def _createViewData(self):
        self._viewData = DialogCrewbookViewData(self._ctx)

    def _updateExtraData(self, model):
        self._setTitleArgs(model.getTitleArgs(), (('crewbookType', self._viewData.crewbookItem.userName),))
        model.setType(ConvertCurrencyModel.BOOKS)

    def _getExchangeGold(self, exchangeGold):
        self._result = exchangeGold
        self._onAccept()

    def _getAdditionalData(self):
        return self._result

    def _setTitleArgs(self, arrModel, frmtArgs):
        for name, resource in frmtArgs:
            frmtModel = FormatResourceStringArgModel()
            frmtModel.setName(name)
            frmtModel.setValue(resource)
            arrModel.addViewModel(frmtModel)

        arrModel.invalidate()


class ConvertCurrencyForRestoreTankmanView(ConvertCurrencyView):

    def __init__(self, ctx=None):
        super(ConvertCurrencyForRestoreTankmanView, self).__init__(ctx)
        self._result = None
        return

    def _addListeners(self):
        super(ConvertCurrencyForRestoreTankmanView, self)._addListeners()
        model = self.viewModel
        model.onAccept += self._getExchangeGold

    def _removeListeners(self):
        super(ConvertCurrencyForRestoreTankmanView, self)._removeListeners()
        model = self.viewModel
        model.onAccept -= self._getExchangeGold

    def _createViewData(self):
        self._viewData = DialogRestoreRecruitViewData(self._ctx)

    def _updateExtraData(self, model):
        model.setType(ConvertCurrencyModel.TANKMAN)

    def _getExchangeGold(self, exchangeGold):
        self._result = exchangeGold
        self._onAccept()

    def _getAdditionalData(self):
        return self._result


class ConvertCurrencyForSaveMatrixView(ConvertCurrencyView):

    def __init__(self, ctx=None):
        super(ConvertCurrencyForSaveMatrixView, self).__init__(ctx)
        self._result = None
        return

    def _addListeners(self):
        super(ConvertCurrencyForSaveMatrixView, self)._addListeners()
        model = self.viewModel
        model.onAccept += self._getExchangeGold

    def _removeListeners(self):
        super(ConvertCurrencyForSaveMatrixView, self)._removeListeners()
        model = self.viewModel
        model.onAccept -= self._getExchangeGold

    def _createViewData(self):
        self._viewData = DialogMatrixEditViewData(self._ctx)

    def _updateExtraData(self, model):
        model.setType(ConvertCurrencyModel.MATRIX_EDIT)

    def _getExchangeGold(self, exchangeGold):
        self._result = exchangeGold
        self._onAccept()

    def _getAdditionalData(self):
        return self._result
