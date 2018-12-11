# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/new_year/new_year_vehicle_selector_popup.py
from gui import DialogsInterface, SystemMessages
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta, HtmlMessageDialogMeta, DIALOG_BUTTON_ID
from gui.Scaleform.locale.NY import NY
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.Scaleform.daapi.view.lobby.cyberSport.VehicleSelectorPopup import VehicleSelectorPopup
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeVehicleBasicVO
from gui.SystemMessages import SM_TYPE
from gui.shared.utils import decorators
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency, i18n, int2roman
from new_year.ny_processor import ApplyVehicleDiscountProcessor
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController

class NewYearVehicleSelectorPopup(VehicleSelectorPopup):
    _itemsCache = dependency.descriptor(IItemsCache)
    _nyController = dependency.descriptor(INewYearController)

    def __init__(self, ctx=None):
        super(NewYearVehicleSelectorPopup, self).__init__(ctx)
        self.__levelInfo = self._nyController.getLevel(ctx['level'])
        self._infoText = i18n.makeString(NY.APPLYDISCOUNTWINDOW_INFOTEXT, discount=self.__levelInfo.variadicDiscountValue(), level=int2roman(self.__levelInfo.level()))
        self._titleText = NY.APPLYDISCOUNTWINDOW_TITLE
        self._selectButton = NY.APPLYDISCOUNTWINDOW_BUTTONS_SELECT
        self._cancelButton = NY.APPLYDISCOUNTWINDOW_BUTTONS_CANCEL
        self._compatibleOnlyLabel = NY.APPLYDISCOUNTWINDOW_COMPATIBLECHECKBOX_LABEL
        self.__vehiclesByDiscount = self.__levelInfo.getVehiclesByDiscount()
        self.__allVehicles = self._itemsCache.items.getVehicles(REQ_CRITERIA.VEHICLE.SPECIFIC_BY_CD(self.__vehiclesByDiscount.keys()))
        self.__allVehicles = self.__allVehicles.filter(~REQ_CRITERIA.INVENTORY)

    def initFilters(self):
        filters = self._initFilter(nation=-1, vehicleType='none', isMain=False, level=-1, compatibleOnly=False)
        self._updateFilter(filters['nation'], filters['vehicleType'], filters['isMain'], filters['level'], filters['compatibleOnly'])
        self.as_setFiltersDataS(filters)
        return filters

    def updateData(self):
        super(NewYearVehicleSelectorPopup, self).updateData()
        if self.getFilters().get('compatibleOnly', True):
            vehicleVOs = self._updateData(self.__allVehicles.filter(REQ_CRITERIA.UNLOCKED))
        else:
            vehicleVOs = self._updateData(self.__allVehicles)
        self.as_setListDataS(vehicleVOs, None)
        return

    @decorators.process('newYear/applyVehicleDiscount')
    def onSelectVehicles(self, items):
        vehIntCD = int(items[0])
        vehicle = self._itemsCache.items.getItemByCD(typeCompDescr=vehIntCD)
        goodiesID = self.__vehiclesByDiscount[vehIntCD]
        discountID = self.__levelInfo.variadicDiscountID()
        discountVal = self.__levelInfo.variadicDiscountValue()
        ctx = {'discount': discountVal,
         'vehicleName': vehicle.userName,
         'vehicleType': vehicle.type}
        isOk = yield DialogsInterface.showDialog(meta=I18nConfirmDialogMeta('confirmApplyVehicleDiscount', ctx, ctx, meta=HtmlMessageDialogMeta('html_templates:newYear/dialogs', 'confirmVehDiscount', ctx, sourceKey='text'), focusedID=DIALOG_BUTTON_ID.SUBMIT))
        if isOk:
            result = yield ApplyVehicleDiscountProcessor(goodiesID, discountID).request()
            if result.success:
                SystemMessages.pushMessage(i18n.makeString(SYSTEM_MESSAGES.NEWYEAR_APPLYVEHICLEDISCOUNT_SUCCESS, discount=discountVal, vehName=vehicle.userName), type=result.sysMsgType)
            else:
                SystemMessages.pushMessage(result.userMsg, type=SM_TYPE.Error)
            self.onWindowClose()

    def _makeVehicleVOAction(self, vehicle):
        return makeVehicleBasicVO(vehicle)
