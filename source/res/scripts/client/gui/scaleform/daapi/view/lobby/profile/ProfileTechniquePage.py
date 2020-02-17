# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/ProfileTechniquePage.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import PROFILE_TECHNIQUE
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.lobby.profile.ProfileUtils import StatisticTypes
from gui.Scaleform.daapi.view.meta.ProfileTechniquePageMeta import ProfileTechniquePageMeta
from gui.Scaleform.genConsts.PROFILE_DROPDOWN_KEYS import PROFILE_DROPDOWN_KEYS

class ProfileTechniquePage(ProfileTechniquePageMeta):

    def _populate(self):
        super(ProfileTechniquePage, self)._populate()
        vehCD = int(self._selectedData.get('itemCD', -1)) if self._selectedData else -1
        accountDossier = self.itemsCache.items.getAccountDossier(None)
        if vehCD in accountDossier.getRandomStats().getVehicles():
            self._battlesType = PROFILE_DROPDOWN_KEYS.ALL
        elif vehCD in accountDossier.getTeam7x7Stats().getVehicles():
            self._battlesType = PROFILE_DROPDOWN_KEYS.TEAM
        elif vehCD in accountDossier.getHistoricalStats().getVehicles():
            self._battlesType = PROFILE_DROPDOWN_KEYS.HISTORICAL
        elif vehCD in accountDossier.getFortBattlesStats().getVehicles():
            self._battlesType = PROFILE_DROPDOWN_KEYS.FORTIFICATIONS_BATTLES
        elif vehCD in accountDossier.getFortSortiesStats().getVehicles():
            self._battlesType = PROFILE_DROPDOWN_KEYS.FORTIFICATIONS_SORTIES
        elif vehCD in accountDossier.getRated7x7Stats().getVehicles():
            self._battlesType = PROFILE_DROPDOWN_KEYS.STATICTEAM
        elif vehCD in accountDossier.getFalloutStats().getVehicles():
            self._battlesType = PROFILE_DROPDOWN_KEYS.FALLOUT
        elif vehCD in accountDossier.getRankedStats().getVehicles():
            self._battlesType = PROFILE_DROPDOWN_KEYS.RANKED
        elif vehCD in accountDossier.getEpicRandomStats().getVehicles():
            self._battlesType = PROFILE_DROPDOWN_KEYS.EPIC_RANDOM
        self.as_setSelectedVehicleIntCDS(vehCD)
        self.as_setTabsDataS([{'id': 'all',
          'label': backport.text(R.strings.profile.profile.tabs.title.allTime()),
          'linkage': 'RegularItemsTabViewUI',
          'selected': True,
          'enabled': True,
          'tooltip': backport.text(R.strings.profile.profile.tabs.tooltip.forAllTime())}, {'id': 'season',
          'label': backport.text(R.strings.profile.profile.tabs.title.season()),
          'linkage': 'RegularItemsTabViewUI',
          'selected': False,
          'enabled': True,
          'tooltip': backport.text(R.strings.profile.profile.tabs.tooltip.forTime(), time='--')}])
        return

    def _getInitData(self, accountDossier=None, isFallout=False):
        initDataResult = super(ProfileTechniquePage, self)._getInitData(accountDossier, isFallout)
        initDataResult['hangarVehiclesLabel'] = backport.text(R.strings.profile.section.technique.window.hangarVehiclesLabel())
        storedData = self._getStorageData()
        initDataResult['isInHangarSelected'] = storedData['isInHangarSelected']
        return initDataResult

    def _getTechniqueListVehicles(self, targetData, addVehiclesThatInHangarOnly=False):
        storedData = self._getStorageData()
        return super(ProfileTechniquePage, self)._getTechniqueListVehicles(targetData, storedData['isInHangarSelected'])

    def _getStorageId(self):
        return PROFILE_TECHNIQUE

    def _sendAccountData(self, targetData, accountDossier):
        super(ProfileTechniquePage, self)._sendAccountData(targetData, accountDossier)
        if self._selectedVehicleIntCD is not None and self._selectedVehicleIntCD not in targetData.getVehicles():
            self.as_setSelectedVehicleIntCDS(-1)
        return

    def setIsInHangarSelected(self, value):
        storageId = self._getStorageId()
        storedData = AccountSettings.getFilter(storageId)
        storedData['isInHangarSelected'] = value
        AccountSettings.setFilter(storageId, storedData)
        vo = {'vehiclesList': self._getTechniqueListVehicles(self._data),
         'available': True}
        if self._data is not None:
            self.as_responseDossierS(self._battlesType, vo, '', self.getEmptyScreenLabel())
        return

    def requestData(self, vehicleId):
        self._receiveVehicleDossier(int(vehicleId), None)
        return

    def invokeUpdate(self):
        super(ProfileTechniquePage, self).invokeUpdate()
        if self._selectedVehicleIntCD is not None:
            self._receiveVehicleDossier(self._selectedVehicleIntCD, None)
        return

    def setSeasonStatisticsFilter(self, value):
        self._statisticType = StatisticTypes.ALL_TIME
        if value == StatisticTypes.SEASON:
            self._statisticType = StatisticTypes.SEASON
        self.invokeUpdate()
