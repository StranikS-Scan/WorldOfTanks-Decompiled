# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/locale/STORE.py
from debug_utils import LOG_WARNING

class STORE(object):
    BUYVEHICLEWINDOW_EQUIPMENT_AMMO = '#store:buyVehicleWindow/equipment/ammo'
    BUYVEHICLEWINDOW_EQUIPMENT_SLOT = '#store:buyVehicleWindow/equipment/slot'
    BUYVEHICLEWINDOW_BUYBTN = '#store:buyVehicleWindow/buyBtn'
    BUYVEHICLEWINDOW_RENTBTN = '#store:buyVehicleWindow/rentBtn'
    BUYVEHICLEWINDOW_EXCHANGE = '#store:buyVehicleWindow/exchange'
    BUYVEHICLEWINDOW_RESTORE = '#store:buyVehicleWindow/restore'
    BUYVEHICLEWINDOW_CANCEL = '#store:buyVehicleWindow/cancel'
    BUYVEHICLEWINDOW_TRADEINBTNLABEL = '#store:buyVehicleWindow/tradeInBtnLabel'
    BUYVEHICLEWINDOW_FREE = '#store:buyVehicleWindow/free'
    BUYVEHICLEWINDOW_DESCRIPTION = '#store:buyVehicleWindow/description'
    BUYVEHICLEWINDOW_FOOTERTEXT = '#store:buyVehicleWindow/footerText'
    BUYVEHICLEWINDOW_FOOTERTEXTRENT = '#store:buyVehicleWindow/footerTextRent'
    BUYVEHICLEWINDOW_FOOTERTEXTRESTORE = '#store:buyVehicleWindow/footerTextRestore'
    BUYVEHICLEWINDOW_TYPE_LIGHTTANK = '#store:buyVehicleWindow/type/lightTank'
    BUYVEHICLEWINDOW_TYPE_MEDIUMTANK = '#store:buyVehicleWindow/type/mediumTank'
    BUYVEHICLEWINDOW_TYPE_HEAVYTANK = '#store:buyVehicleWindow/type/heavyTank'
    BUYVEHICLEWINDOW_TYPE_AT_SPG = '#store:buyVehicleWindow/type/AT-SPG'
    BUYVEHICLEWINDOW_TYPE_SPG = '#store:buyVehicleWindow/type/SPG'
    BUYVEHICLEWINDOW_TITLEBUY = '#store:buyVehicleWindow/titleBuy'
    BUYVEHICLEWINDOW_TITLERESTORE = '#store:buyVehicleWindow/titleRestore'
    BUYVEHICLEWINDOW_TITLERENT = '#store:buyVehicleWindow/titleRent'
    BUYVEHICLEWINDOW_RENTBTNLABELSEASON_EPICSEASON = '#store:buyVehicleWindow/rentBtnLabelSeason/epicSeason'
    BUYVEHICLEWINDOW_RENTBTNLABELSEASON_EPICCYCLE = '#store:buyVehicleWindow/rentBtnLabelSeason/epicCycle'
    BUYVEHICLEWINDOW_RENTBTNLABELSEASON_RANKEDSEASON = '#store:buyVehicleWindow/rentBtnLabelSeason/rankedSeason'
    BUYVEHICLEWINDOW_RENTBTNLABELSEASON_RANKEDCYCLE = '#store:buyVehicleWindow/rentBtnLabelSeason/rankedCycle'
    BUYVEHICLEWINDOW_RENTBTNLABEL3DAYS = '#store:buyVehicleWindow/rentBtnLabel3Days'
    BUYVEHICLEWINDOW_RENTBTNLABEL7DAYS = '#store:buyVehicleWindow/rentBtnLabel7Days'
    BUYVEHICLEWINDOW_RENTBTNLABEL30DAYS = '#store:buyVehicleWindow/rentBtnLabel30Days'
    BUYVEHICLEWINDOW_TERMSLOTUNLIM = '#store:buyVehicleWindow/termSlotUnlim'
    BUYVEHICLEWINDOW_RENTBTNLABELANY = '#store:buyVehicleWindow/rentBtnLabelAny'
    BUYVEHICLEWINDOW_TOGGLEBTN_RENT = '#store:buyVehicleWindow/toggleBtn/rent'
    BUYVEHICLEWINDOW_TOGGLEBTN_BUY = '#store:buyVehicleWindow/toggleBtn/buy'
    SELLCONFIRMATIONPOPOVER_TITLELABEL = '#store:sellConfirmationPopover/titleLabel'
    SELLCONFIRMATIONPOPOVER_PRICELABEL = '#store:sellConfirmationPopover/priceLabel'
    RENTALTERMSELECTIONPOPOVER_TITLELABEL = '#store:rentalTermSelectionPopover/titleLabel'
    RENTALTERMSELECTIONPOPOVER_TERMSLOT3DAYS = '#store:rentalTermSelectionPopover/termSlot3Days'
    RENTALTERMSELECTIONPOPOVER_TERMSLOT7DAYS = '#store:rentalTermSelectionPopover/termSlot7Days'
    RENTALTERMSELECTIONPOPOVER_TERMSLOT30DAYS = '#store:rentalTermSelectionPopover/termSlot30Days'
    RENTALTERMSELECTIONPOPOVER_TERMSLOTANY = '#store:rentalTermSelectionPopover/termSlotAny'
    RENTALTERMSELECTIONPOPOVER_TERMSLOTSEASON_EPICSEASON = '#store:rentalTermSelectionPopover/termSlotSeason/epicSeason'
    RENTALTERMSELECTIONPOPOVER_TERMSLOTSEASON_EPICCYCLE = '#store:rentalTermSelectionPopover/termSlotSeason/epicCycle'
    RENTALTERMSELECTIONPOPOVER_TERMSLOTSEASON_RANKEDSEASON = '#store:rentalTermSelectionPopover/termSlotSeason/rankedSeason'
    RENTALTERMSELECTIONPOPOVER_TERMSLOTSEASON_RANKEDCYCLE = '#store:rentalTermSelectionPopover/termSlotSeason/rankedCycle'
    RENTALTERMSELECTIONPOPOVER_TERMSLOTUNLIM = '#store:rentalTermSelectionPopover/termSlotUnlim'
    CONGRATULATIONANIM_BUYINGLABEL = '#store:congratulationAnim/buyingLabel'
    CONGRATULATIONANIM_DESCRIPTIONLABEL_STYLE = '#store:congratulationAnim/descriptionLabel/style'
    CONGRATULATIONANIM_CONFIRMLABEL = '#store:congratulationAnim/confirmLabel'
    CONGRATULATIONANIM_BACKLABEL = '#store:congratulationAnim/backLabel'
    CONGRATULATIONANIM_COLLECTIBLELABEL = '#store:congratulationAnim/collectibleLabel'
    CONGRATULATIONANIM_RESTORELABEL = '#store:congratulationAnim/restoreLabel'
    CONGRATULATIONANIM_SHOWPREVIEWBTNLABEL = '#store:congratulationAnim/showPreviewBtnLabel'
    CONGRATULATIONANIM_BACKTOEPICLABEL = '#store:congratulationAnim/backToEpicLabel'
    RENTALTERMSELECTIONPOPOVER_TERMSLOTALLDAYS_ENUM = (RENTALTERMSELECTIONPOPOVER_TERMSLOT3DAYS, RENTALTERMSELECTIONPOPOVER_TERMSLOT7DAYS, RENTALTERMSELECTIONPOPOVER_TERMSLOT30DAYS)

    @classmethod
    def getRentTermDays(cls, days):
        outcome = '#store:rentalTermSelectionPopover/termSlot{}Days'.format(days)
        if outcome not in cls.RENTALTERMSELECTIONPOPOVER_TERMSLOTALLDAYS_ENUM:
            LOG_WARNING('Localization key "{}" not found'.format(outcome))
            return None
        else:
            return outcome
