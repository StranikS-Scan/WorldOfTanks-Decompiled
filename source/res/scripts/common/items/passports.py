# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/passports.py


def invalidFemalePassportProducer(nationID, isPremium=False):
    return (-1, (nationID,
      isPremium,
      True,
      0,
      0,
      0))


def invalidMalePassportProducer(nationID, isPremium=False):
    return (-1, (nationID,
      isPremium,
      False,
      0,
      0,
      0))


def passport_generator(nationID, isPremium=False, method=invalidMalePassportProducer, *filters):
    tmp = []
    i = 0
    while True:
        tmp.append(method(nationID, isPremium))
        try:
            try:
                if all(map(lambda f: f(i, *tmp[0]), filters)):
                    yield tmp.pop()[1]
                else:
                    tmp.pop()
            except StopIteration:
                yield tmp.pop()[1]
                raise StopIteration()

        finally:
            i += 1


def acceptOn(key, value):

    def wrapper(seqId, group, passport):
        original = getattr(group, key)
        return value in (original if hasattr(original, '__contains__') else (original,))

    return wrapper


def distinctFrom(old=()):

    def wrapper(seqId, group, passport):
        return False if old and passport in old else True

    return wrapper


def uniformIds():

    def wrapper(seqId, group, passport):
        return True if len(set(passport[3:])) == 1 else False


def maxAttempts(count=1):

    def wrapper(seqId, group, passport):
        if 0 < count <= seqId + 1:
            raise StopIteration
        return True

    return wrapper


class PassportCache(list):

    def __init__(self, seq=()):
        super(PassportCache, self).__init__(seq)

    def __contains__(self, o):
        fnId, lnId, icId = o[3:]
        for p in self:
            if icId == p[5] or (fnId, lnId) == p[3:5]:
                return True

        return False
