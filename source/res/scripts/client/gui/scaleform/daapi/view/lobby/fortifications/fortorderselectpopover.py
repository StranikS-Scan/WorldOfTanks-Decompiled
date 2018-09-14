# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortOrderSelectPopover.py
import constants
from adisp import process
from gui.Scaleform.genConsts.TEXT_MANAGER_STYLES import TEXT_MANAGER_STYLES
from helpers.i18n import makeString as _ms
from gui.prb_control.prb_helpers import UnitListener
from gui.shared.fortifications.context import ActivateConsumableCtx, ReturnConsumableCtx
from gui.Scaleform.daapi.view.meta.FortOrderSelectPopoverMeta import FortOrderSelectPopoverMeta
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.framework import AppRef
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.managers.UtilsManager import ImageUrlProperties
from gui.Scaleform.framework.managers.TextManager import TextIcons
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_formatters

class FortOrderSelectPopover(FortOrderSelectPopoverMeta, SmartPopOverView, View, FortViewHelper, AppRef, UnitListener):

    def __init__(self, ctx = None):
        super(FortOrderSelectPopover, self).__init__()
        self.__slotIdx = ctx.get('data').slotID

    def onWindowClose(self):
        self.destroy()

    @process
    def addOrder(self, consumableOrderTypeID):
        yield self.fortProvider.sendRequest(ActivateConsumableCtx(consumableOrderTypeID, self.__slotIdx, waitingID='fort/activateConsumable'))

    @process
    def removeOrder(self, consumableOrderTypeID):
        yield self.fortProvider.sendRequest(ReturnConsumableCtx(consumableOrderTypeID, waitingID='fort/returnConsumable'))

    def onConsumablesChanged(self, unitMgrID):
        self.destroy()

    def onUnitExtraChanged(self, extra):
        self.destroy()

    def _populate(self):
        super(FortOrderSelectPopover, self)._populate()
        self.startFortListening()
        self.__updateData()

    def _dispose(self):
        self.stopFortListening()
        super(FortOrderSelectPopover, self)._dispose()

    def __updateData(self):
        fort = self.fortCtrl.getFort()
        extra = self.unitFunctional.getExtra()
        _getText = self.app.utilsManager.textManager.getText
        result = []
        activeConsumes = dict(((otID, slotIdx) for slotIdx, (otID, level) in extra.getConsumables().iteritems()))
        for orderTypeID in constants.FORT_ORDER_TYPE.CONSUMABLES:
            orderItem = fort.getOrder(orderTypeID)
            building = fort.getBuilding(orderItem.buildingID)
            isBuildingReady = building is not None
            isSelected = orderTypeID in activeConsumes
            isSelectedInThisSlot = isSelected and activeConsumes[orderTypeID] == self.__slotIdx
            isConsumableEnabled = isSelectedInThisSlot or not isSelected and orderItem.count > 0
            showArsenalIcon = isBuildingReady and not isSelected
            if isSelectedInThisSlot:
                returnBtnLabel = FORTIFICATIONS.ORDERSELECTPOPOVER_RETURNBTNLABEL
            else:
                returnBtnLabel = ''
            orderLevelLabel = _getText(TEXT_MANAGER_STYLES.MAIN_TEXT, _ms(FORTIFICATIONS.ORDERSELECTPOPOVER_ORDERLEVEL, orderLevel=fort_formatters.getTextLevel(orderItem.level)))
            if not isBuildingReady:
                icon = self.app.utilsManager.getHtmlIconText(ImageUrlProperties(RES_ICONS.MAPS_ICONS_LIBRARY_REDNOTAVAILABLE, 16, 16, -2, 0))
                description = '%s %s' % (icon, _getText(TEXT_MANAGER_STYLES.ERROR_TEXT, _ms(FORTIFICATIONS.ORDERSELECTPOPOVER_NOTAVAILABLE)))
                orderCountText = ''
            elif not isSelected:
                description = orderLevelLabel
                if orderItem.count:
                    orderCountText = _getText(TEXT_MANAGER_STYLES.STANDARD_TEXT, _ms(FORTIFICATIONS.ORDERSELECTPOPOVER_ORDERCOUNT, orderNumber=_getText(TEXT_MANAGER_STYLES.STATS_TEXT, str(orderItem.count))))
                else:
                    orderCountText = _getText(TEXT_MANAGER_STYLES.STANDARD_TEXT, _ms(FORTIFICATIONS.ORDERSELECTPOPOVER_ORDERCOUNT, orderNumber=_getText(TEXT_MANAGER_STYLES.ERROR_TEXT, str(orderItem.count))))
            else:
                if isSelectedInThisSlot:
                    description = ''
                else:
                    description = orderLevelLabel
                icon = self.app.utilsManager.textManager.getIcon(TextIcons.CHECKMARK_ICON)
                orderCountText = icon + _getText(TEXT_MANAGER_STYLES.SUCCESS_TEXT, _ms(FORTIFICATIONS.ORDERSELECTPOPOVER_SELECTED))
            result.append({'orderID': orderTypeID,
             'orderIconSrc': orderItem.icon,
             'headerText': _getText(TEXT_MANAGER_STYLES.MIDDLE_TITLE, _ms(orderItem.userName)),
             'descriptionText': description,
             'orderCountText': orderCountText,
             'isEnabled': isConsumableEnabled,
             'isSelected': isSelectedInThisSlot,
             'showArsenalIcon': showArsenalIcon,
             'returnBtnLabel': returnBtnLabel,
             'orderLevel': orderItem.level})

        self.as_setDataS({'orders': result})
        return
