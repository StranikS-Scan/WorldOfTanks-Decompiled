# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCPrebattleHints.py
import SoundGroups
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.Scaleform.daapi.view.meta.BCPrebattleHintsMeta import BCPrebattleHintsMeta

class BCPrebattleHints(BCPrebattleHintsMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, settings):
        super(BCPrebattleHints, self).__init__()
        self.__visibleHints = settings.get('visible_hints', set())
        self.__invisibleHints = settings.get('invisible_hints', set())
        self.__wwSound = settings.get('wwSound')

    def _populate(self):
        super(BCPrebattleHints, self)._populate()
        self.as_setHintsVisibilityS(self.__visibleHints, self.__invisibleHints)
        crewRoles = self.sessionProvider.shared.vehicleState.getControllingVehicle().typeDescriptor.type.crewRoles
        self.as_setCrewCountS(len(crewRoles))
        if self.__wwSound is not None:
            SoundGroups.g_instance.playSound2D(self.__wwSound)
        return

    def _dispose(self):
        super(BCPrebattleHints, self)._dispose()
        self.__visibleHints = None
        self.__invisibleHints = None
        return
