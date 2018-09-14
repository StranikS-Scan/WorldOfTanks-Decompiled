# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/ProfileTechniquePage.py
from gui.Scaleform.daapi.view.meta.ProfileTechniquePageMeta import ProfileTechniquePageMeta
from gui.Scaleform.locale.PROFILE import PROFILE
from gui.shared.ItemsCache import g_itemsCache
from helpers.i18n import makeString
from gui.Scaleform.genConsts.PROFILE_DROPDOWN_KEYS import PROFILE_DROPDOWN_KEYS

class ProfileTechniquePage(ProfileTechniquePageMeta):

    def __init__(self, *args):
        super(ProfileTechniquePage, self).__init__(*args)
        self.__isInHangarSelected = False

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
        initDataResult['isInHangarSelected'] = self.__isInHangarSelected
        return initDataResult

    def _getTechniqueListVehicles(self, targetData, addVehiclesThatInHangarOnly=False):
        return super(ProfileTechniquePage, self)._getTechniqueListVehicles(targetData, self.__isInHangarSelected)

    def setIsInHangarSelected(self, value):
        self.__isInHangarSelected = value
        self.invokeUpdate()

    def requestData(self, data):
        self._receiveVehicleDossier(data.vehicleId, None)
        return
