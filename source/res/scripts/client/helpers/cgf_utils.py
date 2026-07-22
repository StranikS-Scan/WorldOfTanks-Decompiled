# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/cgf_utils.py


def toggleCgfComponent(go, componentType, enable, *componentArgs):
    component = go.findComponentByType(componentType)
    if enable:
        if component is None:
            go.createComponent(componentType, *componentArgs)
    elif component is not None:
        go.removeComponentByType(componentType)
    return
