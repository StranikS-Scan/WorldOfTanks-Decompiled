# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/wrapped_options.py
from constants import IS_EDITOR
if IS_EDITOR:
    from Options import setOptionString
    from Options import getOptionString
    from Options import setOptionInt
    from Options import getOptionInt
    from Options import setOptionBool
    from Options import getOptionBool
    from Options import setOptionFloat
    from Options import getOptionFloat
    from Options import setOptionVector2
    from Options import getOptionVector2
    from Options import setOptionVector3
    from Options import getOptionVector3
    from Options import setOptionVector4
    from Options import getOptionVector4
    from Options import setOptionMatrix34
    from Options import getOptionMatrix34
    from Options import setOption
else:

    def setOptionString(name, value):
        pass


    def getOptionString(name, defaultVal):
        return defaultVal


    def setOptionInt(name, value):
        pass


    def getOptionInt(name, defaultVal):
        return defaultVal


    def setOptionBool(name, value):
        pass


    def getOptionBool(name, defaultVal):
        return defaultVal


    def setOptionFloat(name, value):
        pass


    def getOptionFloat(name, defaultVal):
        return defaultVal


    def setOptionVector2(name, value):
        pass


    def getOptionVector2(name, defaultVal):
        return defaultVal


    def setOptionVector3(name, value):
        pass


    def getOptionVector3(name, defaultVal):
        return defaultVal


    def setOptionVector4(name, value):
        pass


    def getOptionVector3(name, defaultVal):
        return defaultVal


    def setOptionMatrix34(name, value):
        pass


    def getOptionMatrix34(name, defaultVal):
        return defaultVal


    def setOption(name, value):
        pass
