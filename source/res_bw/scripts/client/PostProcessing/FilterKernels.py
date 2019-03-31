# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PostProcessing/FilterKernels.py
# Compiled at: 2010-05-25 20:46:16


def straightTransfer4Tap():
    samples = []
    samples.append((0.0, 0.0, 1.0))
    samples.append((0.0, 0.0, 0.0))
    samples.append((0.0, 0.0, 0.0))
    samples.append((0.0, 0.0, 0.0))
    return samples


def mean4Tap():
    """This set of filter samples implements a 4-tap
    averaging filter"""
    samples = []
    samples.append((-1.0, 0.0, 0.25))
    samples.append((-1.0, 1.0, 0.25))
    samples.append((1.0, 1.0, 0.25))
    samples.append((1.0, 0.0, 0.25))
    return samples


def mean9Tap():
    """This set of filter samples implements a 9-tap
    averaging filter"""
    samples = []
    w = 1.0 / 9.0
    samples.append((-1.0, -1.0, w))
    samples.append((-1.0, 0.0, w))
    samples.append((-1.0, 1.0, w))
    samples.append((0.0, -1.0, w))
    samples.append((0.0, 0.0, w))
    samples.append((0.0, 1.0, w))
    samples.append((1.0, -1.0, w))
    samples.append((1.0, 0.0, w))
    samples.append((1.0, 1.0, w))
    samples.append((0.0, 0.0, 0.0))
    samples.append((0.0, 0.0, 0.0))
    samples.append((0.0, 0.0, 0.0))
    return samples


def gaussianBlur4Tap(horiz, width):
    """This set of filter samples implements a 12021 4-tap filter,
    and can be configured to be horizontal or vertical."""
    samples = []
    if horiz:
        samples.append((-2.5 * width, 0.0, 1.0 / 6.0))
        samples.append((-0.5 * width, 0.0, 2.0 / 6.0))
        samples.append((0.5 * width, 0.0, 2.0 / 6.0))
        samples.append((2.5 * width, 0.0, 1.0 / 6.0))
    else:
        samples.append((0.0, -2.5 * width, 1.0 / 6.0))
        samples.append((0.0, -0.5 * width, 2.0 / 6.0))
        samples.append((0.0, 0.5 * width, 2.0 / 6.0))
        samples.append((0.0, 2.5 * width, 1.0 / 6.0))
    return samples


def normaliseWeights(samples):
    total = 0.0
    for i in samples:
        total += i[2]

    for i in samples:
        i[2] /= total

    samples2 = []
    for i in samples:
        samples2.append(tuple(i))

    return samples2


def gaussianBlurNTap(horiz, n, stddev, width=1.0):
    samples = []
    import math
    twopi = math.pi * 2.0
    a = 1.0 / (math.sqrt(twopi) * stddev)
    twodevsq = 2 * stddev * stddev
    x = -n / 2.0 + 0.5
    for i in xrange(0, n):
        weight = a * math.exp(-(x * x) / twodevsq)
        if horiz:
            samples.append((x * width, 0.0, weight))
        else:
            samples.append((0.0, x * width, weight))
        x += 1

    return samples


