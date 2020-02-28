# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehiclePreview20/info/vehicle_preview_browse_tab.py
from CurrentVehicle import g_currentPreviewVehicle
from gui.Scaleform.daapi.view.lobby.vehiclePreview20.items_kit_helper import OFFER_CHANGED_EVENT
from gui.Scaleform.daapi.view.meta.VehiclePreviewBrowseTabMeta import VehiclePreviewBrowseTabMeta
from gui.shared import g_eventBus
from gui.shared.formatters import text_styles
from gui.shared.money import Currency
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.shared import IItemsCache
_MAX_LENGTH_FULL_DESCRIPTION_NO_KPI = 400
_MAX_LENGTH_FULL_DESCRIPTION_WITH_KPI = 280

class VehiclePreviewBrowseTab(VehiclePreviewBrowseTabMeta):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(VehiclePreviewBrowseTab, self).__init__()
        self.__isHeroTank = False
        self.__offer = None
        return

    def _populate(self):
        super(VehiclePreviewBrowseTab, self)._populate()
        g_currentPreviewVehicle.onComponentInstalled += self.update
        g_currentPreviewVehicle.onChanged += self.update
        g_eventBus.addListener(OFFER_CHANGED_EVENT, self.__onOfferChanged)
        self.update()

    def _dispose(self):
        g_currentPreviewVehicle.onComponentInstalled -= self.update
        g_currentPreviewVehicle.onChanged -= self.update
        g_eventBus.removeListener(OFFER_CHANGED_EVENT, self.__onOfferChanged)
        super(VehiclePreviewBrowseTab, self)._dispose()

    def setActiveState(self, isActive):
        pass

    def setHeroTank(self, isHeroTank):
        self.__isHeroTank = isHeroTank
        self.update()

    def setActiveOffer(self, offer):
        self.__offer = offer
        self.update()

    def update(self, *_):
        self._update()

    def _update(self):
        if g_currentPreviewVehicle.isPresent():
            item = g_currentPreviewVehicle.item
            if item.buyPrices.itemPrice.defPrice.get(Currency.GOLD):
                maxDescriptionLength = _MAX_LENGTH_FULL_DESCRIPTION_WITH_KPI
                bonuses = []
                if not self.__isFrontlineCreditsOffer():
                    bonuses.append({'icon': backport.image(R.images.gui.maps.shop.kpi.star_icon_benefits()),
                     'title': text_styles.concatStylesToMultiLine(text_styles.highTitle(backport.text(R.strings.vehicle_preview.infoPanel.premium.freeExpMultiplier())), text_styles.main(backport.text(R.strings.vehicle_preview.infoPanel.premium.freeExpText())))})
                if not (item.isSpecial or self.__isFrontlineCreditsOffer()):
                    bonuses.append({'icon': backport.image(R.images.gui.maps.shop.kpi.money_benefits()),
                     'title': text_styles.concatStylesToMultiLine(text_styles.highTitle(backport.text(R.strings.vehicle_preview.infoPanel.premium.creditsMultiplier())), text_styles.main(backport.text(R.strings.vehicle_preview.infoPanel.premium.creditsText())))})
                if not item.isCrewLocked:
                    bonuses.append({'icon': backport.image(R.images.gui.maps.shop.kpi.crow_benefits()),
                     'title': text_styles.concatStylesToMultiLine(text_styles.highTitle(backport.text(R.strings.vehicle_preview.infoPanel.premium.crewTransferTitle())), text_styles.main(backport.text(R.strings.vehicle_preview.infoPanel.premium.crewTransferText())))})
                builtInEquipmentIDs = item.getBuiltInEquipmentIDs()
                builtInCount = len(builtInEquipmentIDs) if builtInEquipmentIDs else 0
                if builtInCount > 0:
                    if builtInCount == 1:
                        equipment = self.itemsCache.items.getItemByCD(builtInEquipmentIDs[0])
                        mainText = equipment.userName
                    else:
                        mainText = backport.text(R.strings.vehicle_preview.infoPanel.premium.builtInEqupmentText(), value=builtInCount)
                    bonuses.append({'icon': backport.image(R.images.gui.maps.shop.kpi.infinity_benefits()),
                     'title': text_styles.concatStylesToMultiLine(text_styles.highTitle(backport.text(R.strings.vehicle_preview.infoPanel.premium.builtInEqupmentTitle())), text_styles.main(mainText))})
            else:
                maxDescriptionLength = _MAX_LENGTH_FULL_DESCRIPTION_NO_KPI
                bonuses = None
            description = item.fullDescription.decode('utf-8')
            hasTooltip = len(description) > maxDescriptionLength
            if hasTooltip:
                description = description[:maxDescriptionLength - 3] + '...'
            self.as_setDataS(text_styles.main(description), hasTooltip, bonuses)
        return

    def __onOfferChanged(self, event):
        ctx = event.ctx
        self.setActiveOffer(ctx.get('offer'))

    def __isFrontlineCreditsOffer(self):
        return self.__offer is not None and self.__offer.eventType == 'frontline' and self.__offer.buyPrice.credits
