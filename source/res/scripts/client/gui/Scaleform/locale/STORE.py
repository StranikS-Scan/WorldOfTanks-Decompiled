# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/locale/STORE.py
from debug_utils import LOG_WARNING

class STORE(object):
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
    RENTALTERMSELECTIONPOPOVER_TERMSLOTALLDAYS_ENUM = (RENTALTERMSELECTIONPOPOVER_TERMSLOT3DAYS, RENTALTERMSELECTIONPOPOVER_TERMSLOT7DAYS, RENTALTERMSELECTIONPOPOVER_TERMSLOT30DAYS)

    @classmethod
    def getRentTermDays(cls, days):
        outcome = '#store:rentalTermSelectionPopover/termSlot{}Days'.format(days)
        if outcome not in cls.RENTALTERMSELECTIONPOPOVER_TERMSLOTALLDAYS_ENUM:
            LOG_WARNING('Localization key "{}" not found'.format(outcome))
            return None
        else:
            return outcome
