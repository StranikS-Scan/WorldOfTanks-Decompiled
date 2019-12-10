# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/dialogs/new_year_talisman_gift_dialog.py
from collections import namedtuple
from constants import ENDLESS_TOKEN_TIME
from gui import SystemMessages
from gui.impl.auxiliary.rewards_helper import getBackportTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.dialogs.new_year_talisman_gift_dialog_model import NewYearTalismanGiftDialogModel
from gui.impl.gen.view_models.views.lobby.new_year.dialogs.new_year_talisman_gift_dialog_type import NewYearTalismanGiftDialogType
from gui.impl.lobby.loot_box.loot_box_helper import getLootboxBonuses, getLootboxRendererModelPresenter, getTooltipContent
from gui.impl.lobby.loot_box.loot_box_sounds import setOverlayHangarGeneral
from gui.impl.pub.lobby_dialog_window import NYLobbyDialogWindow
from helpers import dependency
from items.components.ny_constants import TOKEN_TALISMAN_BONUS
from new_year.ny_constants import CURRENT_NY_TOYS_BONUS
from frameworks.wulf import ViewSettings, WindowStatus
from gui.impl.pub.dialog_window import DialogContent, DialogButtons, DialogLayer
from gui.impl.gen.view_models.constants.dialog_presets import DialogPresets
from gui.impl.backport import TooltipData
from gui.impl.backport import BackportTooltipWindow
from gui.impl.gen.view_models.constants.base_format_constants import BaseFormatConstants
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
from gui.shared.utils import decorators
from skeletons.new_year import ITalismanSceneController
from gui.impl.gen.view_models.windows.dialog_window_adaptive_settings_model import DialogWindowAdaptiveSettingsModel
from items.components.ny_constants import ToySettings
TalismanAdaptiveSettings = namedtuple('TalismanAdaptiveSettings', ('breakpointSM', 'breakpointML', 'widthSmall', 'widthMedium', 'widthLarge', 'offsetSmall', 'offsetMedium', 'offsetLarge'))
_ANIMATION_SHOW_CONFIRM_OK = 'show_confirm_ok'
_TALISMAN_CONGRAT_GIFT_SETTINGS = TalismanAdaptiveSettings(1400, 1620, 500, 670, 820, 30, 30, 30)
_TALISMAN_SELECT_GIFT_SETTINGS = {ToySettings.ORIENTAL: TalismanAdaptiveSettings(1380, 1620, 470, 670, 820, 30, 30, 30),
 ToySettings.NEW_YEAR: TalismanAdaptiveSettings(1380, 1620, 470, 670, 820, 30, 30, 30),
 ToySettings.CHRISTMAS: TalismanAdaptiveSettings(1380, 1620, 420, 670, 800, 30, 30, 30),
 ToySettings.FAIRYTALE: TalismanAdaptiveSettings(1380, 1620, 470, 670, 820, 30, 30, 30)}

