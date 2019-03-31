# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/Profile.py
# Compiled at: 2018-11-29 14:33:44
import BigWorld, time
import account_helpers
from adisp import process
from gui import SystemMessages
from helpers.i18n import makeString
from helpers.time_utils import makeLocalServerTime
from gui.Scaleform.windows import UIInterface
from gui.Scaleform.utils.requesters import StatsRequester
from gui.Scaleform.utils import dossiers_utils
from PlayerEvents import g_playerEvents
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.utils.gui_items import formatPrice
from debug_utils import LOG_DEBUG

class Profile(UIInterface):

    def populateUI(self, proxy):
        UIInterface.populateUI(self, proxy)
        self.uiHolder.movie.backgroundAlpha = 0
        self.uiHolder.movie.wg_inputKeyMode = 1
        self.uiHolder.addExternalCallbacks({'profile.getStat': self.getStat,
         'profile.getStatsList': self.getStatsList})
        g_playerEvents.onClientUpdated += self.setValues
        g_playerEvents.onDossiersResync += self.setValues
        self.setValues()

    def dispossessUI(self):
        self.uiHolder.removeExternalCallbacks('profile.getStat', 'profile.getStatsList')
        g_playerEvents.onClientUpdated -= self.setValues
        g_playerEvents.onDossiersResync -= self.setValues
        UIInterface.dispossessUI(self)

    def setValues(self, *args):
        self.__updateStatsList()
        Waiting.hide('loadPage')

    @process
    def getStatsList(self, cid):
        dossier = yield StatsRequester().getAccountDossier()
        self.call('profile.setStatsList', dossiers_utils.getDossierVehicleList(dossier))

    @process
    def __updateStatsList(self):
        self.uiHolder.updateAccountInfo()
        dossier = yield StatsRequester().getAccountDossier()
        clanInfo = yield StatsRequester().getClanInfo()
        clanDBID = yield StatsRequester().getClanDBID()
        self.call('profile.setCommonInfo', dossiers_utils.getCommonInfo(BigWorld.player().name, dossier, clanInfo, None))
        if clanDBID is not None and clanDBID != 0:
            tID = 'userInfoId' + BigWorld.player().name
            success = yield dossiers_utils.getClanEmblemTextureID(clanDBID, True, tID)
            if success:
                self.call('profile.setClanEmblem', [tID])
        return

    @process
    def getStat(self, callBackId, vehTypeId):
        Waiting.show('loadStats')
        if vehTypeId == 'ALL':
            dossier = yield StatsRequester().getAccountDossier()
            data = dossiers_utils.getDossierTotalBlocks(dossier)
            medals = dossiers_utils.getDossierMedals(dossier)
        else:
            dossier = yield StatsRequester().getVehicleDossier(vehTypeId)
            data = dossiers_utils.getDossierVehicleBlocks(dossier, vehTypeId)
            medals = dossiers_utils.getDossierMedals(dossier)
        self.call('profile.setMedals', medals)
        self.call('profile.setStat', data)
        Waiting.hide('loadStats')
