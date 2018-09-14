# Embedded file name: scripts/client/gui/shared/fortifications/FortBuilding.py
from FortifiedRegionBase import BuildingDescr
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.shared.formatters import time_formatters
from gui.shared.gui_items import HasStrCD
from helpers import time_utils, i18n

class FortBuilding(BuildingDescr, HasStrCD):

    def __init__(self, buildingCompactDescr = None, typeID = None):
        BuildingDescr.__init__(self, buildingCompactDescr, typeID=typeID)
        HasStrCD.__init__(self, buildingCompactDescr or self.makeCompactDescr())

    @property
    def userName(self):
        from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
        return i18n.makeString(FORTIFICATIONS.buildings_buildingname(FortViewHelper.getBuildingUIDbyID(self.typeID)))

    def getUserLevel(self, nextLevel = False):
        from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_formatters
        level = self.level
        if nextLevel:
            level += 1
        return fort_formatters.getTextLevel(level)

    def hasStorageToExport(self):
        from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
        step = FortViewHelper.fortCtrl.getFort().getDefResStep()
        return self.storage >= step

    def hasSpaceToImport(self):
        from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
        step = FortViewHelper.fortCtrl.getFort().getDefResStep()
        space = self.levelRef.storage - self.storage
        return space >= step

    def isInCooldown(self):
        return self.getEstimatedCooldown() > 0

    def isInProduction(self):
        return self.getProductionCooldown() > 0

    def hasTimer(self):
        return self.isInCooldown() or self.isInProduction()

    def getEstimatedCooldown(self):
        if self.timeTransportCooldown > 0:
            return time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(self.timeTransportCooldown))
        else:
            return 0

    def getProductionCooldown(self):
        productionTime = self.orderInProduction.get('timeFinish')
        if productionTime:
            return time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(productionTime))
        else:
            return 0

    def getEstimatedCooldownStr(self):
        return time_formatters.getTimeDurationStr(self.getEstimatedCooldown())

    def isExportAvailable(self, resCount = None):
        enoughRes = True
        if resCount is not None:
            enoughRes = self.storage >= resCount
        return self.isReady() and not self.isInCooldown() and self.hasStorageToExport() and enoughRes

    def isImportAvailable(self, resCount = None):
        space = self.levelRef.storage - self.storage
        enoughRes = True
        if resCount is not None:
            enoughRes = space >= resCount
        return not self.isInCooldown() and self.hasSpaceToImport() and enoughRes
