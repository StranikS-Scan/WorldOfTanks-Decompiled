# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ab_feature_test_token_based_shared.py
import typing
_AB_TEST_TOKEN_DELIMITER = ':'
_AB_TEST_TOKEN_PREFIX = 'ab_test'

def getFeatures(tokenNames):
    return dict((parseABTestToken(t) for t in tokenNames if isABTestToken(t)))


def getGroupByFeature(tokenNames, featureName):
    for t in tokenNames:
        if isABTestFeatureToken(t, featureName):
            _, group = parseABTestToken(t)
            return group

    return None


def isABTestToken(tokenName):
    return tokenName.startswith(_AB_TEST_TOKEN_PREFIX + _AB_TEST_TOKEN_DELIMITER)


def isABTestFeatureToken(tokenName, featureName):
    return tokenName.startswith(_AB_TEST_TOKEN_PREFIX + _AB_TEST_TOKEN_DELIMITER + featureName)


def parseABTestToken(tokenName):
    tokenParts = tokenName.split(_AB_TEST_TOKEN_DELIMITER)
    return (tokenParts[1], tokenParts[2])


def formatABTestToken(featureName, groupName, additionalInfo=None):
    tokenParts = [_AB_TEST_TOKEN_PREFIX, featureName, groupName]
    if additionalInfo is not None:
        tokenParts.append(additionalInfo)
    return _AB_TEST_TOKEN_DELIMITER.join(tokenParts)
