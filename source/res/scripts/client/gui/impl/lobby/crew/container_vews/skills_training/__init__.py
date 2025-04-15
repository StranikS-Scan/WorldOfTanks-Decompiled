# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/container_vews/skills_training/__init__.py
import logging
import typing
from gui.impl.lobby.crew.container_vews.personal_file import getPersonalFileView
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from gui.impl.lobby.crew.container_vews.personal_file.controller import PersonalFileInteractionController

def loadSortingOrderType():
    personalFileView = getPersonalFileView()
    if personalFileView:
        ctrl = personalFileView.interactionCtrl
        return ctrl.getCrewAssistSortSelection()
    _logger.warning("Couldn't load setting because PersonalFileView is not found!")


def saveSortingOrderType(sortingType):
    personalFileView = getPersonalFileView()
    if personalFileView:
        ctrl = personalFileView.interactionCtrl
        ctrl.setCrewAssistSortSelection(sortingType)
    else:
        _logger.warning("Couldn't save setting because PersonalFileView is not found!")
