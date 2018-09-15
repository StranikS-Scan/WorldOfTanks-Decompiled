# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/component_override.py


class ComponentOverride(object):

    def __init__(self, default, override, check):
        super(ComponentOverride, self).__init__()
        self.__default = default if isinstance(default, ComponentOverride) else (lambda : default)
        self.__override = override if isinstance(override, ComponentOverride) else (lambda : override)
        self.__check = check

    def __call__(self):
        return self.__override() if self.__check() else self.__default()
