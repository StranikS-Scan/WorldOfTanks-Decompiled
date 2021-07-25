# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/tooltips/commander_look_tooltip.py
import typing
from frameworks.wulf import ViewSettings
from gui import GUI_NATIONS_ORDER_INDICES
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.commander_look_tooltip_model import CommanderLookTooltipModel
from gui.impl.pub import ViewImpl
from gui.shared.gui_items.crew_skin import Rarity, localizedFullName
from helpers import dependency
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.shared import IItemsCache
from uilogging.detachment.loggers import DynamicGroupTooltipLogger
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.detachment import Detachment
    from gui.shared.gui_items.crew_skin import CrewSkin
    from gui.shared.gui_items import Vehicle
_COMMA = ', '
_PERIOD = '.'

class CommanderLookTooltip(ViewImpl):
    __slots__ = ('_id',)
    __itemsCache = dependency.descriptor(IItemsCache)
    __detachmentCache = dependency.descriptor(IDetachmentCache)
    uiLogger = DynamicGroupTooltipLogger()

    def __init__(self, id_):
        settings = ViewSettings(R.views.lobby.detachment.tooltips.CommanderLookTooltip())
        settings.model = CommanderLookTooltipModel()
        super(CommanderLookTooltip, self).__init__(settings)
        self._id = id_

    def _onLoading(self):
        crewSkin = self.__itemsCache.items.getCrewSkin(self._id)
        vm = super(CommanderLookTooltip, self).getViewModel()
        vm.setName(localizedFullName(crewSkin))
        vm.setIcon(R.images.gui.maps.icons.commanders.c_158x118.crewSkins.dyn(crewSkin.getIconID())())
        vm.setDescription(backport.textRes(crewSkin.getDescription())())
        vm.setNation(crewSkin.getNation() or '')
        vm.setFreeCount(crewSkin.getFreeCount())
        vm.setUseCount(len(crewSkin.getDetachmentIDs()))
        vm.setRarity(R.strings.item_types.crewSkins.itemType.dyn(Rarity.STRINGS[crewSkin.getRarity()])())
        vm.setUsedIn(self.__getUsedIn())

    def _initialize(self, *args, **kwargs):
        super(CommanderLookTooltip, self)._initialize()
        self.uiLogger.tooltipOpened()

    def _finalize(self):
        self.uiLogger.tooltipClosed(self.__class__.__name__)
        self.uiLogger.reset()
        super(CommanderLookTooltip, self)._finalize()

    def __getUsedIn(self):
        usedInVehicles = []
        inBarracksCount = 0
        for detachment in self.__detachmentCache.getDetachments().values():
            if detachment.skinID == self._id:
                if detachment.isInTank:
                    vehicle = self.__itemsCache.items.getVehicle(detachment.vehInvID)
                    usedInVehicles.append(vehicle)
                else:
                    inBarracksCount += 1

        usedInVehicles = sorted(usedInVehicles, key=lambda v: GUI_NATIONS_ORDER_INDICES[v.nationID])
        usedIn = [ v.shortUserName for v in usedInVehicles ]
        if inBarracksCount > 0:
            usedIn.append(backport.text(R.strings.tooltips.crewSkins.inBarracks(), count=inBarracksCount))
        return _COMMA.join(usedIn) + _PERIOD if usedIn else ''
