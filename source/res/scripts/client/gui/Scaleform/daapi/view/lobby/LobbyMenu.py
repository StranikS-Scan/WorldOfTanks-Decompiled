# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/LobbyMenu.py
import BigWorld
import constants
from PlayerEvents import g_playerEvents as events
from account_helpers.AccountSettings import AccountSettings, LOBBY_MENU_MANUAL_TRIGGER_SHOWN, LOBBY_MENU_BOOTCAMP_TRIGGER_SHOWN
from account_helpers.counter_settings import getCountNewSettings
from adisp import adisp_process
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.impl import backport
from gui.impl.gen import R
from wg_async import wg_async, wg_await
from gui import DialogsInterface, SystemMessages
from gui.Scaleform.daapi.view.dialogs import DIALOG_BUTTON_ID
from gui.Scaleform.daapi.view.meta.LobbyMenuMeta import LobbyMenuMeta
from gui.Scaleform.genConsts.MENU_CONSTANTS import MENU_CONSTANTS
from gui.Scaleform.locale.BOOTCAMP import BOOTCAMP
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.impl.dialogs import dialogs
from gui.impl.lobby.account_completion.curtain.curtain_view import CurtainWindow
from gui.prb_control import prbEntityProperty
from gui.shared import event_dispatcher, EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles, icons
from gui.shared.tutorial_helper import getTutorialGlobalStorage
from gui.sounds.ambients import LobbySubViewEnv
from helpers import i18n, getShortClientVersion, dependency, getFullClientVersion
from skeletons.gameplay import IGameplayLogic
from skeletons.gui.game_control import IBootcampController, IDemoAccCompletionController
from skeletons.gui.game_control import IManualController
from skeletons.gui.game_control import IPromoController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from tutorial.control.context import GLOBAL_FLAG

def _getVersionMessage():
    return ('{0} {1}'.format(text_styles.main(i18n.makeString(MENU.PROMO_PATCH_MESSAGE)), text_styles.stats(getShortClientVersion())),)


