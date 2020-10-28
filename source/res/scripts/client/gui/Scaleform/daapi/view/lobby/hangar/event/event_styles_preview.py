# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/event/event_styles_preview.py
import logging
import BigWorld
import Keys
from helpers import dependency
from gui import SystemMessages
from gui.Scaleform.genConsts.CURRENCIES_CONSTANTS import CURRENCIES_CONSTANTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.money import Money
from gui.shop import showBuyGoldForCustomization
from gui.server_events.events_dispatcher import showEventHangar
from gui.Scaleform.daapi.view.lobby.hangar.event.event_styles_preview_base import EventStylesTradeBase
from gui.shared.utils import decorators
from items.vehicles import makeVehicleTypeCompDescrByName, VehicleDescriptor
from gui.shared.gui_items.processors import Processor, makeI18nError, plugins
from ClientSelectableCameraObject import ClientSelectableCameraObject
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents, CameraMovementStates
from HalloweenHangarTank import HalloweenHangarTank
from gui.impl.gen import R
from gui.impl import backport
from gui import InputHandler
from skeletons.gui.game_event_controller import IGameEventController
_logger = logging.getLogger(__name__)
_COMMA = ', '

class StyleItemBuyer(Processor):
    gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, vehTypeCompDescr, currency, money):
        super(StyleItemBuyer, self).__init__(plugins=(plugins.MoneyValidator(Money(**{currency: money})), plugins.RandomStylesSellingAvailable(self.gameEventController.getShop().isRandomStylesSellingAvailable())))
        self._vehTypeCompDescr = vehTypeCompDescr
        self._currency = currency
        self._money = money

    def _request(self, callback):
        _logger.debug('Make server request to buy style %d for: %d ', self._vehTypeCompDescr, self._money)
        BigWorld.player().buyHalloweenStyle(self._vehTypeCompDescr, lambda code, errorCode: self._response(code, callback, errorCode))

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('hw19_style/%s' % errStr, defaultSysMsgKey='hw19/server_error')


class StyleBundleBuyer(Processor):
    gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, currency, money):
        super(StyleBundleBuyer, self).__init__(plugins=(plugins.MoneyValidator(Money(**{currency: money})), plugins.RandomStylesSellingAvailable(self.gameEventController.getShop().isRandomStylesSellingAvailable())))
        self._currency = currency
        self._money = money

    def _request(self, callback):
        _logger.debug('Make server request to buy bundle for: %d ', self._money)
        BigWorld.player().buyHalloweenStyleBundle(lambda code, errorCode: self._response(code, callback, errorCode))

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('hw19_style/%s' % errStr, defaultSysMsgKey='hw19/server_error')


