# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/fairplayWindow.py
from gui.impl.dialogs.dialog_template import DialogTemplateView
from gui.impl.dialogs.dialog_template_button import ConfirmButton
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders as Placeholder
from gui.impl.gen.view_models.views.dialogs.template_settings.default_dialog_template_settings import DisplayFlags
from gui.impl.dialogs.sub_views.icon.icon_set import IconSet
from gui.impl.dialogs.sub_views.content.simple_text_content import SimpleTextContent
from gui.impl.dialogs.sub_views.title.simple_text_title import SimpleTextTitle
from historical_battles.gui.impl.dialogs.sub_views.content.text_with_warning_content import TextWithWarning
from gui.impl.dialogs.sub_views.common.simple_text import ImageSubstitution
from gui.impl import backport
from messenger.formatters import TimeFormatter
_DIMMER_ALPHA = 0.7
_FAIR_PLAY_RES = R.strings.hb_lobby.fairPlayWindow

class FairPlayWindow(DialogTemplateView):

    def __init__(self, data={}):
        super(FairPlayWindow, self).__init__()
        self.__isStarted = data.get('isStarted', False)
        reason = data.get('reason', '')
        self.__reason = reason.split(':')[1] if ':' in reason else reason
        self.__banExpiryTime = data.get('banExpiryTime', 0)

    def _onLoading(self, *args, **kwargs):
        if self.__isStarted:
            self.__loadBanInfo()
        else:
            self.__loadUnBanInfo()
        super(FairPlayWindow, self)._onLoading(*args, **kwargs)

    def __loadBanInfo(self):
        resBan = _FAIR_PLAY_RES.ban.dyn(self.__reason)
        self.setBackgroundImagePath(R.images.historical_battles.gui.maps.icons.backgrounds.vignette())
        self.setBackgroundDimmerAlpha(_DIMMER_ALPHA)
        self.setDisplayFlags(DisplayFlags.RESPONSIVEHEADER.value)
        self.setSubView(Placeholder.TITLE, SimpleTextTitle(resBan.header()))
        icon = IconSet(R.images.historical_battles.gui.maps.icons.fairplayWindow.hb_fairplay_window())
        self.setSubView(Placeholder.ICON, icon)
        bodyStr = backport.text(resBan.body(), date='{0}, {1}'.format(TimeFormatter.getShortDateFormat(self.__banExpiryTime), TimeFormatter.getShortTimeFormat(self.__banExpiryTime)))
        self.setSubView(Placeholder.CONTENT, TextWithWarning(bodyStr, resBan.reason(), ImageSubstitution(R.images.historical_battles.gui.maps.icons.fairplayWindow.banIcon(), 'icon', 4, 7, 0, 0)))
        self.addButton(ConfirmButton(resBan.button()))

    def __loadUnBanInfo(self):
        self.setBackgroundDimmerAlpha(_DIMMER_ALPHA)
        self.setDisplayFlags(DisplayFlags.RESPONSIVEHEADER.value)
        self.setSubView(Placeholder.TITLE, SimpleTextTitle(_FAIR_PLAY_RES.unban.header()))
        icon = IconSet(R.images.historical_battles.gui.maps.icons.fairplayWindow.hb_unban_window())
        self.setSubView(Placeholder.ICON, icon)
        self.setSubView(Placeholder.CONTENT, SimpleTextContent(_FAIR_PLAY_RES.unban.body()))
        self.addButton(ConfirmButton(_FAIR_PLAY_RES.unban.button()))
