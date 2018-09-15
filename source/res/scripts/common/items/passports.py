# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/passports.py
"""
Module provides common functionality for passport generation assuming that
generated passport satisfies some criteria.
Typical scenario of using module looks as follows:
* create generator using passport_generator for desired nation and premiality by suppliyng method
 that produces single passport:
 nationID = <some nation>

 pg = passport_generator(nationID, True, tankmen.passportProducer)
 passport = next(pg)

ATTENTION: Unconstrained generator such as above is infinite.
* To constrain generated passport, filters with signature (seqId, group, passport) -> bool, should be supplied.
Generation process can be constrained on number of attempts to generate, group the passport is generated from,
passport itself:

 pg = passport_generator(nationID, True, tankmen.passportProducer,
                        lambda seqId, group, passport: 'someTag' in group['tags'])
 passport = next(pg)

Make sure that criteria are feasible by providing the appropriate producer, of criteria that can be in principle
 satisfied. Otherwise next will loop forever.

* Criteria are combined via 'and' operation, all criteria are avaluated beforehand.
* Criteria can be soften by if any of filters raises StopIteration, generator then returns currently generated
passport that partially satisfies all criteria. After that generator is empty and should not be used.
* most frequent builders for filters are provide by module as well;
    - acceptOn(key, value) provides constraint that is satisfied when value is equal or contained in group[key];
    - distinctFrom(old) provides constraint that is satisfied when passport not in old;
    - uniformIds() provides constraint that is satisfied when passport has equal ids for last and first names;
    - maxAttempts(count) limits generation attempts to count, the last attempt will return any passport generated.
"""

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
    """
    Constructs filter for passport generator returning True if value is equal or
    contained to/in contents of group[key].
    :param key: key inside group.
    :param value: anything to be compared to contents of group[key].
    :return: True if group[key] contains or equal to value depending on group[key] type.
    """

    def wrapper(seqId, group, passport):
        original = getattr(group, key)
        return value in (original if hasattr(original, '__contains__') else (original,))

    return wrapper


def distinctFrom(old=()):
    """
    Returns filter to discard passports that are already in old
    :param old: cache of already generated items.
    :return: function, returning True if cache contains provided passports.
    """

    def wrapper(seqId, group, passport):
        return False if old and passport in old else True

    return wrapper


def uniformIds():
    """
    Returns filter to constrain generated passports to have equal ids for first names, last names and icons.
    :return: filter, accepting seqId, group, passport and returning True in case parameters match
    the criteria mentioned above.
    """

    def wrapper(seqId, group, passport):
        return True if len(set(passport[3:])) == 1 else False


def maxAttempts(count=1):
    """
    Returns filter to constrain generated passports on number of invocations of method, producing
    passport. If number of invocations exceeds count, generator returns last generated passport
    and closes generation.
    :param count: number of invocations of passport producing method.
    :return: True if number of invocations does nod exceed count, raises StopIteration otherwise.
    """

    def wrapper(seqId, group, passport):
        if 0 < count <= seqId + 1:
            raise StopIteration
        return True

    return wrapper


class PassportCache(list):
    """
    Enhanced list class to override the __contains__ method for passports
    to match on iconId or (firstNameId, lastNameId)
    """

    def __init__(self, seq=()):
        super(PassportCache, self).__init__(seq)

    def __contains__(self, o):
        fnId, lnId, icId = o[3:]
        for p in self:
            if icId == p[5] or (fnId, lnId) == p[3:5]:
                return True

        return False