class NewYearTalismanGiftDialog(NYLobbyDialogWindow):
    __slots__ = ('__talismanType', '__dialogContentType')
    __talismanController = dependency.descriptor(ITalismanSceneController)

    def __init__(self, talismanType, dialogType=NewYearTalismanGiftDialogType.SELECT):
        self.__dialogContentType = dialogType
        self.__talismanType = talismanType
        dialogContent = NewYearTalismanGiftDialogContent(talismanType, dialogType)
        super(NewYearTalismanGiftDialog, self).__init__(content=dialogContent, enableBlur=False, layer=DialogLayer.OVERLAY)

    def _initialize(self):
        super(NewYearTalismanGiftDialog, self)._initialize()
        self.__setupDialog(self.__dialogContentType)
        self.__addButtons(self.__dialogContentType)
        self.contentViewModel.onShowCongratButtons += self.__onShowCongratButtons
        setOverlayHangarGeneral(True)
        NewYearSoundsManager.setStylesTalismanSwitchBox(self.__talismanType)
        NewYearSoundsManager.playEvent(NewYearSoundEvents.TALISMAN_GIFT)

    def _finalize(self):
        NewYearSoundsManager.playEvent(NewYearSoundEvents.TALISMAN_GIFT_EXIT)
        setOverlayHangarGeneral(False)
        self.contentViewModel.onShowCongratButtons -= self.__onShowCongratButtons
        super(NewYearTalismanGiftDialog, self)._finalize()

    def __setupDialog(self, dialogType):
        with self.viewModel.transaction() as model:
            model.setPreset(DialogPresets.TRANSPARENT_DEFAULT)
            model.setDialogTitleTextStyle('TalismanSelectViewTitleStyle')
            settings = model.getAdaptiveSettings()
            settings.clear()
            adaptiveSet = DialogWindowAdaptiveSettingsModel()
            adaptiveSet.setContentHorizontalAlign(BaseFormatConstants.ALIGN_RIGHT)
            adaptiveSet.setButtonsHorizontalAlign(BaseFormatConstants.ALIGN_LEFT)
            if dialogType == NewYearTalismanGiftDialogType.CONGRAT:
                model.setIsDividerVisible(False)
                settingsSet = _TALISMAN_CONGRAT_GIFT_SETTINGS
                adaptiveSet.setButtonsHorizontalAlign(BaseFormatConstants.ALIGN_CENTER)
            if dialogType == NewYearTalismanGiftDialogType.SELECT:
                model.setIsDividerVisible(True)
                settingsSet = _TALISMAN_SELECT_GIFT_SETTINGS[self.__talismanType]
            adaptiveSet.setHorizontalChangeBreakpointSM(settingsSet.breakpointSM)
            adaptiveSet.setHorizontalChangeBreakpointML(settingsSet.breakpointML)
            adaptiveSet.setContentHorizontalOffsetSmall(settingsSet.offsetSmall)
            adaptiveSet.setContentHorizontalOffsetMedium(settingsSet.offsetMedium)
            adaptiveSet.setContentHorizontalOffsetLarge(settingsSet.offsetLarge)
            adaptiveSet.setContentWidthSmall(settingsSet.widthSmall)
            adaptiveSet.setContentWidthMedium(settingsSet.widthMedium)
            adaptiveSet.setContentWidthLarge(settingsSet.widthLarge)
            settings.addViewModel(adaptiveSet)
            settings.invalidate()

    def __addButtons(self, dialogType, hideAll=False):
        checkOkBtn = self._getButton(DialogButtons.PURCHASE)
        okBtnTxt = R.strings.ny.newYearTalisman.getBtn()
        cancelBtnTxt = R.strings.ny.newYearTalisman.backBtn()
        if dialogType == NewYearTalismanGiftDialogType.CONGRAT:
            okBtnTxt = R.strings.ny.newYearTalisman.backTreeBtn()
            cancelBtnTxt = R.strings.ny.newYearTalisman.backTalismanBtn()
        if checkOkBtn is None:
            self._addButton(DialogButtons.PURCHASE, okBtnTxt, isFocused=True)
            self._addButton(DialogButtons.CANCEL, cancelBtnTxt, invalidateAll=True)
        else:
            self._getButton(DialogButtons.PURCHASE).setLabel(okBtnTxt)
            self._getButton(DialogButtons.CANCEL).setLabel(cancelBtnTxt)
        if hideAll:
            self._getButton(DialogButtons.PURCHASE).setIsVisible(False)
            self._getButton(DialogButtons.CANCEL).setIsVisible(False)
            self.viewModel.buttons.invalidate()
        return

    def __onShowCongratButtons(self):
        self._getButton(DialogButtons.PURCHASE).setIsVisible(True)
        self._getButton(DialogButtons.CANCEL).setIsVisible(True)
        self.viewModel.buttons.invalidate()

    def _onButtonClick(self, item):
        if not item.getIsEnabled():
            return
        if item.getName() == DialogButtons.CANCEL:
            super(NewYearTalismanGiftDialog, self)._onButtonClick(item)
            return
        if self.__dialogContentType == NewYearTalismanGiftDialogType.SELECT:
            self.__takeGift()
            return
        super(NewYearTalismanGiftDialog, self)._onButtonClick(item)

    @decorators.process('updating')
    def __takeGift(self):
        from new_year.ny_processor import GetTalismanToyProcessor
        result = yield GetTalismanToyProcessor(self.__talismanType).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        if result.success:
            self.__talismanController.setGiftAnimationState(self.__talismanType, _ANIMATION_SHOW_CONFIRM_OK)
        if self.windowStatus != WindowStatus.LOADED:
            return
        if result.success:
            converted = self.__convertGiftToBonuses(result.auxData)
            self.__initCongratFlow(converted)
        else:
            self.destroy()

    @staticmethod
    def __convertGiftToBonuses(rawData):
        toyID, tokenCount = rawData
        token = {'expires': {'at': ENDLESS_TOKEN_TIME},
         'count': tokenCount}
        bonuses, _ = getLootboxBonuses({CURRENT_NY_TOYS_BONUS: {toyID: 1},
         'tokens': {TOKEN_TALISMAN_BONUS: token}})
        return bonuses

    def __initCongratFlow(self, rewards):
        self.__dialogContentType = NewYearTalismanGiftDialogType.CONGRAT
        self.__addButtons(self.__dialogContentType, True)
        self.__setupDialog(self.__dialogContentType)
        NewYearSoundsManager.playEvent(NewYearSoundEvents.TALISMAN_RECEIVING_GIFT)
        self.content.setRewards(self.__dialogContentType, rewards)


