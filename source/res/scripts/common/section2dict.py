# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/section2dict.py
import typing
if typing.TYPE_CHECKING:
    from ResMgr import DataSection

def _parseDataSection(dataSection):
    if not len(dataSection.values()):
        return _normalizeValue(dataSection.asString)
    result = {}
    for section in dataSection.values():
        if section.isAttribute:
            continue
        key = section.name
        value = _parseDataSection(section)
        if key in result:
            if isinstance(result[key], list):
                result[key].append(value)
            else:
                result[key] = [result[key], value]
        result[key] = value

    return result


def _normalizeValue(value):
    if value.isdigit():
        value = int(value)
    else:
        try:
            value = float(value)
        except ValueError:
            pass

    return value


def parse(data):
    return {} if not len(data.values()) else _parseDataSection(data)
