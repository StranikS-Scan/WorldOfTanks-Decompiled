# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/visual_script_client/__init__.py
from constants import IS_UE_EDITOR
from visual_script.misc import ASPECT
from visual_script.registrar import VSBlockRegistrar
from sound_notifications_context import WTSoundNotificationsContext
g_blockRegistrar = VSBlockRegistrar(ASPECT.CLIENT, ASPECT.HANGAR)

def registerForGeneral():
    import vehicle_blocks
    import cgf_blocks
    import sound_blocks
    g_blockRegistrar.regBlocksFromModule(vehicle_blocks)
    g_blockRegistrar.regBlocksFromModule(cgf_blocks)
    g_blockRegistrar.regBlocksFromModule(sound_blocks)
    g_blockRegistrar.regContext(WTSoundNotificationsContext)


def registerForUEEditor():
    g_blockRegistrar.regContext(WTSoundNotificationsContext)


if IS_UE_EDITOR:
    registerForUEEditor()
else:
    registerForGeneral()
