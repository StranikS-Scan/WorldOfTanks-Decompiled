# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/wt_fairplay_windows.py
from frameworks.wulf import ViewSettings
from gui.impl import backport
from helpers import dependency
from skeletons.gui.game_control import IWhiteTigerController
from gui.impl.dialogs.dialog_template import DialogTemplateView
from gui.impl.dialogs.dialog_template_button import ConfirmButton
from gui.impl.dialogs.sub_views.common.simple_text import ImageSubstitution
from gui.impl.dialogs.sub_views.content.simple_text_content import SimpleTextContent
from gui.impl.dialogs.sub_views.icon.icon_set import IconSet
from gui.impl.dialogs.sub_views.title.simple_text_title import SimpleTextTitle
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders as Placeholder
from gui.impl.gen.view_models.views.dialogs.template_settings.default_dialog_template_settings import DisplayFlags
from gui.impl.pub import ViewImpl
from messenger.formatters import TimeFormatter
from gui.impl.gen.view_models.views.lobby.white_tiger.dialogs.content.text_with_warning_view_model import TextWithWarningViewModel
_DIMMER_ALPHA = 0.7
_FAIR_PLAY_RES = R.strings.white_tiger.fairPlayWindow
_FAIR_PLAY_WARNING_RES = R.strings.white_tiger.fairPlayWarningWindow

class _TextWithWarning(ViewImpl):
    __slots__ = ()

    def __init__(self, mainText, warningText=None, punishmentText=None, warningImageSubstitution=None):
        settings = ViewSettings(R.views.lobby.white_tiger.dialogs.content.TextWithWarning())
        settings.model = TextWithWarningViewModel()
        settings.kwargs = {'mainText': mainText,
         'warningText': warningText,
         'punishmentText': punishmentText,
         'warningImageSubstitution': warningImageSubstitution}
        super(_TextWithWarning, self).__init__(settings)

    def _onLoading(self, mainText, warningText, punishmentText, warningImageSubstitution, *args, **kwargs):
        super(_TextWithWarning, self)._onLoading(*args, **kwargs)
        with self.getViewModel().transaction() as model:
            model.setMainText(mainText)
            if warningText:
                model.setWarningText(warningText)
            if punishmentText:
                model.setPunishmentText(punishmentText)
            imageSubs = model.warningImageSubstitution
            imageSubs.setPath(warningImageSubstitution.resourceID)
            imageSubs.setPlaceholder(warningImageSubstitution.placeholder)
            imageSubs.setMarginTop(warningImageSubstitution.marginTop)
            imageSubs.setMarginRight(warningImageSubstitution.marginRight)
            imageSubs.setMarginBottom(warningImageSubstitution.marginBottom)
            imageSubs.setMarginLeft(warningImageSubstitution.marginLeft)


class WTFairPlayWindow(DialogTemplateView):
    __wtController = dependency.descriptor(IWhiteTigerController)

    def __init__(self, data=None):
        super(WTFairPlayWindow, self).__init__()
        if data is None:
            data = {}
        self.__isStarted = data.get('isStarted', False)
        reason = data.get('reason', '')
        self.__reason = reason.split(':')[1] if ':' in reason else reason
        self.__banExpiryTime = data.get('banExpiryTime', 0)
        return

    def _onLoading(self, *args, **kwargs):
        if self.__isStarted:
            self.__loadBanInfo()
        else:
            self.__loadUnBanInfo()
        super(WTFairPlayWindow, self)._onLoading(*args, **kwargs)

    def __loadBanInfo(self):
        self.setBackgroundImagePath(R.images.white_tiger.gui.maps.icons.backgrounds.vignette())
        self.setBackgroundDimmerAlpha(_DIMMER_ALPHA)
        self.setDisplayFlags(DisplayFlags.RESPONSIVEHEADER.value)
        self.setSubView(Placeholder.TITLE, SimpleTextTitle(_FAIR_PLAY_RES.ban.header()))
        icon = IconSet(R.images.white_tiger.gui.maps.icons.fairplayWindow.wt_fairplay_window())
        self.setSubView(Placeholder.ICON, icon)
        bodyStr = backport.text(_FAIR_PLAY_RES.ban.body(), date='{0}, {1}'.format(TimeFormatter.getShortDateFormat(self.__banExpiryTime), TimeFormatter.getShortTimeFormat(self.__banExpiryTime)))
        self.setSubView(Placeholder.CONTENT, _TextWithWarning(bodyStr, backport.text(_FAIR_PLAY_RES.ban.reason.dyn(self.__reason)()), backport.text(_FAIR_PLAY_RES.punishment()), ImageSubstitution(R.images.white_tiger.gui.maps.icons.fairplayWindow.banIcon(), 'icon', 4, 7, 0, 0)))
        self.addButton(ConfirmButton(_FAIR_PLAY_RES.ban.button()))

    def __loadUnBanInfo(self):
        self.setBackgroundDimmerAlpha(_DIMMER_ALPHA)
        self.setDisplayFlags(DisplayFlags.RESPONSIVEHEADER.value)
        self.setSubView(Placeholder.TITLE, SimpleTextTitle(_FAIR_PLAY_RES.unban.header()))
        icon = IconSet(R.images.white_tiger.gui.maps.icons.fairplayWindow.wt_unban_window())
        self.setSubView(Placeholder.ICON, icon)
        self.setSubView(Placeholder.CONTENT, SimpleTextContent(_FAIR_PLAY_RES.unban.body()))
        self.addButton(ConfirmButton(_FAIR_PLAY_RES.unban.button()))


class WTFairPlayWarningWindow(DialogTemplateView):

    def __init__(self, data):
        super(WTFairPlayWarningWindow, self).__init__()
        self.__reason = data.get('reason', '')

    def _onLoading(self, *args, **kwargs):
        self.setBackgroundImagePath(R.images.white_tiger.gui.maps.icons.backgrounds.vignette())
        self.setBackgroundDimmerAlpha(_DIMMER_ALPHA)
        self.setDisplayFlags(DisplayFlags.RESPONSIVEHEADER.value)
        self.setSubView(Placeholder.TITLE, SimpleTextTitle(_FAIR_PLAY_WARNING_RES.header()))
        icon = IconSet(R.images.white_tiger.gui.maps.icons.fairplayWindow.wt_fairplay_window())
        self.setSubView(Placeholder.ICON, icon)
        self.setSubView(Placeholder.CONTENT, _TextWithWarning(backport.text(_FAIR_PLAY_WARNING_RES.body()), backport.text(_FAIR_PLAY_WARNING_RES.reason.dyn(self.__reason)()), backport.text(_FAIR_PLAY_RES.punishment()), ImageSubstitution(R.images.gui.maps.icons.library.alertIcon2(), 'icon', 3, 7, 0, 0)))
        self.addButton(ConfirmButton(_FAIR_PLAY_WARNING_RES.button()))
        super(WTFairPlayWarningWindow, self)._onLoading(*args, **kwargs)