class EventStylesPreview(EventStylesTradeBase):
    _HW20_STYLE_VEHICLE_NAME = 'germany:G89_Leopard1'

    def __init__(self, ctx=None):
        super(EventStylesPreview, self).__init__(ctx)
        self._vehicleStyles = self.gameEventController.getShop().getStylesForRandom().values()
        self._skipHangarView = False
        if 'itemCD' in self._ctx:
            types = self._getVehicleTypes()
            self._selectedTank = [ makeVehicleTypeCompDescrByName(veh) for veh in types ].index(self._ctx['itemCD'])

    def closeView(self):
        ClientSelectableCameraObject.switchCamera()
        showEventHangar()

    def onBackClick(self):
        self.closeView()

    def onBuyClick(self):
        vehicleType = self._getVehicleTypes()[self._selectedTank]
        vehTypeCompDescr = makeVehicleTypeCompDescrByName(vehicleType)
        styles = self.gameEventController.getShop().getStylesForRandom()
        style = styles[vehTypeCompDescr]
        currency, price = style['currency'], style['price']
        currencyAmount = self._getCurrencyAmount(style['currency'])
        if currencyAmount < price:
            showBuyGoldForCustomization(price)
        else:
            self.__buyStyle(vehTypeCompDescr, currency, price)

    def onUseClick(self):
        self._skipHangarView = True
        ClientSelectableCameraObject.switchCamera()
        super(EventStylesPreview, self).onUseClick()

    def onBundleClick(self):
        config = self.gameEventController.getShop().getStylesForRandomBundle()
        currency, price = config['currency'], config['price']
        currencyAmount = self._getCurrencyAmount(currency)
        if currencyAmount < price:
            showBuyGoldForCustomization(price)
        else:
            self.__buyBundle(currency, price)

    def showBlur(self):
        super(EventStylesPreview, self).showBlur()
        self.hideMarkers()

    def hideBlur(self):
        super(EventStylesPreview, self).hideBlur()
        self.showMarkers()

    def _onSelect(self, index):
        vehicleType = self._getVehicleTypes()[index]
        for cameraObject in ClientSelectableCameraObject.allCameraObjects:
            if isinstance(cameraObject, HalloweenHangarTank) and vehicleType == cameraObject.vehicleType:
                ClientSelectableCameraObject.switchCamera(cameraObject)
                break

    def _populate(self):
        super(EventStylesPreview, self)._populate()
        self.addListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__onCameraSwitched)
        self.hangarSpace.setVehicleSelectable(True)
        InputHandler.g_instance.onKeyDown += self.__handleKeyEvent

    def _dispose(self):
        self.removeListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__onCameraSwitched)
        ClientSelectableCameraObject.switchCamera()
        InputHandler.g_instance.onKeyDown -= self.__handleKeyEvent
        super(EventStylesPreview, self)._dispose()

    def _getStyles(self):
        return self._vehicleStyles

    def _getCurrencyAmount(self, currency):
        stats = self.itemsCache.items.stats
        return stats.money.get(currency, 0)

    def _getBundlePrice(self):
        config = self.gameEventController.getShop().getStylesForRandomBundle()
        return config['price']

    def _getVO(self):
        vo = super(EventStylesPreview, self)._getVO()
        styles = self._getStyles()
        stylesInInventory = self._getStylesInInventory()
        vehiclesInInventory = self._getVehiclesInInventory()
        anyStyleInStorage = False
        allVehiclesInHangar = True
        anyVehicleInHangar = False
        tankNames = []
        tankNotInInventoryNames = []
        for style in styles:
            styleID = int(style['styleID'])
            vehicleDescr = VehicleDescriptor(typeName=style['vehicle'])
            vehicleName = vehicleDescr.type.shortUserString
            tankNames.append(vehicleName)
            if styleID in stylesInInventory:
                anyStyleInStorage = True
            haveTank = vehicleDescr.type.compactDescr in vehiclesInInventory
            if not haveTank:
                allVehiclesInHangar = False
                tankNotInInventoryNames.append(vehicleName)
            anyVehicleInHangar = True

        bundleNotEnoughCount = max(self._getBundlePrice() - self._getCurrencyAmount(CURRENCIES_CONSTANTS.GOLD), 0)
        if allVehiclesInHangar:
            description = backport.text(R.strings.event.tradeStyles.warningMultiHasTank())
        elif anyVehicleInHangar:
            description = backport.text(R.strings.event.tradeStyles.warningMultiHasNotAllTanks(), name=', '.join(tankNotInInventoryNames))
        else:
            description = backport.text(R.strings.event.tradeStyles.warningMulti())
        vo.update({'noOneInHangar': not anyVehicleInHangar,
         'header': backport.text(R.strings.event.tradeStyles.confirmationMultiTitle(), name=', '.join(tankNames)),
         'description': description,
         'canBuyBundle': not anyStyleInStorage,
         'bundlePrice': backport.getNiceNumberFormat(self._getBundlePrice()),
         'isShowAuthor': True,
         'useConfirm': True,
         'bundleNotEnough': bundleNotEnoughCount > 0,
         'bundleTooltip': {'tooltip': '',
                           'specialArgs': [bundleNotEnoughCount],
                           'specialAlias': TOOLTIPS_CONSTANTS.EVENT_GOLD_ERROR,
                           'isSpecial': True}})
        return vo

    def _getSkinVO(self, style):
        vo = super(EventStylesPreview, self)._getSkinVO(style)
        vo.update(self.__getStyleAuthorAndDescription(style['vehicle']))
        return vo

    def __handleKeyEvent(self, event):
        if event.key == Keys.KEY_ESCAPE:
            self.closeView()

    def __getTanksStr(self, tankNames):
        return backport.text(R.strings.event.tradeStyles.infoVehTypeStr()).format(_COMMA.join(tankNames[:-1]), tankNames[-1])

    def __getStyleAuthorAndDescription(self, vehicleName):
        return {'isShowAuthorImage': False,
         'styleTitle': backport.text(R.strings.event.tradeStyles.infoTitleNewStyle()),
         'styleDescription': backport.text(R.strings.event.tradeStyles.infoDescrNewStyle())} if vehicleName == self._HW20_STYLE_VEHICLE_NAME else {'isShowAuthorImage': True,
         'styleTitle': backport.text(R.strings.event.tradeStyles.infoTitle()),
         'styleDescription': backport.text(R.strings.event.tradeStyles.infoDescr())}

    @decorators.process('updating')
    def __buyStyle(self, vehTypeCompDescr, currency, price):
        result = yield StyleItemBuyer(vehTypeCompDescr, currency, price).request()
        if result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)

    @decorators.process('updating')
    def __buyBundle(self, currency, price):
        result = yield StyleBundleBuyer(currency, price).request()
        if result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)

    def __onCameraSwitched(self, event):
        cameraObject = None
        for obj in ClientSelectableCameraObject.allCameraObjects:
            if obj.id == event.ctx['entityId']:
                cameraObject = obj
                break

        if not cameraObject:
            return
        else:
            if isinstance(cameraObject, HalloweenHangarTank):
                index = self._getVehicleTypes().index(cameraObject.vehicleType)
                if event.ctx['state'] != CameraMovementStates.FROM_OBJECT:
                    self._selectVehicleByIndex(index)
                else:
                    _logger.debug('Deselect old vehicle with index %s.', index)
            else:
                skipHangarView = self._skipHangarView
                self.destroy()
                if not skipHangarView:
                    showEventHangar()
            return
