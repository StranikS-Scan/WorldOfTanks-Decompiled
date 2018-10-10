# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/version.py
import string, re
from types import StringType

class Version:

    def __init__(self, vstring=None):
        if vstring:
            self.parse(vstring)

    def __repr__(self):
        return "%s ('%s')" % (self.__class__.__name__, str(self))


class StrictVersion(Version):
    version_re = re.compile('^(\\d+) \\. (\\d+) (\\. (\\d+))? ([ab](\\d+))?$', re.VERBOSE)

    def parse(self, vstring):
        match = self.version_re.match(vstring)
        if not match:
            raise ValueError, "invalid version number '%s'" % vstring
        major, minor, patch, prerelease, prerelease_num = match.group(1, 2, 4, 5, 6)
        if patch:
            self.version = tuple(map(string.atoi, [major, minor, patch]))
        else:
            self.version = tuple(map(string.atoi, [major, minor]) + [0])
        if prerelease:
            self.prerelease = (prerelease[0], string.atoi(prerelease_num))
        else:
            self.prerelease = None
        return

    def __str__(self):
        if self.version[2] == 0:
            vstring = string.join(map(str, self.version[0:2]), '.')
        else:
            vstring = string.join(map(str, self.version), '.')
        if self.prerelease:
            vstring = vstring + self.prerelease[0] + str(self.prerelease[1])
        return vstring

    def __cmp__(self, other):
        if isinstance(other, StringType):
            other = StrictVersion(other)
        compare = cmp(self.version, other.version)
        if compare == 0:
            if not self.prerelease and not other.prerelease:
                return 0
            if self.prerelease and not other.prerelease:
                return -1
            if not self.prerelease and other.prerelease:
                return 1
            if self.prerelease and other.prerelease:
                return cmp(self.prerelease, other.prerelease)
        else:
            return compare


class LooseVersion(Version):
    component_re = re.compile('(\\d+ | [a-z]+ | \\.)', re.VERBOSE)

    def __init__(self, vstring=None):
        if vstring:
            self.parse(vstring)

    def parse(self, vstring):
        self.vstring = vstring
        components = filter(lambda x: x and x != '.', self.component_re.split(vstring))
        for i in range(len(components)):
            try:
                components[i] = int(components[i])
            except ValueError:
                pass

        self.version = components

    def __str__(self):
        return self.vstring

    def __repr__(self):
        return "LooseVersion ('%s')" % str(self)

    def __cmp__(self, other):
        if isinstance(other, StringType):
            other = LooseVersion(other)
        return cmp(self.version, other.version)
