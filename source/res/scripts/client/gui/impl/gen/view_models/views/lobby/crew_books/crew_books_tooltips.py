# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew_books/crew_books_tooltips.py
from frameworks.wulf import ViewModel

class CrewBooksTooltips(ViewModel):
    __slots__ = ()
    TOOLTIP_CREW_BOOK_RESTRICTED = 'crewBookRestricted'
    TOOLTIP_TANKMAN = 'tankman'
    TOOLTIP_TANKMAN_NEW_SKILL = 'tankmanNewSkill'
    TOOLTIP_TANKMAN_SKILL = 'tankmanSkill'

    def __init__(self, properties=0, commands=0):
        super(CrewBooksTooltips, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(CrewBooksTooltips, self)._initialize()
