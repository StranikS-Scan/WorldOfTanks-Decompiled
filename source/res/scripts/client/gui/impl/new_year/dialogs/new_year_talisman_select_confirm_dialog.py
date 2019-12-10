# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/dialogs/new_year_talisman_select_confirm_dialog.py
from collections import namedtuple
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.dialogs.new_year_talisman_select_confirm_dialog_model import NewYearTalismanSelectConfirmDialogModel
from frameworks.wulf import ViewSettings
from gui.impl.pub.dialog_window import DialogContent, DialogButtons, DialogLayer
from gui.impl.gen.view_models.constants.dialog_presets import DialogPresets
from gui.impl.gen.view_models.constants.base_format_constants import BaseFormatConstants
from gui.impl.pub.lobby_dialog_window import NYLobbyDialogWindow
from gui.impl.gen.view_models.windows.dialog_window_adaptive_settings_model import DialogWindowAdaptiveSettingsModel
TalismanAdaptiveSettings = namedtuple('TalismanAdaptiveSettings', ('breakpointSM', 'breakpointML', 'widthSmall', 'widthMedium', 'widthLarge', 'offsetSmall', 'offsetMedium', 'offsetLarge'))
_TALISMAN_SELECT_SETTINGS = TalismanAdaptiveSettings(1380, 1830, 430, 600, 820, 40, 40, 40)

class NewYearTalismanSelectConfirmDialog(NYLobbyDialogWindow):
    __slots__ = ('__talismanType',)

    def __init__(self, talismanType):
        super(NewYearTalismanSelectConfirmDialog, self).__init__(content=NewYearTalismanSelectConfirmDialogContent(talismanType), enableBlur=False, layer=DialogLayer.OVERLAY)
        self.__talismanType = talismanType

    def _initialize(self, *args, **kwargs):
        super(NewYearTalismanSelectConfirmDialog, self)._initialize()
        self.viewModel.setPreset(DialogPresets.TRANSPARENT_DEFAULT)
        self.viewModel.setDialogTitleTextStyle('TalismanSelectViewTitleStyle')
        settings = self.viewModel.getAdaptiveSettings()
        adaptiveSet = DialogWindowAdaptiveSettingsModel()
        adaptiveSet.setContentHorizontalAlign(BaseFormatConstants.ALIGN_RIGHT)
        adaptiveSet.setButtonsHorizontalAlign(BaseFormatConstants.ALIGN_LEFT)
        adaptiveSet.setHorizontalChangeBreakpointSM(_TALISMAN_SELECT_SETTINGS.breakpointSM)
        adaptiveSet.setHorizontalChangeBreakpointML(_TALISMAN_SELECT_SETTINGS.breakpointML)
        adaptiveSet.setContentHorizontalOffsetSmall(_TALISMAN_SELECT_SETTINGS.offsetSmall)
        adaptiveSet.setContentHorizontalOffsetMedium(_TALISMAN_SELECT_SETTINGS.offsetMedium)
        adaptiveSet.setContentHorizontalOffsetLarge(_TALISMAN_SELECT_SETTINGS.offsetLarge)
        adaptiveSet.setContentWidthSmall(_TALISMAN_SELECT_SETTINGS.widthSmall)
        adaptiveSet.setContentWidthMedium(_TALISMAN_SELECT_SETTINGS.widthMedium)
        adaptiveSet.setContentWidthLarge(_TALISMAN_SELECT_SETTINGS.widthLarge)
        settings.addViewModel(adaptiveSet)
        settings.invalidate()
        self._addButton(DialogButtons.PURCHASE, R.strings.ny.newYearTalisman.selectBtn(), isFocused=True)
        self._addButton(DialogButtons.CANCEL, R.strings.ny.newYearTalisman.backBtn(), invalidateAll=True)


class NewYearTalismanSelectConfirmDialogContent(DialogContent):
    __slots__ = ()

    def __init__(self, talismanType):
        content = R.views.lobby.new_year.dialogs.ny_talisman_select_confirm_dialog.NYTalismanSelectConfirmDialog()
        settings = ViewSettings(content)
        settings.model = NewYearTalismanSelectConfirmDialogModel()
        settings.args = (talismanType,)
        super(NewYearTalismanSelectConfirmDialogContent, self).__init__(settings)

    def _initialize(self, talismanType):
        super(NewYearTalismanSelectConfirmDialogContent, self)._initialize()
        with self.getViewModel().transaction() as model:
            model.setTalismanType(talismanType)
            model.setHorizontalChangeBreakpointSM(_TALISMAN_SELECT_SETTINGS.breakpointSM)
            model.setHorizontalChangeBreakpointML(_TALISMAN_SELECT_SETTINGS.breakpointML)
            model.setContentWidthSmall(_TALISMAN_SELECT_SETTINGS.widthSmall)
            model.setContentWidthMedium(_TALISMAN_SELECT_SETTINGS.widthMedium)
            model.setContentWidthLarge(_TALISMAN_SELECT_SETTINGS.widthLarge)
