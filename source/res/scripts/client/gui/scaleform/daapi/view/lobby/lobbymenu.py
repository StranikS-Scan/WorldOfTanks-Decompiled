# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/LobbyMenu.py
from adisp import process
from gui.Scaleform.daapi.view.common.settings.new_settings_counter import getNewSettings, invalidateSettings
from helpers import i18n, getShortClientVersion
from gui import DialogsInterface, game_control
from gui.app_loader import g_appLoader
from gui.shared import event_dispatcher
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.daapi.view.dialogs import DIALOG_BUTTON_ID
from gui.Scaleform.daapi.view.meta.LobbyMenuMeta import LobbyMenuMeta
from gui.shared.formatters import text_styles
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS

def _getVersionMessage():
    return {'message': '{0} {1}'.format(text_styles.main(i18n.makeString(MENU.PROMO_PATCH_MESSAGE)), text_styles.stats(getShortClientVersion())),
     'label': i18n.makeString(MENU.PROMO_TOARCHIVE),
     'promoEnabel': game_control.g_instance.promo.isPatchPromoAvailable(),
     'tooltip': TOOLTIPS.LOBBYMENU_VERSIONINFOBUTTON}


class LobbyMenu(LobbyMenuMeta):

    def versionInfoClick(self):
        game_control.g_instance.promo.showVersionsPatchPromo()
        self.destroy()

    def settingsClick(self):
        event_dispatcher.showSettingsWindow(redefinedKeyMode=False)

    def onWindowClose(self):
        self.destroy()

    def cancelClick(self):
        self.destroy()

    @process
    def refuseTraining(self):
        isOk = yield DialogsInterface.showI18nConfirmDialog('refuseTraining')
        if isOk:
            event_dispatcher.stopTutorial()
        self.destroy()

    @process
    def logoffClick(self):
        isOk = yield DialogsInterface.showI18nConfirmDialog('disconnect', focusedID=DIALOG_BUTTON_ID.CLOSE)
        if isOk:
            g_appLoader.goToLoginByRQ()

    @process
    def quitClick(self):
        isOk = yield DialogsInterface.showI18nConfirmDialog('quit', focusedID=DIALOG_BUTTON_ID.CLOSE)
        if isOk:
            g_appLoader.quitFromGame()

    def onCounterNeedUpdate(self):
        self.__updateNewSettingsCount()

    def _populate(self):
        super(LobbyMenu, self)._populate()
        self.as_setVersionMessageS(_getVersionMessage())

    def __updateNewSettingsCount(self):
        newSettingsCnt = len(getNewSettings())
        if newSettingsCnt > 0:
            self.as_setSettingsBtnCounterS(str(newSettingsCnt))
