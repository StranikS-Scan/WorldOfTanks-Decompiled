# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/arena_component_system/client_arena_component_assembler.py
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from debug_utils import LOG_WARNING
from client_arena_component_system import ClientArenaComponentSystem
from arena_components.player_type_specific_components import getDefaultComponents

def createComponentSystem(arena, bonusType, arenaType):
    componentSystem = ClientArenaComponentSystem(arena, bonusType, arenaType)
    from arena_component_system.assembler_helper import COMPONENT_ASSEMBLER
    if bonusType in COMPONENT_ASSEMBLER:
        COMPONENT_ASSEMBLER[bonusType].assembleComponents(componentSystem)
    else:
        ClientArenaComponentAssembler._assembleBonusCapsComponents(componentSystem)
    ClientArenaComponentAssembler._addArenaComponents(componentSystem, getDefaultComponents(bonusType))
    componentSystem.activate()
    return componentSystem


def destroyComponentSystem(componentSystem):
    if componentSystem is None:
        return
    else:
        componentSystem.destroy()
        from arena_component_system.assembler_helper import COMPONENT_ASSEMBLER
        if componentSystem.bonusType in COMPONENT_ASSEMBLER:
            COMPONENT_ASSEMBLER[componentSystem.bonusType].disassembleComponents(componentSystem)
        return


class ClientArenaComponentAssembler(object):

    @staticmethod
    def assembleComponents(componentSystem):
        pass

    @staticmethod
    def disassembleComponents(componentSystem):
        pass

    @staticmethod
    def _assembleBonusCapsComponents(componentSystem):
        from arena_component_system.assembler_helper import ARENA_BONUS_TYPE_CAP_COMPONENTS
        for name, (bonusFlag, componentClass) in ARENA_BONUS_TYPE_CAP_COMPONENTS.iteritems():
            isBonusTypeCapActive = ARENA_BONUS_TYPE_CAPS.checkAny(componentSystem.bonusType, bonusFlag)
            if isBonusTypeCapActive:
                ClientArenaComponentAssembler._addArenaComponent(componentSystem, name, componentClass)

    @staticmethod
    def _addArenaComponents(componentSystem, componentsList):
        for name, componentClass in componentsList.iteritems():
            ClientArenaComponentAssembler._addArenaComponent(componentSystem, name, componentClass)

    @staticmethod
    def _addArenaComponent(componentSystem, name, componentClass):
        comp = componentClass(componentSystem)
        if comp is not None:
            prevValue = getattr(componentSystem, name, None)
            if prevValue is not None:
                LOG_WARNING('componenent %s is already available, old component will be removed', name)
                componentSystem.removeComponent(prevValue)
            componentSystem.addComponent(comp)
            setattr(componentSystem, name, comp)
        return
