# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/animator_instance_properties.py
from collections import namedtuple
AnimatorInstanceProperties = namedtuple('AnimatorInstanceProperties', ('delay', 'speed', 'loopCount', 'loop'))
AnimatorInstanceProperties.__new__.__defaults__ = (0.0,
 1.0,
 -1,
 True)
