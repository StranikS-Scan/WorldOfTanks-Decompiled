# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/ProfileTechniquePage.py
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.view.lobby.profile.ProfileTechnique import ProfileTechnique
from gui.Scaleform.daapi.view.meta.ProfileTechniquePageMeta import ProfileTechniquePageMeta
from gui.Scaleform.locale.PROFILE import PROFILE
from gui.shared.ItemsCache import g_itemsCache
from helpers.i18n import makeString

class ProfileTechniquePage(ProfileTechnique, ProfileTechniquePageMeta):

    def __init__(self, *args):
        ProfileTechnique.__init__(self, *args)
        ProfileTechniquePageMeta.__init__(self)
        self.__isInHangarSelected = False

    def _sendAccountData(self, targetData, accountDossier):
        if self.__isInHangarSelected:
            vehList = self._getTechniqueListVehicles(targetData, True)
        else:
            vehList = self._getTechniqueListVehicles(targetData, False)
        self.as_responseDossierS(self._battlesType, vehList)

    def _populate(self):
        super(ProfileTechniquePage, self)._populate()
        if self._selectedData is not None:
            intVehCD = int(self._selectedData.get('itemCD'))
            accountDossier = g_itemsCache.items.getAccountDossier(None)
            if intVehCD in accountDossier.getRandomStats().getVehicles():
                self._battlesType = PROFILE.PROFILE_DROPDOWN_LABELS_ALL
            elif intVehCD in accountDossier.getTeam7x7Stats().getVehicles():
                self._battlesType = PROFILE.PROFILE_DROPDOWN_LABELS_TEAM
        self.as_setSelectedVehicleIntCDS(int(self._selectedData.get('itemCD')) if self._selectedData else -1)
        return

    def _getInitData(self):
        initDataResult = super(ProfileTechniquePage, self)._getInitData()
        initDataResult['hangarVehiclesLabel'] = makeString(PROFILE.SECTION_TECHNIQUE_WINDOW_HANGARVEHICLESLABEL)
        initDataResult['isInHangarSelected'] = self.__isInHangarSelected
        return initDataResult

    def setIsInHangarSelected(self, value):
        self.__isInHangarSelected = value
        self.invokeUpdate()

    def requestData(self, data):
        self._receiveVehicleDossier(data.vehicleId, None)
        return
