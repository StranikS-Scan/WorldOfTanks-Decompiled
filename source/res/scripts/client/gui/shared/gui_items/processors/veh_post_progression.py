# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/veh_post_progression.py
import typing
import BigWorld
from gui.shared.gui_items.processors import Processor, plugins
from gui.veh_post_porgression.messages import makeModificationErrorMsg, makeDiscardPairsMsg, makeBuyPairMsg, makePurchaseStepsMsg, makeChangeSlotCategoryMsg, makeSetSlotCategoryMsg
from gui.veh_post_porgression.sounds import playSound
from gui.veh_post_porgression.sounds import Sounds
from post_progression_common import ACTION_TYPES
from gui.veh_post_porgression.models.ext_money import EXT_MONEY_ZERO, getFullXPFromXPPrice
if typing.TYPE_CHECKING:
    from gui.shared.gui_items import Vehicle

class PostProgressionProcessor(Processor):
    __slots__ = ('_vehicleCD',)
    IS_GAMEFACE_SUPPORTED = True

    def __init__(self, vehicle):
        super(PostProgressionProcessor, self).__init__()
        self._vehicleCD = vehicle.intCD
        self.__setupPlugins()

    def _getVehicle(self):
        return self.itemsCache.items.getItemByCD(self._vehicleCD)

    def __setupPlugins(self):
        self.addPlugin(plugins.PostProgressionStateValidator(self._getVehicle()))


class ChangeVehicleSetupEquipments(PostProgressionProcessor):
    __slots__ = ('__groupID', '__layoutIdx')

    def __init__(self, vehicle, groupID, layoutIdx):
        super(ChangeVehicleSetupEquipments, self).__init__(vehicle)
        self.__groupID = groupID
        self.__layoutIdx = layoutIdx
        self.addPlugin(plugins.PostProgressionChangeSetupValidator(vehicle, groupID))

    def _request(self, callback):
        BigWorld.player().inventory.changeVehicleSetupGroup(self._getVehicle().invID, self.__groupID, self.__layoutIdx, lambda code: self._response(code, callback))


class DiscardPairsProcessor(PostProgressionProcessor):
    __slots__ = ('__stepIDs', '__modIDs')

    def __init__(self, vehicle, stepIDs, modIDs):
        super(DiscardPairsProcessor, self).__init__(vehicle)
        self.__stepIDs = stepIDs
        self.__modIDs = modIDs
        self.addPlugins([plugins.PostProgressionStepsValidator(vehicle, stepIDs, {ACTION_TYPES.PAIR_MODIFICATION}), plugins.PostProgressionDiscardPairsValidator(vehicle, stepIDs)])

    def _successHandler(self, code, ctx=None):
        playSound(Sounds.MODIFICATION_DESTROY)
        vehicle = self._getVehicle()
        discardMods = [ vehicle.postProgression.getStep(stepID).action.getModificationByID(modificationID) for stepID, modificationID in zip(self.__stepIDs, self.__modIDs) ]
        return makeDiscardPairsMsg(vehicle, discardMods)

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeModificationErrorMsg()

    def _request(self, callback):
        BigWorld.player().inventory.discardPostProgressionPairs(self._vehicleCD, self.__stepIDs, lambda code: self._response(code, callback))


class PurchasePairProcessor(PostProgressionProcessor):
    __slots__ = ('__stepID', '__modID')

    def __init__(self, vehicle, stepID, modificationID):
        super(PurchasePairProcessor, self).__init__(vehicle)
        self.__stepID = stepID
        self.__modID = modificationID
        self.addPlugins([plugins.PostProgressionStepsValidator(vehicle, [stepID], {ACTION_TYPES.PAIR_MODIFICATION}), plugins.PostProgressionPurchasePairValidator(vehicle, stepID, modificationID)])

    def _successHandler(self, code, ctx=None):
        playSound(Sounds.MODIFICATION_MOUNT)
        return makeBuyPairMsg(self._getVehicle(), self.__stepID, self.__modID)

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeModificationErrorMsg()

    def _request(self, callback):
        pairType = self._getVehicle().postProgression.getStep(self.__stepID).action.getInnerPairType(self.__modID)
        BigWorld.player().inventory.purchasePostProgressionPair(self._vehicleCD, self.__stepID, pairType, lambda code: self._response(code, callback))


class PurchaseStepsProcessor(PostProgressionProcessor):
    __slots__ = ('__stepIDs', '__price')

    def __init__(self, vehicle, stepIDs):
        super(PurchaseStepsProcessor, self).__init__(vehicle)
        self.__price = EXT_MONEY_ZERO
        self.__stepIDs = stepIDs
        self.addPlugins([plugins.PostProgressionStepsValidator(vehicle, stepIDs, {ACTION_TYPES.FEATURE, ACTION_TYPES.MODIFICATION}), plugins.PostProgressionPurchaseStepsValidator(vehicle, stepIDs)])

    def _request(self, callback):
        self.__price = self.__getPrice(self._getVehicle())
        BigWorld.player().inventory.purchasePostProgressionSteps(self._vehicleCD, self.__stepIDs, lambda code, ext: self._response(code, callback, ctx=ext))

    def _successHandler(self, code, ctx=None):
        return makePurchaseStepsMsg(self._getVehicle(), ctx, self.__price)

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeModificationErrorMsg()

    def __getPrice(self, vehicle):
        price = EXT_MONEY_ZERO
        for stepID in self.__stepIDs:
            price += vehicle.postProgression.getStep(stepID).getPrice()

        return getFullXPFromXPPrice(self.itemsCache.items.stats.getMoneyExt(self._vehicleCD), price)


class SetEquipmentSlotTypeProcessor(PostProgressionProcessor):
    __slots__ = ('__slotID', '__isChange')

    def __init__(self, vehicle, slotID):
        super(SetEquipmentSlotTypeProcessor, self).__init__(vehicle)
        self.__slotID = slotID
        self.__isChange = vehicle.optDevices.getSlot(vehicle.optDevices.dynSlotTypeFirstIdx).isDynamic
        self.addPlugin(plugins.PostProgressionSetSlotTypeValidator(vehicle, slotID))

    def _request(self, callback):
        BigWorld.player().inventory.setEquipmentSlotType(self._getVehicle().invID, self.__slotID, lambda code: self._response(code, callback))

    def _successHandler(self, code, ctx=None):
        vehicle = self._getVehicle()
        slot = vehicle.optDevices.getSlot(vehicle.optDevices.dynSlotTypeFirstIdx).item
        if self.__isChange:
            price = self.itemsCache.items.shop.customRoleSlotChangeCost(vehicle.level)
            return makeChangeSlotCategoryMsg(vehicle, slot, price)
        return makeSetSlotCategoryMsg(vehicle, slot)

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeModificationErrorMsg()
