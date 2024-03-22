# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/crew5075/loggers.py
from uilogging.crew.loggers import CrewViewLogger, CrewDialogLogger
from uilogging.crew5075.logging_constants import FEATURE, Crew5075NavigationButtons
from gui.impl.gen.view_models.views.lobby.crew.crew_intro_view_model import CloseReason

class Crew5075ViewLogger(CrewViewLogger):
    _FEATURE = FEATURE
    _REASONS = {CloseReason.CLOSE.value: Crew5075NavigationButtons.CLOSE,
     CloseReason.ESC.value: Crew5075NavigationButtons.ESC,
     CloseReason.AFFIRMATIVE.value: Crew5075NavigationButtons.AFFIRMATIVE}

    def logButtonClick(self, closeReason):
        return super(Crew5075ViewLogger, self).logNavigationButtonClick(self._REASONS.get(closeReason, Crew5075NavigationButtons.CLOSE))


class Crew5075DialogLogger(CrewDialogLogger):
    _FEATURE = FEATURE
