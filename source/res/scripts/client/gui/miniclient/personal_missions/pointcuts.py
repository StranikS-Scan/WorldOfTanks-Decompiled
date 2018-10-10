# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/miniclient/personal_missions/pointcuts.py
import aspects
from helpers import aop

class IsPersonalMissionsEnabled(aop.Pointcut):

    def __init__(self):
        aop.Pointcut.__init__(self, 'helpers.server_settings', 'ServerSettings', 'isPersonalMissionsEnabled', aspects=(aspects.IsPersonalMissionsEnabled,))
