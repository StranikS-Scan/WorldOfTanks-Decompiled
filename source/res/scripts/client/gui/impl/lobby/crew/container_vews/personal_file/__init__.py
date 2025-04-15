# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/container_vews/personal_file/__init__.py
import typing
from helpers.dependency import replace_none_kwargs
from gui.impl.gen import R
from skeletons.gui.impl import IGuiLoader
if typing.TYPE_CHECKING:
    from gui.impl.lobby.crew.container_vews.personal_file.personal_file_view import PersonalFileView

@replace_none_kwargs(uiLoader=IGuiLoader)
def getPersonalFileView(uiLoader=None):
    return uiLoader.windowsManager.getViewByLayoutID(R.views.lobby.crew.personal_case.PersonalFileView())