class LobbyMenu(LobbyMenuMeta):
    __sound_env__ = LobbySubViewEnv
    promo = dependency.descriptor(IPromoController)
    bootcamp = dependency.descriptor(IBootcampController)
    lobbyContext = dependency.descriptor(ILobbyContext)
    gameplay = dependency.descriptor(IGameplayLogic)
    manualController = dependency.descriptor(IManualController)
    gui = dependency.descriptor(IGuiLoader)
    demoAccController = dependency.descriptor(IDemoAccCompletionController)

    def __init__(self, *args, **kwargs):
        super(LobbyMenu, self).__init__(*args, **kwargs)
        self.__bootcampBtnIsVisible = True
        self.__manualBtnIsVisible = True
        self.__postBtnIsVisible = True

    @prbEntityProperty
    def prbEntity(self):
        pass

    @adisp_process
    def postClick(self):
        self.destroy()
        navigationPossible = yield self.lobbyContext.isHeaderNavigationPossible()
        if navigationPossible:
            self.promo.showFieldPost()

    def settingsClick(self):
        event_dispatcher.showSettingsWindow(redefinedKeyMode=False)

    def onWindowClose(self):
        self.destroy()

    def cancelClick(self):
        self.destroy()

    def onEscapePress(self):
        self.destroy()

    @adisp_process
    def refuseTraining(self):
        isOk = yield DialogsInterface.showI18nConfirmDialog('refuseTraining')
        if isOk:
            event_dispatcher.stopTutorial()
        self.destroy()

    @adisp_process
    def logoffClick(self):
        isOk = yield DialogsInterface.showI18nConfirmDialog('disconnect', focusedID=DIALOG_BUTTON_ID.CLOSE)
        if isOk:
            self.gameplay.goToLoginByDisconnectRQ()

    @wg_async
    def quitClick(self):
        isOk = yield wg_await(dialogs.quitGame(self.getParentWindow()))
        if isOk:
            self.gameplay.quitFromGame()

    def onCounterNeedUpdate(self):
        self.__updateNewSettingsCount()

    def bootcampClick(self):
        if not self.bootcamp.canRun() and not self.bootcamp.isInBootcamp():
            SystemMessages.pushI18nMessage('#system_messages:prebattle/bootcamp/inOtherQueue', type=SystemMessages.SM_TYPE.Warning)
            self.destroy()
        else:
            self.bootcamp.runBootcamp()

    def manualClick(self):
        if self.manualController.isActivated():
            view = self.manualController.getView()
            if view is not None:
                self.destroy()
            else:
                self.manualController.show()
        return

    def showLegal(self):
        self.fireEvent(event_dispatcher.events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LEGAL_INFO_TOP_WINDOW)), EVENT_BUS_SCOPE.LOBBY)

    def _populate(self):
        super(LobbyMenu, self)._populate()
        self.__addListeners()
        isDemoAccountWithOpenedCurtain = self.__getIsDemoAccountWithOpenedCurtain()
        self.__updateUIState(isDemoAccountWithOpenedCurtain)
        self.__updateBootcampBtn(isDemoAccountWithOpenedCurtain)
        if isDemoAccountWithOpenedCurtain:
            self.as_showManualButtonS(False)
        self.as_setVersionMessageS(text_styles.main(getFullClientVersion()))
        self.as_setCopyrightS(backport.text(R.strings.menu.copy()), backport.text(R.strings.menu.legal()))
        self.__updateVersionState()
        self.__updateManualBtn()
        if self.__manualBtnIsVisible:
            self.as_setManualButtonIconS(icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_MANUALICON, 24, 24, -6, 0))
        self.__updatePostButton()
        if self.__postBtnIsVisible:
            self.__setPostButtonsIcons()

    def _dispose(self):
        globalStorage = getTutorialGlobalStorage()
        if globalStorage.getValue(GLOBAL_FLAG.LOBBY_MENU_ITEM_MANUAL):
            globalStorage.setValue(GLOBAL_FLAG.LOBBY_MENU_ITEM_MANUAL, False)
            AccountSettings.setManualData(LOBBY_MENU_MANUAL_TRIGGER_SHOWN, True)
        if globalStorage.getValue(GLOBAL_FLAG.LOBBY_MENU_ITEM_BOOTCAMP):
            globalStorage.setValue(GLOBAL_FLAG.LOBBY_MENU_ITEM_BOOTCAMP, False)
            AccountSettings.setManualData(LOBBY_MENU_BOOTCAMP_TRIGGER_SHOWN, True)
        self.__removeListeners()
        super(LobbyMenu, self)._dispose()

    def __getIsDemoAccountWithOpenedCurtain(self):
        return self.demoAccController.isDemoAccount and CurtainWindow.isOpened()

    def __updateBootcampBtn(self, isDemoAccountWithOpenedCurtain):
        enabledOnServer = self.lobbyContext.getServerSettings().isBootcampEnabled()
        isInBootcamp = self.bootcamp.isInBootcamp()
        disabledBySPAFlag = BigWorld.player().spaFlags.getFlag(constants.SPA_ATTRS.BOOTCAMP_DISABLED)
        isPlayerEntityChanging = events.isPlayerEntityChanging
        isVisible = (enabledOnServer or isInBootcamp) and not disabledBySPAFlag and not isPlayerEntityChanging and not isDemoAccountWithOpenedCurtain
        if self.__bootcampBtnIsVisible != isVisible:
            self.as_showBootcampButtonS(isVisible)
            self.__bootcampBtnIsVisible = isVisible
        if isVisible:
            self.__updateBootcampBtnContent(enabledOnServer)
            triggerIsShown = AccountSettings.getManualData(LOBBY_MENU_BOOTCAMP_TRIGGER_SHOWN)
            if not triggerIsShown and not self.bootcamp.hasFinishedBootcampBefore() and not isInBootcamp:
                getTutorialGlobalStorage().setValue(GLOBAL_FLAG.LOBBY_MENU_ITEM_BOOTCAMP, True)

    def __updateManualBtn(self):
        isVisible = self.manualController.isActivated() and not self.bootcamp.isInBootcamp() and not self.__isInQueue()
        isVisible = isVisible and not self.__getIsDemoAccountWithOpenedCurtain()
        if self.__manualBtnIsVisible != isVisible:
            self.as_showManualButtonS(isVisible)
            self.__manualBtnIsVisible = isVisible
        if self.__manualBtnIsVisible and not AccountSettings.getManualData(LOBBY_MENU_MANUAL_TRIGGER_SHOWN):
            getTutorialGlobalStorage().setValue(GLOBAL_FLAG.LOBBY_MENU_ITEM_MANUAL, True)

    def __updateVersionState(self):
        self.as_showVersionS(not self.__isInQueue())

    def __updateBootcampBtnContent(self, enabledOnServer):
        bootcampIcon = RES_ICONS.MAPS_ICONS_BOOTCAMP_MENU_MENUBOOTCAMPICON
        bootcampIconSource = icons.makeImageTag(bootcampIcon, 24, 24, -6, 0)
        label = None
        if self.bootcamp.isInBootcamp():
            label = BOOTCAMP.REQUEST_BOOTCAMP_FINISH
        elif enabledOnServer:
            runCount = self.bootcamp.runCount()
            label = BOOTCAMP.REQUEST_BOOTCAMP_RETURN if runCount > 0 else BOOTCAMP.REQUEST_BOOTCAMP_START
        if label is not None:
            self.as_setBootcampButtonLabelS(label, bootcampIconSource)
        return

    def __updateUIState(self, isDemoAccountWithOpenedCurtain):
        state = MENU_CONSTANTS.STATE_SHOW_ALL
        if self.bootcamp.isInBootcamp() or isDemoAccountWithOpenedCurtain:
            state = MENU_CONSTANTS.STATE_HIDE_ALL
        elif constants.IS_CHINA:
            state = MENU_CONSTANTS.STATE_SHOW_SERVER_NAME
        elif not constants.IS_SHOW_SERVER_STATS:
            state = MENU_CONSTANTS.STATE_HIDE_SERVER_STATS_ITEM
        self.as_setMenuStateS(state)

    def __setPostButtonsIcons(self):
        postIconClose = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_POST_CLOSE, 26, 22, -5, 0)
        postIconOpen = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_POST_OPEN, 26, 22, -5, 0)
        self.as_setPostButtonIconsS(postIconClose, postIconOpen)

    def __isInQueue(self):
        return self.prbEntity and self.prbEntity.isInQueue()

    def __updateNewSettingsCount(self):
        userLogin = getattr(BigWorld.player(), 'name', '')
        if userLogin == '':
            return
        toShow, toHide = [], []
        counts = {'settingsBtn': getCountNewSettings(),
         'postBtn': self.promo.getPromoCount()}
        if not self.bootcamp.isInBootcamp():
            counts['manualBtn'] = self.manualController.getNewContentCount()
        for componentID, count in counts.iteritems():
            if count > 0:
                toShow.append({'componentId': componentID,
                 'count': str(count)})
            toHide.append(componentID)

        if toShow:
            self.as_setCounterS(toShow)
        if toHide:
            self.as_removeCounterS(toHide)

    def __addListeners(self):
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        self.promo.onPromoCountChanged += self.__updateNewSettingsCount

    def __removeListeners(self):
        self.promo.onPromoCountChanged -= self.__updateNewSettingsCount
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged

    def __onServerSettingChanged(self, diff):
        if 'isManualEnabled' in diff:
            self.__updateManualBtn()
        if 'isFieldPostEnabled' in diff:
            self.__updatePostButton()

    def __updatePostButton(self):
        isVisible = self.promo.isActive() and not self.__isInQueue() and not self.__getIsDemoAccountWithOpenedCurtain()
        if self.__postBtnIsVisible != isVisible:
            self.as_setPostButtonVisibleS(isVisible)
            self.__postBtnIsVisible = isVisible
