# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/visual_script/__init__.py
from story_mode.visual_script import voiceover_blocks, ui_blocks
from visual_script.misc import ASPECT
from visual_script.registrar import VSBlockRegistrar
g_blockRegistrar = VSBlockRegistrar(ASPECT.CLIENT, ASPECT.HANGAR)
g_blockRegistrar.regBlocksFromModule(voiceover_blocks)
g_blockRegistrar.regBlocksFromModule(ui_blocks)
