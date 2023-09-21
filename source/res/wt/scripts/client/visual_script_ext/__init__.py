# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: wt/scripts/client/visual_script_ext/__init__.py
from visual_script.misc import ASPECT
from visual_script.registrar import VSBlockRegistrar
from constants import IS_DEVELOPMENT
from visual_script_ext.wt_sound_notifications_context import WTSoundNotificationsContext
g_blockRegistrar = VSBlockRegistrar(ASPECT.CLIENT)
g_blockRegistrar.regContext(WTSoundNotificationsContext)
