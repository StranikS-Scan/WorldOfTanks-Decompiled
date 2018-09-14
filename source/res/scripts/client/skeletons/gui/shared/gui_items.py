# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/shared/gui_items.py


class IGuiItemsFactory(object):
    """
    Interface of GUI items factory.
    """

    def clear(self):
        raise NotImplementedError

    def createGuiItem(self, itemTypeIdx, *args, **kwargs):
        raise NotImplementedError

    def createGuiItemFromCompactDescr(self, compactDescr, *args, **kwargs):
        raise NotImplementedError

    def createShell(self, intCompactDescr, count=0, defaultCount=0, proxy=None, isBoughtForCredits=False):
        raise NotImplementedError

    def createEquipment(self, intCompactDescr, proxy=None, isBoughtForCredits=False):
        raise NotImplementedError

    def createOptionalDevice(self, intCompactDescr, proxy=None, isBoughtForCredits=False):
        raise NotImplementedError

    def createVehicleGun(self, intCompactDescr, proxy=None, descriptor=None):
        raise NotImplementedError

    def createVehicleChassis(self, intCompactDescr, proxy=None, descriptor=None):
        raise NotImplementedError

    def createVehicleTurret(self, intCompactDescr, proxy=None, descriptor=None):
        raise NotImplementedError

    def createVehicleEngine(self, intCompactDescr, proxy=None, descriptor=None):
        raise NotImplementedError

    def createVehicleRadio(self, intCompactDescr, proxy=None, descriptor=None):
        raise NotImplementedError

    def createVehicleFuelTank(self, intCompactDescr, proxy=None, descriptor=None):
        raise NotImplementedError

    def createVehicle(self, strCompactDescr=None, inventoryID=-1, typeCompDescr=None, proxy=None):
        raise NotImplementedError

    def createTankman(self, strCompactDescr, inventoryID=-1, vehicle=None, dismissedAt=None, proxy=None):
        raise NotImplementedError

    def createTankmanDossier(self, tmanDescr, tankmanDossierDescr, extDossier, playerDBID=None, currentVehicleItem=None):
        raise NotImplementedError

    def createAccountDossier(self, dossier, playerDBID=None, rated7x7Seasons=None, rankedCurrentSeason=None):
        raise NotImplementedError

    def createVehicleDossier(self, dossier, vehTypeCompDescr, playerDBID=None, rankedCurrentSeason=None):
        raise NotImplementedError
