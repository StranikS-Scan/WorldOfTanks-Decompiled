# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ab_feature_test_token_based_shared.py
import typing
_AB_TEST_TOKEN_DELIMITER = ':'
_AB_TEST_TOKEN_PREFIX = 'ab_test'

def getFeatures(tokenNames):
    return dict((parseABTestToken(t) for t in tokenNames if isABTestToken(t)))


def isABTestToken(tokenName):
    return tokenName.startswith(_AB_TEST_TOKEN_PREFIX + _AB_TEST_TOKEN_DELIMITER)


def parseABTestToken(tokenName):
    tokenParts = tokenName.split(_AB_TEST_TOKEN_DELIMITER)
    return (tokenParts[1], tokenParts[2])
