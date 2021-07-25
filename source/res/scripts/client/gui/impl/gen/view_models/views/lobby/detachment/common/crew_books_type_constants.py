# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/crew_books_type_constants.py
from frameworks.wulf import ViewModel

class CrewBooksTypeConstants(ViewModel):
    __slots__ = ()
    BROCHURE = 'brochure'
    GUIDE = 'guide'
    CREWBOOK = 'crewBook'
    UNIVERSAL_BROCHURE = 'universalBrochure'
    UNIVERSAL_GUIDE = 'universalGuide'
    UNIVERSAL_CREWBOOK = 'universalBook'

    def __init__(self, properties=0, commands=0):
        super(CrewBooksTypeConstants, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(CrewBooksTypeConstants, self)._initialize()
