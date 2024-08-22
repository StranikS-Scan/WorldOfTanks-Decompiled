# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/shared/gui_items.py
import typing
if typing.TYPE_CHECKING:
    from typing import Optional
    from gui.veh_post_progression.models.progression import PostProgressionItem
    from items.vehicles import VehicleType
    from post_progression_common import VehicleState
    from gui.shared.gui_items.dossier import AccountDossier
    from dossiers2.common.DossierDescr import DossierDescr

class IGuiItemsFactory(object):

    def clear(self):
        raise NotImplementedError

    def createGuiItem(self, itemTypeIdx, *args, **kwargs):
        raise NotImplementedError

    def createGuiItemFromCompactDescr(self, compactDescr, *args, **kwargs):
        raise NotImplementedError

    def createShell(self, intCompactDescr, count=0, proxy=None, isBoughtForCredits=False):
        raise NotImplementedError

    def createEquipment(self, intCompactDescr, proxy=None, isBoughtForCredits=False):
        raise NotImplementedError

    def createOptionalDevice(self, intCompactDescr, proxy=None):
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

    def createVehicle(self, strCompactDescr=None, inventoryID=-1, typeCompDescr=None, proxy=None, extData=None, invData=None):
        raise NotImplementedError

    def createTankman(self, strCompactDescr, inventoryID=-1, vehicle=None, dismissedAt=None, proxy=None, vehicleSlotIdx=-1):
        raise NotImplementedError

    def createTankmanDossier(self, tmanDescr, tankmanDossierDescr, extDossier, playerDBID=None, currentVehicleItem=None):
        raise NotImplementedError

    def createAccountDossier(self, dossier, playerDBID=None, rated7x7Seasons=None):
        raise NotImplementedError

    def createVehicleDossier(self, dossier, vehTypeCompDescr, playerDBID=None):
        raise NotImplementedError

    def createBadge(self, descriptor, proxy=None, extraData=None, receivedBadges=None):
        raise NotImplementedError

    def createLootBox(self, lootBoxID, lootBoxConfig, count):
        raise NotImplementedError

    def createCustomization(self, intCompactDescr, proxy=None):
        raise NotImplementedError

    def createOutfit(self, strCompactDescr=None, component=None, vehicleCD=''):
        raise NotImplementedError

    def createVehPostProgression(self, vehIntCD, state, vehType):
        raise NotImplementedError
