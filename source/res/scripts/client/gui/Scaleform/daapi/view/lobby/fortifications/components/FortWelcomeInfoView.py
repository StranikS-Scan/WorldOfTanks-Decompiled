# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/components/FortWelcomeInfoView.py
import Event
from adisp import process
from gui import makeHtmlString
from gui import SystemMessages
from gui.Scaleform.daapi.view.meta.FortWelcomeInfoViewMeta import FortWelcomeInfoViewMeta
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortSoundController import g_fortSoundController
from gui.clans.clan_helpers import ClanListener
from gui.shared.utils.functions import makeTooltip
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared import g_eventBus
from gui.shared.ClanCache import g_clanCache
from gui.shared.events import OpenLinkEvent
from gui.shared.formatters import text_styles
from gui.shared.fortifications.context import CreateFortCtx
from gui.shared.fortifications.settings import CLIENT_FORT_STATE, FORT_RESTRICTION
from helpers import i18n
from debug_utils import LOG_DEBUG, LOG_CURRENT_EXCEPTION
from gui.shared import event_dispatcher as shared_events
from gui.clans.clan_controller import g_clanCtrl

class FortWelcomeInfoView(FortWelcomeInfoViewMeta, FortViewHelper, ClanListener):

    def __init__(self):
        super(FortWelcomeInfoView, self).__init__()
        self._isMyClan = False
        self.onFortCreationRequested = Event.Event()
        self.onFortCreationDone = Event.Event()

    def onClientStateChanged(self, state):
        if not self.isDisposed():
            self.__updateData()

    def onClanMembersListChanged(self):
        if not self.isDisposed():
            self.__updateData()

    def onNavigate(self, code):
        LOG_DEBUG('navigate: %s' % code)
        g_eventBus.handleEvent(OpenLinkEvent(code))

    def setMyClan(self, isMyClan):
        self._isMyClan = isMyClan
        if not self.isDisposed():
            self.__updateData()

    def _populate(self):
        super(FortWelcomeInfoView, self)._populate()
        self.startFortListening()
        self.startClanListening()
        self.__updateData()

    @staticmethod
    def __makeHyperLink(linkType, textId):
        return makeHtmlString('html_templates:lobby/fortifications', 'link', {'linkType': linkType,
         'text': i18n.makeString(textId)})

    def _dispose(self):
        self.stopFortListening()
        self.stopClanListening()
        try:
            self.onFortCreationRequested.clear()
            self.onFortCreationRequested = None
            self.onFortCreationDone.clear()
            self.onFortCreationDone = None
        except:
            LOG_CURRENT_EXCEPTION()

        super(FortWelcomeInfoView, self)._dispose()
        return

    def _getCustomData(self):
        return {'canRoleCreateFortRest': self.fortCtrl.getPermissions().canCreate() and self._isMyClan,
         'canCreateFortLim': self.fortCtrl.getLimits().isCreationValid()[0] and self._isMyClan,
         'joinClanAvailable': not g_clanCache.isInClan and self._isMyClan,
         'clanSearchAvailable': g_clanCtrl.isEnabled()}

    def __updateData(self):
        data = self.getData()
        self.as_setCommonDataS(data)
        self.__updateViewState(data)

    def __updateViewState(self, data):
        state = self.fortState
        warningText = ('', None)
        if state.getStateID() in (CLIENT_FORT_STATE.NO_CLAN, CLIENT_FORT_STATE.NO_CLAN_SUBSCRIBED):
            self.as_setRequirementTextS(self.__getNoClanText())
        elif self.fortCtrl.getPermissions().canCreate():
            result, reason = self.fortCtrl.getLimits().isCreationValid()
            if not result:
                if reason == FORT_RESTRICTION.CREATION_MIN_COUNT:
                    warningText = self.__getNotEnoughMembersText(data)
                elif reason == FORT_RESTRICTION.NOT_AVAILABLE and self.fortCtrl.getPermissions().canCreate() and self._isMyClan:
                    warningText = self.__getFortAlreadyCreatedText()
        else:
            self.as_setRequirementTextS(self.__getClanMemberWelcomeText(data))
        self.as_setWarningTextS(*warningText)
        return None

    def __getNoClanText(self):
        return text_styles.standard(i18n.makeString(FORTIFICATIONS.FORTWELCOMEVIEW_REQUIREMENTCLAN))

    def __getFortAlreadyCreatedText(self):
        return (text_styles.error(i18n.makeString(FORTIFICATIONS.FORTWELCOMEVIEW_ALREADYCREATED)), None)

    def __getNotEnoughMembersText(self, data):
        minClanSize = data.get('minClanSize', 0)
        text = text_styles.alert(i18n.makeString(FORTIFICATIONS.FORTWELCOMEVIEW_WARNING, minClanSize=minClanSize))
        header = i18n.makeString(TOOLTIPS.FORTIFICATION_WELCOME_CANTCREATEFORT_HEADER)
        body = i18n.makeString(TOOLTIPS.FORTIFICATION_WELCOME_CANTCREATEFORT_BODY, minClanSize=minClanSize)
        tooltip = makeTooltip(header, body)
        return (text, tooltip)

    def __getClanMemberWelcomeText(self, data):
        return ''.join((text_styles.standard(i18n.makeString(FORTIFICATIONS.FORTWELCOMEVIEW_REQUIREMENTCOMMANDER)), text_styles.neutral(data.get('clanCommanderName', ''))))

    def onCreateBtnClick(self):
        self.onFortCreationRequested()
        g_fortSoundController.playCreateFort()
        self.requestFortCreation()

    def onClanStateChanged(self, oldStateID, newStateID):
        self.__updateData()

    @process
    def requestFortCreation(self):
        result = yield self.fortProvider.sendRequest(CreateFortCtx('fort/create'))
        if result:
            SystemMessages.g_instance.pushI18nMessage(SYSTEM_MESSAGES.FORTIFICATION_CREATED, type=SystemMessages.SM_TYPE.Warning)
        self.onFortCreationDone()

    def openClanResearch(self):
        shared_events.showClanSearchWindow()