class NewYearTalismanGiftDialogContent(DialogContent):
    __slots__ = ('__talismanType', '__dialogType', '__tooltipData')

    def __init__(self, talismanType, dialogType):
        settings = ViewSettings(R.views.lobby.new_year.dialogs.new_year_talisman_gift_dialog.NewYearTalismanGiftDialog())
        settings.model = NewYearTalismanGiftDialogModel()
        super(NewYearTalismanGiftDialogContent, self).__init__(settings)
        self.__talismanType = talismanType
        self.__dialogType = dialogType
        self.__tooltipData = {}

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            window = None
            if tooltipId is not None:
                window = BackportTooltipWindow(self.__tooltipData[tooltipId], self.getParentWindow())
                window.load()
            return window
        else:
            return super(NewYearTalismanGiftDialogContent, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        tooltipData = getBackportTooltipData(event, self.__tooltipData)
        return getTooltipContent(event, tooltipData)

    def setRewards(self, contentType, rewards):
        self.__dialogType = contentType
        self.__setupDialog(rewards)

    def _initialize(self):
        super(NewYearTalismanGiftDialogContent, self)._initialize()
        self.__setupDialog()

    def __setupDialog(self, rewards=None):
        with self.getViewModel().transaction() as model:
            model.setTalismanType(self.__talismanType)
            model.setDialogType(self.__dialogType)
            if self.__dialogType == NewYearTalismanGiftDialogType.SELECT:
                settingsSet = _TALISMAN_SELECT_GIFT_SETTINGS[self.__talismanType]
                model.setHorizontalChangeBreakpointSM(settingsSet.breakpointSM)
                model.setHorizontalChangeBreakpointML(settingsSet.breakpointML)
                model.setContentWidthSmall(settingsSet.widthSmall)
                model.setContentWidthMedium(settingsSet.widthMedium)
                model.setContentWidthLarge(settingsSet.widthLarge)
            if self.__dialogType == NewYearTalismanGiftDialogType.CONGRAT:
                model.setHorizontalChangeBreakpointSM(_TALISMAN_CONGRAT_GIFT_SETTINGS.breakpointSM)
                model.setHorizontalChangeBreakpointML(_TALISMAN_CONGRAT_GIFT_SETTINGS.breakpointML)
                model.setContentWidthSmall(_TALISMAN_CONGRAT_GIFT_SETTINGS.widthSmall)
                model.setContentWidthMedium(_TALISMAN_CONGRAT_GIFT_SETTINGS.widthMedium)
                model.setContentWidthLarge(_TALISMAN_CONGRAT_GIFT_SETTINGS.widthLarge)
                rewardsList = model.getRewards()
                rewardsList.clear()
                for index, reward in enumerate(rewards):
                    formatter = getLootboxRendererModelPresenter(reward)
                    rewardRender = formatter.getModel(reward, index)
                    rewardsList.addViewModel(rewardRender)
                    self.__tooltipData[index] = TooltipData(tooltip=reward.get('tooltip', None), isSpecial=reward.get('isSpecial', False), specialAlias=reward.get('specialAlias', ''), specialArgs=reward.get('specialArgs', None))

                rewardsList.invalidate()
        return
