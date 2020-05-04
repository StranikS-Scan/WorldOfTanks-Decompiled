# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/__init__.py
from visual_script.block import ASPECT
from visual_script.registrar import regAllVScriptBlocksInModule, regVScriptBlock, aspectActive, anyAspectActive
if anyAspectActive(ASPECT.CLIENT, ASPECT.SERVER):
    import example
    regAllVScriptBlocksInModule(example)
    import general
    regAllVScriptBlocksInModule(general)
if aspectActive(ASPECT.CLIENT):
    from visual_script_client import event
    regAllVScriptBlocksInModule(event)
    from visual_script_client import sequence
    regAllVScriptBlocksInModule(sequence)
    from visual_script_client import camera
    regAllVScriptBlocksInModule(camera)
if aspectActive(ASPECT.SERVER):
    pass
