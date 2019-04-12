# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/locale/STORE.py
from debug_utils import LOG_WARNING

class STORE(object):
    BUYVEHICLEWINDOW_TITLE = '#store:buyVehicleWindow/title'
    BUYVEHICLEWINDOW_TITLE_RESTORE = '#store:buyVehicleWindow/title_restore'
    BUYVEHICLEWINDOW_RENT_TITLE = '#store:buyVehicleWindow/rent/title'
    BUYVEHICLEWINDOW_PRICEDESCRIPTION_FULL = '#store:buyVehicleWindow/priceDescription/full'
    BUYVEHICLEWINDOW_PRICEDESCRIPTION_RENT = '#store:buyVehicleWindow/priceDescription/rent'
    BUYVEHICLEWINDOW_PRICEDESCRIPTION_RESTORE = '#store:buyVehicleWindow/priceDescription/restore'
    BUYVEHICLEWINDOW_PRICEDESCRIPTION_TRADEIN = '#store:buyVehicleWindow/priceDescription/tradeIn'
    BUYVEHICLEWINDOW_SLOT_0 = '#store:buyVehicleWindow/slot/0'
    BUYVEHICLEWINDOW_FREESLOT = '#store:buyVehicleWindow/freeSlot'
    BUYVEHICLEWINDOW_BOOTCAMP_TOPCOMMANDERFREE = '#store:buyVehicleWindow/bootcamp/topCommanderFree'
    BUYVEHICLEWINDOW_SLOT_1 = '#store:buyVehicleWindow/slot/1'
    BUYVEHICLEWINDOW_SLOT_2 = '#store:buyVehicleWindow/slot/2'
    BUYVEHICLEWINDOW_CHECKBOX_BUY_WITHOUTCREW = '#store:buyVehicleWindow/checkBox/buy/withoutCrew'
    BUYVEHICLEWINDOW_CHECKBOX_RESTORE_WITHOUTCREW = '#store:buyVehicleWindow/checkBox/restore/withoutCrew'
    BUYVEHICLEWINDOW_COUNTCREWLBL = '#store:buyVehicleWindow/countCrewLbl'
    BUYVEHICLEWINDOW_EQUIPMENT_AMMO = '#store:buyVehicleWindow/equipment/ammo'
    BUYVEHICLEWINDOW_EQUIPMENT_SLOT = '#store:buyVehicleWindow/equipment/slot'
    BUYVEHICLEWINDOW_BUYBTN = '#store:buyVehicleWindow/buyBtn'
    BUYVEHICLEWINDOW_RENTBTN = '#store:buyVehicleWindow/rentBtn'
    BUYVEHICLEWINDOW_EXCHANGE = '#store:buyVehicleWindow/exchange'
    BUYVEHICLEWINDOW_RESTORE = '#store:buyVehicleWindow/restore'
    BUYVEHICLEWINDOW_TRADEINBTNLABEL = '#store:buyVehicleWindow/tradeInBtnLabel'
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
    BUYVEHICLEWINDOW_CREWINVEHICLE = '#store:buyVehicleWindow/crewInVehicle'
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
    CONGRATULATIONANIM_RESTORELABEL = '#store:congratulationAnim/restoreLabel'
    CONGRATULATIONANIM_SHOWPREVIEWBTNLABEL = '#store:congratulationAnim/showPreviewBtnLabel'
    CONGRATULATIONANIM_SHOWEPICBTNLABEL = '#store:congratulationAnim/showEpicBtnLabel'
    BUYVEHICLEWINDOW_SLOT_ENUM = (BUYVEHICLEWINDOW_SLOT_0, BUYVEHICLEWINDOW_SLOT_1, BUYVEHICLEWINDOW_SLOT_2)
    RENTALTERMSELECTIONPOPOVER_TERMSLOTALLDAYS_ENUM = (RENTALTERMSELECTIONPOPOVER_TERMSLOT3DAYS, RENTALTERMSELECTIONPOPOVER_TERMSLOT7DAYS, RENTALTERMSELECTIONPOPOVER_TERMSLOT30DAYS)

    @classmethod
    def getBuyVehicleSlotTitle(cls, key0):
        outcome = '#store:buyVehicleWindow/slot/{}'.format(key0)
        if outcome not in cls.BUYVEHICLEWINDOW_SLOT_ENUM:
            LOG_WARNING('Localization key "{}" not found'.format(outcome))
            return None
        else:
            return outcome

    @classmethod
    def getRentTermDays(cls, days):
        outcome = '#store:rentalTermSelectionPopover/termSlot{}Days'.format(days)
        if outcome not in cls.RENTALTERMSELECTIONPOPOVER_TERMSLOTALLDAYS_ENUM:
            LOG_WARNING('Localization key "{}" not found'.format(outcome))
            return None
        else:
            return outcome
