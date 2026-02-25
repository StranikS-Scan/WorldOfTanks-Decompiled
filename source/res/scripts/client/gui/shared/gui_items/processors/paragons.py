# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/paragons.py
import logging
from functools import partial
import typing
import BigWorld
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Vehicle import getUserName
from gui.shared.gui_items.processors import Processor, makeError, makeSuccess
from gui.shared.gui_items.processors.paragons_plugins import ParagonsResetBranchValidator, ParagonsChapterValidator, ParagonsChapterLevelValidator, ParagonsValidateSelectedRewardEntCode, ParagonsValidateSelectedRewardInOrder, ParagonsChangeChapterValidator, ParagonsValidateSelectedRewardToken
from gui.shared.utils.decorators import adisp_process
from helpers import dependency
from items.components.c11n_constants import ItemTags
from paragons_common import PARAGONS_ENTITLEMENT_TO_NUMBER_CODES
from skeletons.gui.game_control import IParagonsController
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Callable
    from gui.SystemMessages import ResultMsg
_logger = logging.getLogger(__name__)

class ParagonsResetBranchProcessor(Processor):
    __slots__ = ('__branchID', '__vehiclesCopy', '_credits', '_equipments', '_instructions', '_ammunitions', '_appearances', '_kits', '_crews')
    __paragonsController = dependency.descriptor(IParagonsController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, branchID, isStockVehConfiguration=False, ctx=None):
        super(ParagonsResetBranchProcessor, self).__init__(plugins=[ParagonsResetBranchValidator(branchID)])
        self.__branchID = branchID
        self.__isStock = int(isStockVehConfiguration)
        self.__vehiclesCopy = []
        expectedCredits = ctx.get('credits', 0) if ctx is not None else None
        for vehicle in self.__paragonsController.getBranchResetVehicles(self.__branchID):
            self.__vehiclesCopy.append(self.__itemsCache.items.getVehicleCopy(vehicle))

        if expectedCredits is None:
            self._credits = self.__paragonsController.branches.getBranchResetCompensation(self.__branchID)
        else:
            self._credits = expectedCredits
        self._equipments = 0
        self._instructions = 0
        self._ammunitions = 0
        self._appearances = 0
        self._kits = 0
        self._crews = 0
        for vehicle in self.__vehiclesCopy:
            if not vehicle.isInInventory:
                continue
            self._equipments += self.__getEquipments(vehicle)
            self._instructions += self.__getInstructions(vehicle)
            self._ammunitions += self.__getAmmunitions(vehicle)
            self._appearances += self.__getAppearances(vehicle)
            self._kits += self.__getConsumables(vehicle)
            self._crews += self.__getCrews(vehicle)

        return

    def _successHandler(self, code, ctx=None):
        auxData = {'credits': self._credits,
         'equipments': self._equipments,
         'instructions': self._instructions,
         'ammunitions': self._ammunitions,
         'appearances': self._appearances,
         'kits': self._kits,
         'crews': self._crews}
        return makeSuccess(auxData=auxData)

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeError()

    def _request(self, callback):
        BigWorld.player().paragons.resetBranch(self.__branchID, self.__isStock, partial(self.__resetBranchCallback, callback))

    def __resetBranchCallback(self, callback, _, resultID, errorStr, ctx=None):
        return self._response(resultID, callback, errorStr, ctx)

    def __formatVehicleText(self):
        result = []
        for vehicle in self.__paragonsController.getBranchResetVehicles(self.__branchID):
            result.append(text_styles.vehicleName(getUserName(vehicle.typeDescr)))

        return '\n'.join(result)

    def __getAppearances(self, resetVehicle):
        outfits = resetVehicle.outfits
        itemsCount = 0
        for outfit in outfits.itervalues():
            if outfit.style:
                itemsCount += 1
                break
            for itemCD in outfit.items():
                item = self.__itemsCache.items.getItemByCD(itemCD)
                if ItemTags.NATIONAL_EMBLEM not in item.tags:
                    itemsCount += 1

        return itemsCount

    def __getEquipments(self, vehicle):
        return len(vehicle.optDevices.setupLayouts.getUniqueItems())

    def __getAmmunitions(self, vehicle):
        shells = 0
        for shell in vehicle.shells.setupLayouts.getUniqueItems():
            shells += shell.count

        return shells

    def __getConsumables(self, vehicle):
        return len(vehicle.consumables.setupLayouts.getUniqueItems())

    def __getInstructions(self, vehicle):
        return len(vehicle.battleBoosters.setupLayouts.getUniqueItems())

    def __getCrews(self, vehicle):
        return len([ t for t in vehicle.crew if t[1] is not None ])


class ParagonsSetChapterProcessor(Processor):
    __slots__ = ('__chapterID',)
    __paragonsController = dependency.descriptor(IParagonsController)

    def __init__(self, chapterID):
        super(ParagonsSetChapterProcessor, self).__init__(plugins=[ParagonsChapterValidator(chapterID), ParagonsChangeChapterValidator(chapterID)])
        self.__chapterID = chapterID

    def _successHandler(self, code, ctx=None):
        return makeSuccess()

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeError()

    def _request(self, callback):
        BigWorld.player().paragons.setChapter(self.__chapterID, partial(self.__setChapterCallback, callback))

    def __setChapterCallback(self, callback, _, resultID, errorStr, ctx=None):
        return self._response(resultID, callback, errorStr, ctx)


class MarkSelectedRewardsProcessor(Processor):
    __slots__ = ('__chapterID', '__levelID', '__entCode', '__tokenID')

    def __init__(self, chapterID, levelID, entitlementID, tokenID):
        self.__chapterID = chapterID
        self.__levelID = levelID
        self.__entCode = PARAGONS_ENTITLEMENT_TO_NUMBER_CODES.get(entitlementID)
        self.__tokenID = tokenID
        super(MarkSelectedRewardsProcessor, self).__init__(plugins=[ParagonsChapterValidator(chapterID),
         ParagonsChapterLevelValidator(chapterID, levelID),
         ParagonsValidateSelectedRewardEntCode(entitlementID),
         ParagonsValidateSelectedRewardToken(tokenID),
         ParagonsValidateSelectedRewardInOrder(chapterID, levelID, self.__entCode, tokenID)])

    def _request(self, callback):
        BigWorld.player().paragons.markSelectedRewards(self.__chapterID, self.__levelID, self.__entCode, int(self.__tokenID.split(':')[-1]), partial(self.__setCallback, callback))

    def __setCallback(self, callback, _, resultID, errorStr, ctx=None):
        return self._response(resultID, callback, errorStr, ctx)


@adisp_process()
def selectMark(chapterID, levelID, entCode, tokenID):
    res = yield MarkSelectedRewardsProcessor(chapterID, levelID, entCode, tokenID).request()
    _logger.info(res)
