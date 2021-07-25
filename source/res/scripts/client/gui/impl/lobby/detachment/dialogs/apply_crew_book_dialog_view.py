# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/dialogs/apply_crew_book_dialog_view.py
import logging
from math import ceil
from helpers.dependency import descriptor
import nations
from async import await, async
from frameworks.wulf import ViewSettings
from gui.impl import backport
from gui.impl.auxiliary.detachment_helper import fillDetachmentTopPanelModel, fillRoseSheetsModel, fillDetachmentPreviewInfo
from gui.impl.dialogs.dialogs import showDetachmentConfrimExpOverflowDialogView
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.dialogs.apply_crew_book_dialog_view_model import ApplyCrewBookDialogViewModel
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.points_info_tooltip_model import PointsInfoTooltipModel
from gui.impl.lobby.detachment.tooltips.commander_perk_tooltip import CommanderPerkTooltip
from gui.impl.lobby.detachment.tooltips.detachment_info_tooltip import DetachmentInfoTooltip
from gui.impl.lobby.detachment.tooltips.level_badge_tooltip_view import LevelBadgeTooltipView
from gui.impl.lobby.detachment.tooltips.points_info_tooltip_view import PointInfoTooltipView
from gui.impl.lobby.detachment.tooltips.rank_tooltip import RankTooltip
from gui.impl.lobby.detachment.tooltips.skills_branch_view import SkillsBranchTooltipView
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
_INITIAL_AMOUNT = 1
_PROGRESS_DELTA_UNCHANGED = -1
_LEVEL_NO_GAINED = 0
_EXP_INPUT_MAX_VALUE = 999999999

