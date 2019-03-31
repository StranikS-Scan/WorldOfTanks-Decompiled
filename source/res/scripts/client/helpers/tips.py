# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/tips.py
# Compiled at: 2011-02-17 17:41:31
import random
import helpers.i18n

def getTip():
    return helpers.i18n.makeString('#tips:tip' + str(random.randint(0, 130)))