def gaussianBlur24Tap(horiz, width=1.0):
    samples = []
    if horiz:
        samples.append([-10.6 * width, 0.0, 0.3327])
        samples.append([-9.6 * width, 0.0, 0.3557])
        samples.append([-8.6 * width, 0.0, 0.379])
        samples.append([-7.6 * width, 0.0, 0.4048])
        samples.append([-6.6 * width, 0.0, 0.4398])
        samples.append([-5.6 * width, 0.0, 0.4967])
        samples.append([-4.6 * width, 0.0, 0.5937])
        samples.append([-3.6 * width, 0.0, 0.7448])
        samples.append([-2.6 * width, 0.0, 0.9418])
        samples.append([-1.6 * width, 0.0, 1.1414])
        samples.append([-0.6 * width, 0.0, 1.2757])
        samples.append([0.4 * width, 0.0, 1.2891])
        samples.append([1.4 * width, 0.0, 1.1757])
        samples.append([2.4 * width, 0.0, 0.9835])
        samples.append([3.4 * width, 0.0, 0.7814])
        samples.append([4.4 * width, 0.0, 0.6194])
        samples.append([5.4 * width, 0.0, 0.5123])
        samples.append([6.4 * width, 0.0, 0.4489])
        samples.append([7.4 * width, 0.0, 0.4108])
        samples.append([8.4 * width, 0.0, 0.3838])
        samples.append([9.4 * width, 0.0, 0.3603])
        samples.append([10.4 * width, 0.0, 0.3373])
        samples.append([0.0, 0.0, 0.0])
        samples.append([0.0, 0.0, 0.0])
    else:
        samples.append([0.0, -10.6 * width, 0.3327])
        samples.append([0.0, -9.6 * width, 0.3557])
        samples.append([0.0, -8.6 * width, 0.379])
        samples.append([0.0, -7.6 * width, 0.4048])
        samples.append([0.0, -6.6 * width, 0.4398])
        samples.append([0.0, -5.6 * width, 0.4967])
        samples.append([0.0, -4.6 * width, 0.5937])
        samples.append([0.0, -3.6 * width, 0.7448])
        samples.append([0.0, -2.6 * width, 0.9418])
        samples.append([0.0, -1.6 * width, 1.1414])
        samples.append([0.0, -0.6 * width, 1.2757])
        samples.append([0.0, 0.4 * width, 1.2891])
        samples.append([0.0, 1.4 * width, 1.1757])
        samples.append([0.0, 2.4 * width, 0.9835])
        samples.append([0.0, 3.4 * width, 0.7814])
        samples.append([0.0, 4.4 * width, 0.6194])
        samples.append([0.0, 5.4 * width, 0.5123])
        samples.append([0.0, 6.4 * width, 0.4489])
        samples.append([0.0, 7.4 * width, 0.4108])
        samples.append([0.0, 8.4 * width, 0.3838])
        samples.append([0.0, 9.4 * width, 0.3603])
        samples.append([0.0, 10.4 * width, 0.3373])
        samples.append([0.0, 0.0 * width, 0.0])
        samples.append([0.0, 0.0 * width, 0.0])
    return normaliseWeights(samples)


def sharpFilter(k=1):
    samples = []
    samples.append((-1.0, -1.0, -1))
    samples.append((0.0, -1.0, -1))
    samples.append((1.0, -1.0, -1))
    samples.append((-1.0, 0.0, -1))
    samples.append((0.0, 0.0, 9))
    samples.append((1.0, 0.0, -1))
    samples.append((-1.0, 1.0, -1))
    samples.append((0.0, 1.0, -1))
    samples.append((1.0, 1.0, -1))
    samples.append((0.0, 0.0, 0.0))
    samples.append((0.0, 0.0, 0.0))
    samples.append((0.0, 0.0, 0.0))
    return samples


def edgeDetectFilter(k=1):
    samples = []
    samples.append((-1.0, -1.0, -1))
    samples.append((0.0, -1.0, -1))
    samples.append((1.0, -1.0, -1))
    samples.append((-1.0, 0.0, -1))
    samples.append((0.0, 0.0, 8))
    samples.append((1.0, 0.0, -1))
    samples.append((-1.0, 1.0, -1))
    samples.append((0.0, 1.0, -1))
    samples.append((1.0, 1.0, -1))
    samples.append((0.0, 0.0, 0.0))
    samples.append((0.0, 0.0, 0.0))
    samples.append((0.0, 0.0, 0.0))
    return samples


def embossFilter(k=1):
    samples = []
    samples.append((-1.0, 1.0, 2))
    samples.append((0.0, 1.0, 0))
    samples.append((1.0, 1.0, 0))
    samples.append((-1.0, 0.0, 0))
    samples.append((0.0, 0.0, -1))
    samples.append((1.0, 0.0, 0))
    samples.append((-1.0, -1.0, 0))
    samples.append((0.0, -1.0, 0))
    samples.append((1.0, -1.0, -1))
    samples.append((0.0, 0.0, 0.0))
    samples.append((0.0, 0.0, 0.0))
    samples.append((0.0, 0.0, 0.0))
    return samples
