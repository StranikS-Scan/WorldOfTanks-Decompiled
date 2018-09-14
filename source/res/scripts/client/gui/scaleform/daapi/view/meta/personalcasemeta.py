# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PersonalCaseMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class PersonalCaseMeta(AbstractWindowView):

    def dismissTankman(self, inventoryID):
        self._printOverrideError('dismissTankman')

    def unloadTankman(self, invengoryid, currentVehicleID):
        self._printOverrideError('unloadTankman')

    def getCommonData(self):
        self._printOverrideError('getCommonData')

    def getDossierData(self):
        self._printOverrideError('getDossierData')

    def getRetrainingData(self):
        self._printOverrideError('getRetrainingData')

    def retrainingTankman(self, inventoryID, innationID, tankmanCostTypeIndex):
        self._printOverrideError('retrainingTankman')

    def getSkillsData(self):
        self._printOverrideError('getSkillsData')

    def getDocumentsData(self):
        self._printOverrideError('getDocumentsData')

    def addTankmanSkill(self, invengoryID, skillName):
        self._printOverrideError('addTankmanSkill')

    def dropSkills(self):
        self._printOverrideError('dropSkills')

    def changeTankmanPassport(self, invengoryID, firstNameID, firstNameGroup, lastNameID, lastNameGroup, iconID, iconGroup):
        self._printOverrideError('changeTankmanPassport')

    def openExchangeFreeToTankmanXpWindow(self):
        self._printOverrideError('openExchangeFreeToTankmanXpWindow')

    def openChangeRoleWindow(self):
        self._printOverrideError('openChangeRoleWindow')

    def as_setCommonDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setCommonData(data)

    def as_setDossierDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setDossierData(data)

    def as_setRetrainingDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setRetrainingData(data)

    def as_setSkillsDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setSkillsData(data)

    def as_setDocumentsDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setDocumentsData(data)
