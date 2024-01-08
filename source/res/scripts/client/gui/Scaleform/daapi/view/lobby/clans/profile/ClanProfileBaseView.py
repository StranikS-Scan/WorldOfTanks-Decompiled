# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/clans/profile/ClanProfileBaseView.py
from adisp import adisp_process
from gui import SystemMessages
from gui.Scaleform.daapi.view.meta.ClanProfileBaseViewMeta import ClanProfileBaseViewMeta
from gui.Scaleform.locale.CLANS import CLANS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.clans import formatters as clans_fmts
from gui.clans.clan_helpers import ClanListener
from gui.clans.data_wrapper.utils import formatField
from gui.clans.settings import CLIENT_CLAN_RESTRICTIONS as RES
from gui.impl import backport
from gui.shared.formatters import text_styles
from gui.shared.view_helpers.emblems import ClanEmblemsHelper
from gui.wgcg.base.contexts import CreateApplicationCtx
from helpers import i18n
_JOIN_BTN_ACTION_ID = 'join'

class ClanProfileBaseView(ClanProfileBaseViewMeta, ClanEmblemsHelper, ClanListener):

    def __init__(self):
        super(ClanProfileBaseView, self).__init__()
        self._clanDossier = None
        self.__headerBtnStates = None
        self._dummyMustBeShown = False
        return

    def setClanDossier(self, clanDossier):
        self._clanDossier = clanDossier
        self._updateClanEmblem(clanDossier.getDbID())

    def onHeaderButtonClick(self, actionID):
        if actionID == _JOIN_BTN_ACTION_ID:
            self._sendApplication()

    def onClanEmblem128x128Received(self, clanDbID, emblem):
        self.as_setClanEmblemS(self.getMemoryTexturePath(emblem))

    def _populate(self):
        super(ClanProfileBaseView, self)._populate()
        self.startClanListening()
        self._updateDummy()
        self._initHeaderBtnStates()

    def onClanEnableChanged(self, enabled):
        self._updateDummy()

    def onAccountWebVitalInfoChanged(self, fieldName, value):
        self._updateHeaderState()

    def onClanWebVitalInfoChanged(self, clanDbID, fieldName, value):
        if clanDbID == self._clanDossier.getDbID():
            self._updateHeaderState()

    def _dispose(self):
        self._clanDossier = None
        self.stopClanListening()
        super(ClanProfileBaseView, self)._dispose()
        return

    @adisp_process
    def _sendApplication(self):
        self.as_showWaitingS(True)
        context = CreateApplicationCtx([self._clanDossier.getDbID()])
        result = yield self.webCtrl.sendRequest(context, allowDelay=True)
        if result.isSuccess():
            clanInfo = yield self._clanDossier.requestClanInfo()
            SystemMessages.pushMessage(clans_fmts.getAppSentSysMsg(clanInfo.getClanName(), clanInfo.getTag()))
            self._onAppSuccessfullySent()
        self.as_showWaitingS(False)

    def _onAppSuccessfullySent(self):
        self._updateHeaderState()

    def _updateClanInfo(self, clanInfo):
        creationDate = i18n.makeString(CLANS.CLAN_HEADER_CREATIONDATE, creationDate=formatField(getter=clanInfo.getCreatedAt, formatter=backport.getShortDateFormat))
        self.as_setClanInfoS({'name': formatField(getter=clanInfo.getFullName),
         'bgIcon': RES_ICONS.MAPS_ICONS_CLANS_CLAN_CARD_HEADER,
         'creationDate': creationDate})

    def _updateClanEmblem(self, clanDbID):
        self.requestClanEmblem128x128(clanDbID)

    def _updateHeaderState(self):
        canSendApplication = self.webCtrl.getLimits().canSendApplication(self._clanDossier)
        self.as_setHeaderStateS(self.__headerBtnStates.get(canSendApplication.reason) or self._getHeaderButtonStateVO())

    def _getHeaderButtonStateVO(self, actionBtnVisible=False, actionBtnLabel=None, iconBtnVisible=False, topTFVisible=False, middleTFVisible=False, actionId=None, actionBtnTooltip=None, middleTF=None, topTF=None):
        return {'actionBtnVisible': actionBtnVisible,
         'iconBtnVisible': iconBtnVisible,
         'topTFVisible': topTFVisible,
         'middleTFVisible': middleTFVisible,
         'actionId': actionId,
         'middleTF': middleTF,
         'actionBtnTooltip': actionBtnTooltip,
         'actionBtnLabel': actionBtnLabel,
         'topTF': topTF}

    def _initHeaderBtnStates(self):
        self.__headerBtnStates = {RES.NO_RESTRICTIONS: self._getHeaderButtonStateVO(True, i18n.makeString(CLANS.CLAN_HEADER_SENDREQUESTBTN), actionId=_JOIN_BTN_ACTION_ID, actionBtnTooltip=CLANS.CLAN_HEADER_SENDREQUESTBTN_TOOLTIP),
         RES.CLAN_APPLICATION_ALREADY_SENT: self._getHeaderButtonStateVO(middleTFVisible=True, middleTF=CLANS.CLAN_HEADER_REQUESTSENT)}
        return self.__headerBtnStates

    def _showWaiting(self):
        self.as_showWaitingS(True)

    def _hideWaiting(self):
        self.as_showWaitingS(False)

    def _updateDummy(self):
        if self.webCtrl.isAvailable() and not self._dummyMustBeShown:
            self.as_hideDummyS()
        else:
            self.as_showDummyS({'iconSource': RES_ICONS.MAPS_ICONS_LIBRARY_ALERTBIGICON,
             'htmlText': str().join((text_styles.middleTitle(i18n.makeString(CLANS.CLANPROFILE_MAINWINDOW_DUMMY_HEADER)), clans_fmts.getHtmlLineDivider(3), text_styles.main(i18n.makeString(CLANS.CLANPROFILE_MAINWINDOW_DUMMY_BODY)))),
             'alignCenter': False,
             'btnVisible': False,
             'btnLabel': '',
             'btnTooltip': ''})
