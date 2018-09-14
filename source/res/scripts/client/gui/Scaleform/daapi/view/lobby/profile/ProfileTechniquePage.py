# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/ProfileTechniquePage.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import PROFILE_TECHNIQUE
from gui.Scaleform.daapi.view.meta.ProfileTechniquePageMeta import ProfileTechniquePageMeta
from gui.Scaleform.locale.PROFILE import PROFILE
from gui.shared.ItemsCache import g_itemsCache
from helpers.i18n import makeString
from gui.Scaleform.genConsts.PROFILE_DROPDOWN_KEYS import PROFILE_DROPDOWN_KEYS

class ProfileTechniquePage(ProfileTechniquePageMeta):

    def _populate(self):
        super(ProfileTechniquePage, self)._populate()
        if self._selectedData is not None:
            intVehCD = int(self._selectedData.get('itemCD'))
            accountDossier = g_itemsCache.items.getAccountDossier(None)
            if intVehCD in accountDossier.getRandomStats().getVehicles():
                self._battlesType = PROFILE_DROPDOWN_KEYS.ALL
            elif intVehCD in accountDossier.getTeam7x7Stats().getVehicles():
                self._battlesType = PROFILE_DROPDOWN_KEYS.TEAM
            elif intVehCD in accountDossier.getHistoricalStats().getVehicles():
                self._battlesType = PROFILE_DROPDOWN_KEYS.HISTORICAL
            elif intVehCD in accountDossier.getFortBattlesStats().getVehicles():
                self._battlesType = PROFILE_DROPDOWN_KEYS.FORTIFICATIONS_BATTLES
            elif intVehCD in accountDossier.getFortSortiesStats().getVehicles():
                self._battlesType = PROFILE_DROPDOWN_KEYS.FORTIFICATIONS_SORTIES
            elif intVehCD in accountDossier.getRated7x7Stats().getVehicles():
                self._battlesType = PROFILE_DROPDOWN_KEYS.STATICTEAM
            elif intVehCD in accountDossier.getFalloutStats().getVehicles():
                self._battlesType = PROFILE_DROPDOWN_KEYS.FALLOUT
        self.as_setSelectedVehicleIntCDS(int(self._selectedData.get('itemCD')) if self._selectedData else -1)
        return

    def _getInitData(self, accountDossier=None, isFallout=False):
        initDataResult = super(ProfileTechniquePage, self)._getInitData(accountDossier, isFallout)
        initDataResult['hangarVehiclesLabel'] = makeString(PROFILE.SECTION_TECHNIQUE_WINDOW_HANGARVEHICLESLABEL)
        storedData = self._getStorageData()
        initDataResult['isInHangarSelected'] = storedData['isInHangarSelected']
        return initDataResult

    def _getTechniqueListVehicles(self, targetData, addVehiclesThatInHangarOnly=False):
        storedData = self._getStorageData()
        return super(ProfileTechniquePage, self)._getTechniqueListVehicles(targetData, storedData['isInHangarSelected'])

    def _getStorageId(self):
        return PROFILE_TECHNIQUE

    def setIsInHangarSelected(self, value):
        storageId = self._getStorageId()
        storedData = AccountSettings.getFilter(storageId)
        storedData['isInHangarSelected'] = value
        AccountSettings.setFilter(storageId, storedData)
        if self._data is not None:
            self.as_responseDossierS(self._battlesType, self._getTechniqueListVehicles(self._data), '', self.getEmptyScreenLabel())
        return

    def requestData(self, vehicleId):
        self._receiveVehicleDossier(int(vehicleId), None)
        return
