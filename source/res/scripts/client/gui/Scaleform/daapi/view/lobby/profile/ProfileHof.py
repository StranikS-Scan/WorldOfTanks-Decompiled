# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/ProfileHof.py
from functools import partial
import BigWorld
from adisp import adisp_process
from debug_utils import LOG_WARNING, LOG_ERROR
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency, i18n
from gui.Scaleform import MENU
from gui.shared.formatters import icons
from skeletons.gui.web import IWebController
from skeletons.gui.server_events import IEventsCache
from gui import DialogsInterface
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.hof.hof_helpers import getHofAchievementsRatingUrl, getHofVehiclesRatingUrl, isHofButtonNew, setHofButtonOld, getHofDisabledKeys, onServerSettingsChange
from gui.Scaleform.daapi.view.lobby.hof.web_handlers import createHofWebHandlers
from gui.Scaleform.daapi.view.meta.ProfileHofMeta import ProfileHofMeta
from gui.Scaleform.genConsts.PROFILE_CONSTANTS import PROFILE_CONSTANTS
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE

class ProfileHof(ProfileHofMeta):
    _eventsCache = dependency.descriptor(IEventsCache)
    _clansController = dependency.descriptor(IWebController)
    _errorsStatusMap = {'1004': PROFILE_CONSTANTS.HOF_SPECIAL_CASES,
     '1005': PROFILE_CONSTANTS.HOF_SPECIAL_CASES,
     '1015': PROFILE_CONSTANTS.HOF_SPECIAL_CASES,
     '1016': PROFILE_CONSTANTS.HOF_SPECIAL_CASES,
     '1003': PROFILE_CONSTANTS.HOF_RESULTS_HIDE,
     '1006': PROFILE_CONSTANTS.HOF_RESULTS_EXCLUSION,
     '1007': PROFILE_CONSTANTS.HOF_RESULTS_INCLUSION}
    _requestRetriesCount = 3
    _retryDelay = 0.5
    _bgPath = '../maps/icons/hof/hof_back_landing.png'
    _buttonsWithCounter = (PROFILE_CONSTANTS.HOF_ACHIEVEMENTS_BUTTON, PROFILE_CONSTANTS.HOF_VEHICLES_BUTTON)

    def __init__(self, *args):
        super(ProfileHof, self).__init__(*args)
        self.__status = PROFILE_CONSTANTS.HOF_RESULTS_SHOW
        self.__retriesCount = 0
        self.__isMaintenance = False
        self.__viewDisposed = False
        self.__requestProcessing = False
        self.__retryCallback = None
        return

    def showAchievementsRating(self):
        setHofButtonOld(PROFILE_CONSTANTS.HOF_ACHIEVEMENTS_BUTTON)
        self.__openHofBrowserView(getHofAchievementsRatingUrl())

    def showVehiclesRating(self):
        setHofButtonOld(PROFILE_CONSTANTS.HOF_VEHICLES_BUTTON)
        self.__openHofBrowserView(getHofVehiclesRatingUrl())

    @adisp_process
    def changeStatus(self):
        if self.__status == PROFILE_CONSTANTS.HOF_RESULTS_SHOW:
            success = yield DialogsInterface.showI18nConfirmDialog('hof/excludeRating')
            if success:
                self.__makeRequest(self._clansController.getClanDossier().requestHofUserExclude, PROFILE_CONSTANTS.HOF_RESULTS_EXCLUSION, lambda errorCode: self.__getRatingStatus())
        elif self.__status == PROFILE_CONSTANTS.HOF_RESULTS_HIDE:
            self.__makeRequest(self._clansController.getClanDossier().requestHofUserRestore, PROFILE_CONSTANTS.HOF_RESULTS_INCLUSION, lambda errorCode: self.__getRatingStatus())
        else:
            LOG_WARNING('Something went wrong! Getting actual status.')
            self.__getRatingStatus()

    def onSectionActivated(self):
        if self.lobbyContext.getServerSettings().bwHallOfFame.isStatusEnabled:
            if self.__requestProcessing:
                LOG_WARNING('ProfileHof request canceled: another request is processing')
            else:
                self.__getRatingStatus()
        else:
            self.as_setStatusS(PROFILE_CONSTANTS.HOF_SPECIAL_CASES)

    def _populate(self):
        super(ProfileHof, self)._populate()
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        self.as_setBackgroundS(self._bgPath)
        self.as_setBtnCountersS(self.__getCountersList())

    def _dispose(self):
        if self.__retryCallback:
            LOG_WARNING('ProfileHof request canceled: ProfileHof view was disposed')
            BigWorld.cancelCallback(self.__retryCallback)
        self.__viewDisposed = True
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        super(ProfileHof, self)._dispose()

    def __getCountersList(self):
        counters = []
        for buttonName in self._buttonsWithCounter:
            if isHofButtonNew(buttonName):
                counters.append({'componentId': buttonName,
                 'count': '1'})

        return counters

    def __getRatingStatus(self):

        def handleError(errorCode):
            status = self._errorsStatusMap.get(errorCode)
            if status:
                self.__status = status
                self.as_setStatusS(status)
            else:
                LOG_ERROR('Unknown error code: ' + str(errorCode))

        self.__makeRequest(self._clansController.getClanDossier().requestHofUserInfo, PROFILE_CONSTANTS.HOF_RESULTS_SHOW, handleError)

    @adisp_process
    def __makeRequest(self, requestFunc, successStatus, errorCallback):
        if self.__retriesCount == 0:
            if not self.__isMaintenance:
                self.as_showWaitingS(backport.msgid(R.strings.waiting.hof.loading()))
            self.__requestProcessing = True
        else:
            self.__retryCallback = None
        response = yield requestFunc()
        if self.__viewDisposed:
            LOG_WARNING('ProfileHof request canceled: ProfileHof view was disposed')
            return
        else:
            if response:
                self.__refreshRequest()
                if self.__isMaintenance:
                    self.as_hideServiceViewS()
                    self.as_setBtnCountersS(self.__getCountersList())
                    self.__isMaintenance = False
                errors = response.getErrors()
                if not errors:
                    self.__status = successStatus
                    self.as_setStatusS(successStatus)
                else:
                    errorCallback(errors[0])
            elif self.__retriesCount < self._requestRetriesCount:
                self.__retriesCount += 1
                self.__retryCallback = BigWorld.callback(self._retryDelay, partial(self.__makeRequest, requestFunc, successStatus, errorCallback))
            else:
                self.__refreshRequest()
                if not self.__isMaintenance:
                    self.__isMaintenance = True
                    header = icons.alert() + i18n.makeString(MENU.BROWSER_DATAUNAVAILABLE_HEADER)
                    description = i18n.makeString(MENU.BROWSER_DATAUNAVAILABLE_DESCRIPTION)
                    self.as_showServiceViewS(header, description)
                    self.as_setBtnCountersS([])
            return

    def __refreshRequest(self):
        self.__retriesCount = 0
        if not self.__isMaintenance:
            self.as_hideWaitingS()
        self.__requestProcessing = False

    def __openHofBrowserView(self, url):
        self._eventsCache.onProfileVisited()
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.BROWSER_VIEW), ctx={'url': url,
         'returnAlias': VIEW_ALIAS.LOBBY_PROFILE,
         'allowRightClick': True,
         'webHandlers': createHofWebHandlers(),
         'selectedAlias': VIEW_ALIAS.PROFILE_HOF,
         'disabledKeys': getHofDisabledKeys(),
         'onServerSettingsChange': onServerSettingsChange}), EVENT_BUS_SCOPE.LOBBY)

    def __onServerSettingChanged(self, diff):
        if 'hallOfFame' in diff:
            self.onSectionActivated()
