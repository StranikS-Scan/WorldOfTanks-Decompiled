# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/time_converters.py


def time2decisec(time):
    return int((time + 0.05) * 10)