class ApplyCrewBookDialogView(FullScreenDialogView):
    __itemsCache = descriptor(IItemsCache)
    __detachmentCache = descriptor(IDetachmentCache)
    __slots__ = ('_bookItem', '_detachment', '__tooltipByContentID')

    def __init__(self, ctx):
        settings = ViewSettings(R.views.lobby.detachment.dialogs.ApplyCrewBookDialogView())
        settings.model = ApplyCrewBookDialogViewModel()
        super(ApplyCrewBookDialogView, self).__init__(settings)
        self._bookItem = self.__itemsCache.items.getItemByCD(ctx.get('bookCD'))
        self._detachment = self.__detachmentCache.getDetachment(ctx.get('detInvID'))
        rTooltips = R.views.lobby.detachment.tooltips
        self.__tooltipByContentID = {rTooltips.CommanderPerkTooltip(): self.__getCommanderPerkTooltip,
         rTooltips.DetachmentInfoTooltip(): self.__getDetachmentInfoTooltip,
         rTooltips.LevelBadgeTooltip(): self.__getLevelBadgeTooltip,
         rTooltips.RankTooltip(): self.__getRankTooltip,
         rTooltips.PointsInfoTooltip(): self.__getPointsInfoTooltip,
         rTooltips.SkillsBranchTooltip(): self.__getSkillsBranchTooltip}

    @property
    def viewModel(self):
        return super(ApplyCrewBookDialogView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        createTooltip = self.__tooltipByContentID.get(contentID)
        return createTooltip(event) if createTooltip else super(ApplyCrewBookDialogView, self).createToolTipContent(event, contentID)

    def _addListeners(self):
        super(ApplyCrewBookDialogView, self)._addListeners()
        self.viewModel.onStepperChange += self._onStepperChange

    def _removeListeners(self):
        super(ApplyCrewBookDialogView, self)._removeListeners()
        self.viewModel.onStepperChange -= self._onStepperChange

    def _finalize(self):
        self.soundManager.playInstantSound(backport.sound(R.sounds.detachment_progress_bar_stop_all()))
        super(ApplyCrewBookDialogView, self)._finalize()
        self.__tooltipByContentID.clear()

    def _setBaseParams(self, model):
        self.__updateRose()
        with model.transaction() as viewModel:
            detachment = self._detachment
            bookItem = self._bookItem
            viewModel.setNation(nations.MAP.get(bookItem.nationID, ''))
            viewModel.setCrewBookType(bookItem.getBookType())
            vehicleItem = self.__itemsCache.items.getVehicle(detachment.vehInvID)
            vehicleName = vehicleItem.shortUserName if vehicleItem else ''
            viewModel.setVehicleName(vehicleName)
            progression = detachment.progression
            detDescr = detachment.getDescriptor()
            availableXP = float(progression.getLevelStartingXP(progression.maxLevel) - detDescr.experience)
            maxValue = min(int(ceil(availableXP / bookItem.getXP())), bookItem.getFreeCount())
            viewModel.setMaxValue(maxValue)
            viewModel.setIsMaxLevel(detachment.hasMaxMasteryLevel)
            viewModel.setTitleBody(R.strings.dialogs.detachment.applyCrewBooks.title())
            viewModel.setAcceptButtonText(R.strings.detachment.common.use())
            viewModel.setCancelButtonText(R.strings.detachment.common.cancel())
        self.__updateStepper(_INITIAL_AMOUNT)
        super(ApplyCrewBookDialogView, self)._setBaseParams(model)

    def _onStepperChange(self, args=None):
        if args is None:
            _logger.error('Incorrect js args.')
            return
        else:
            self.__updateStepper(int(args.get('value')))
            return

    def __updateStepper(self, count):
        with self.viewModel.transaction() as viewModel:
            progression = self._detachment.progression
            detDescr = self._detachment.getDescriptor()
            amountXP = count * self._bookItem.getXP()
            dirtyXP = detDescr.experience + amountXP
            overflowXP = max(0, dirtyXP - progression.getLevelStartingXP(progression.maxLevel))
            viewModel.setSelectedValue(count)
            viewModel.setAmountXP(amountXP)
            viewModel.setAmountXPAfterElite(overflowXP)
            self.__updateTopPanel(amountXP - overflowXP)

    @async
    def _onAcceptClicked(self):
        bookCount = self.viewModel.getSelectedValue()
        bookItem = self._bookItem
        progression = self._detachment.progression
        detDescr = self._detachment.getDescriptor()
        previewXP = detDescr.experience + bookItem.getXP() * bookCount
        experienceOverflow = previewXP - progression.getLevelStartingXP(progression.maxLevel)
        if experienceOverflow > 0:
            sdr = yield await(showDetachmentConfrimExpOverflowDialogView(experienceOverflow))
            if sdr.busy:
                return
            isOk, _ = sdr.result
            if isOk:
                super(ApplyCrewBookDialogView, self)._onAcceptClicked()
        else:
            super(ApplyCrewBookDialogView, self)._onAcceptClicked()

    def _getAdditionalData(self):
        return {'bookCount': self.viewModel.getSelectedValue()}

    def __updateTopPanel(self, gainedXP=0):
        with self.viewModel.transaction() as tx:
            fillDetachmentTopPanelModel(model=tx.topPanelModel, detachment=self._detachment)
            fillDetachmentPreviewInfo(model=tx.topPanelModel, detachment=self._detachment, gainedXP=gainedXP)

    def __updateRose(self):
        with self.viewModel.transaction() as vm:
            fillRoseSheetsModel(roseModel=vm.topPanelModel.roseModel, detachment=self._detachment, newBuild=self.__getCurrentBuild())

    def __getCurrentBuild(self):
        return self._detachment.getDescriptor().build

    def __getCommanderPerkTooltip(self, event):
        perkType = event.getArgument('perkType')
        return CommanderPerkTooltip(perkType=perkType)

    def __getDetachmentInfoTooltip(self, event):
        return DetachmentInfoTooltip(detachmentInvID=self._detachment.invID)

    def __getLevelBadgeTooltip(self, event):
        return LevelBadgeTooltipView(self._detachment.invID)

    def __getRankTooltip(self, event):
        return RankTooltip(self._detachment.rankRecord)

    def __getPointsInfoTooltip(self, event):
        return PointInfoTooltipView(event.contentID, state=PointsInfoTooltipModel.DEFAULT, isClickable=False, detachmentID=self._detachment.invID)

    def __getSkillsBranchTooltip(self, event):
        course = event.getArgument('course')
        return SkillsBranchTooltipView(detachmentID=self._detachment.invID, branchID=int(course) + 1)
