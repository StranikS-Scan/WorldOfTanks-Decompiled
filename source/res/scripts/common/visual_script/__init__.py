# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/__init__.py
from visual_script.component import ASPECT
from visual_script.registrar import regAllVScriptComponentsInModule, regVScriptComponent, aspectActive, anyAspectActive
if anyAspectActive(ASPECT.CLIENT, ASPECT.SERVER):
    import example
    regAllVScriptComponentsInModule(example)
    import general
    regAllVScriptComponentsInModule(general)
if aspectActive(ASPECT.CLIENT):
    from visual_script_client import camera_blocks
    regAllVScriptComponentsInModule(camera_blocks)
    from visual_script_client import tank_blocks
    regAllVScriptComponentsInModule(tank_blocks)
if aspectActive(ASPECT.SERVER):
    pass
