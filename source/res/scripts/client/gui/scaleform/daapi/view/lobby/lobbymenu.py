# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/LobbyMenu.py
import BigWorld
from adisp import process
from gui import DialogsInterface
from gui.Scaleform.daapi.view.common.settings.new_settings_counter import getNewSettings
from gui.Scaleform.daapi.view.dialogs import DIALOG_BUTTON_ID
from gui.Scaleform.daapi.view.meta.LobbyMenuMeta import LobbyMenuMeta
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.app_loader import g_appLoader
from gui.shared import event_dispatcher
from gui.shared.formatters import text_styles
from helpers import i18n, getShortClientVersion, dependency
from skeletons.gui.game_control import IPromoController

def _getVersionMessage(promo):
    return {'message': '{0} {1}'.format(text_styles.main(i18n.makeString(MENU.PROMO_PATCH_MESSAGE)), text_styles.stats(getShortClientVersion())),
     'label': i18n.makeString(MENU.PROMO_TOARCHIVE),
     'promoEnabel': promo.isPatchPromoAvailable(),
     'tooltip': TOOLTIPS.LOBBYMENU_VERSIONINFOBUTTON}


class LobbyMenu(LobbyMenuMeta):
    promo = dependency.descriptor(IPromoController)

    def versionInfoClick(self):
        self.promo.showVersionsPatchPromo()
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
        self.as_setVersionMessageS(_getVersionMessage(self.promo))

    def __updateNewSettingsCount(self):
        userLogin = getattr(BigWorld.player(), 'name', '')
        if userLogin == '':
            return
        newSettingsCnt = len(getNewSettings())
        if newSettingsCnt > 0:
            self.as_setSettingsBtnCounterS(str(newSettingsCnt))
        else:
            self.as_removeSettingsBtnCounterS()
