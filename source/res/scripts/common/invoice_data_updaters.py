# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/invoice_data_updaters.py
LATEST_DATA_VERSION = 3

def _update1to2(data):
    if 'slots' in data:
        return None
    elif 'berths' in data:
        return None
    else:
        data['version'] = 2
        vehicles = data.get('vehicles', [])
        slots = 0
        for cd in vehicles:
            if cd > 0:
                slots += 1

        data['slots'] = slots
        return data


def _update2to3(data):
    data['version'] = 3
    vehicles = data.get('vehicles', [])
    if vehicles:
        data['vehicles'] = dict.fromkeys(vehicles, {})
    return data


_versionUpdaters = {1: _update1to2,
 2: _update2to3}

def updateData(data):
    while True:
        if not isinstance(data, dict):
            return
        ver = data.get('version', 1)
        if ver == LATEST_DATA_VERSION:
            break
        updater = _versionUpdaters.get(ver, None)
        if updater is None:
            return
        data = updater(data)

    return data
