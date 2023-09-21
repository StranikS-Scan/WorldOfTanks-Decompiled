# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/crew_book.py
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.tooltips.common import BlocksTooltipData
from items import tankmen
from items.components.crew_books_constants import CREW_BOOK_PROPERTIES_MASKS, CREW_BOOK_RESTRICTIONS

class CrewBookTooltipDataBlock(BlocksTooltipData):

    def __init__(self, context):
        super(CrewBookTooltipDataBlock, self).__init__(context, TOOLTIP_TYPE.CREW_BOOK)
        self._setContentMargin(bottom=8)
        self._setWidth(320)

    def _packBlocks(self, *args, **kwargs):
        items = super(CrewBookTooltipDataBlock, self)._packBlocks()
        item = self.context.buildItem(*args, **kwargs)
        block = []
        block.append(formatters.packTextBlockData(text=text_styles.highTitle(item.userName)))
        block.append(formatters.packTextBlockData(text=text_styles.main(item.fullDescription)))
        items.append(formatters.packBuildUpBlockData(block))
        return items


class CrewBookRestrictedTooltipDataBlock(BlocksTooltipData):

    def __init__(self, context):
        super(CrewBookRestrictedTooltipDataBlock, self).__init__(context, TOOLTIP_TYPE.CREW_BOOK)
        self._setContentMargin(bottom=8)
        self._setWidth(420)

    def _packBlocks(self, *args, **kwargs):
        items = super(CrewBookRestrictedTooltipDataBlock, self)._packBlocks()
        bookVehicleContext = self.context.buildItem(*args, **kwargs)
        vehicle = bookVehicleContext.vehicle
        block = []
        text = backport.text(R.strings.tooltips.crewBooks.screen.invalidCrew.title())
        block.append(formatters.packTextBlockData(text=text_styles.highlightText(text)))
        vehTypeCD = vehicle.descriptor.type.compactDescr
        crew = [ (tman.strCD if tman else None) for _, tman in vehicle.crew ]
        _, validationMssk, _, crewLists = tankmen.validateCrewToLearnCrewBook(crew, vehTypeCD)
        for mask in CREW_BOOK_PROPERTIES_MASKS.ALL:
            if mask & validationMssk:
                locSuffix = CREW_BOOK_RESTRICTIONS[mask]
                names = ''
                invalidTmen = crewLists[mask]
                for slotID in invalidTmen:
                    _, tman = vehicle.crew[slotID]
                    names += tman.fullUserName
                    if slotID != invalidTmen[-1]:
                        names += ', '

                text = backport.text(R.strings.tooltips.crewBooks.screen.invalidCrew.dyn(locSuffix)(), name=names)
                block.append(formatters.packTextBlockData(text=u'\u2022 ' + text_styles.main(text)))

        items.append(formatters.packBuildUpBlockData(block))
        return items
