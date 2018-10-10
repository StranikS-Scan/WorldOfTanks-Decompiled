# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehiclePreview20/info/vehicle_preview_browse_tab.py
from CurrentVehicle import g_currentPreviewVehicle
from gui.Scaleform.daapi.view.meta.VehiclePreviewBrowseTabMeta import VehiclePreviewBrowseTabMeta
from gui.Scaleform.locale.RES_SHOP import RES_SHOP
from gui.Scaleform.locale.VEHICLE_PREVIEW import VEHICLE_PREVIEW
from gui.shared.formatters import text_styles
from gui.shared.money import Currency
_MAX_LENGTH_FULL_DESCRIPTION_NO_KPI = 400
_MAX_LENGTH_FULL_DESCRIPTION_WITH_KPI = 280

class VehiclePreviewBrowseTab(VehiclePreviewBrowseTabMeta):

    def __init__(self):
        super(VehiclePreviewBrowseTab, self).__init__()
        self.__isHeroTank = False

    def _populate(self):
        super(VehiclePreviewBrowseTab, self)._populate()
        g_currentPreviewVehicle.onComponentInstalled += self.update
        g_currentPreviewVehicle.onChanged += self.update
        self.update()

    def _dispose(self):
        g_currentPreviewVehicle.onComponentInstalled -= self.update
        g_currentPreviewVehicle.onChanged -= self.update
        super(VehiclePreviewBrowseTab, self)._dispose()

    def setActiveState(self, isActive):
        pass

    def setHeroTank(self, isHeroTank):
        self.__isHeroTank = isHeroTank
        self.update()

    def update(self, *args):
        self._update()

    def _update(self):
        if g_currentPreviewVehicle.isPresent():
            item = g_currentPreviewVehicle.item
            if item.buyPrices.itemPrice.defPrice.get(Currency.GOLD):
                maxDescriptionLength = _MAX_LENGTH_FULL_DESCRIPTION_WITH_KPI
                bonuses = [{'icon': RES_SHOP.MAPS_SHOP_KPI_STAR_ICON_BENEFITS,
                  'title': text_styles.concatStylesToMultiLine(text_styles.highTitle(VEHICLE_PREVIEW.INFOPANEL_PREMIUM_FREEEXPMULTIPLIER), text_styles.main(VEHICLE_PREVIEW.INFOPANEL_PREMIUM_FREEEXPTEXT))}, {'icon': RES_SHOP.MAPS_SHOP_KPI_CROW_BENEFITS,
                  'title': text_styles.concatStylesToMultiLine(text_styles.highTitle(VEHICLE_PREVIEW.INFOPANEL_PREMIUM_CREWTRANSFERTITLE), text_styles.main(VEHICLE_PREVIEW.INFOPANEL_PREMIUM_CREWTRANSFERTEXT))}]
                if not item.isSpecial:
                    bonuses.insert(1, {'icon': RES_SHOP.MAPS_SHOP_KPI_MONEY_BENEFITS,
                     'title': text_styles.concatStylesToMultiLine(text_styles.highTitle(VEHICLE_PREVIEW.INFOPANEL_PREMIUM_CREDITSMULTIPLIER), text_styles.main(VEHICLE_PREVIEW.INFOPANEL_PREMIUM_CREDITSTEXT))})
            else:
                maxDescriptionLength = _MAX_LENGTH_FULL_DESCRIPTION_NO_KPI
                bonuses = None
            description = item.fullDescription.decode('utf-8')
            hasTooltip = len(description) > maxDescriptionLength
            if hasTooltip:
                description = description[:maxDescriptionLength - 3] + '...'
            self.as_setDataS(text_styles.main(description), hasTooltip, bonuses)
        return
