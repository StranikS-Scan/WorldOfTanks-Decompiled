# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/shared/gui_items.py
from typing import TYPE_CHECKING, Any
from items.components.crew_skins_constants import NO_CREW_SKIN_ID
from items.components.detachment_constants import NO_INSTRUCTOR_ID, NO_DETACHMENT_ID
if TYPE_CHECKING:
    from gui.shared.gui_items.instructor import Instructor
    from gui.shared.gui_items.detachment import Detachment

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

    def createVehicle(self, strCompactDescr=None, inventoryID=-1, typeCompDescr=None, proxy=None):
        raise NotImplementedError

    def createTankman(self, strCompactDescr, inventoryID=-1, vehicle=None, dismissedAt=None, proxy=None):
        raise NotImplementedError

    def createTankmanDossier(self, tmanDescr, tankmanDossierDescr, extDossier, playerDBID=None, currentVehicleItem=None):
        raise NotImplementedError

    def createAccountDossier(self, dossier, playerDBID=None, rated7x7Seasons=None):
        raise NotImplementedError

    def createVehicleDossier(self, dossier, vehTypeCompDescr, playerDBID=None):
        raise NotImplementedError

    def createBadge(self, descriptor, proxy=None, extraData=None):
        raise NotImplementedError

    def createLootBox(self, lootBoxID, lootBoxConfig, count):
        raise NotImplementedError

    def createCustomization(self, intCompactDescr, proxy=None):
        raise NotImplementedError

    def createOutfit(self, strCompactDescr=None, component=None, vehicleCD=''):
        raise NotImplementedError

    def createDetachment(self, strCompactDescr, proxy=None, invID=NO_DETACHMENT_ID, vehInvID=-1, skinID=NO_CREW_SKIN_ID):
        raise NotImplementedError

    def createInstructor(self, strCompactDescr, proxy=None, invID=NO_INSTRUCTOR_ID, detInvID=NO_DETACHMENT_ID):
        raise NotImplementedError
