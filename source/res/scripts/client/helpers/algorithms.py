# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/algorithms.py
import heapq
import typing
if typing.TYPE_CHECKING:
    from typing import Dict, List, Tuple
T = typing.TypeVar('T')

def shortestPath(graph, start, end):
    pq = []
    heapq.heappush(pq, (0.0, start))
    distances = {node:float('inf') for node in graph}
    distances[start] = 0.0
    previous = {node:None for node in graph}
    while pq:
        currentDistance, currentNode = heapq.heappop(pq)
        if currentDistance > distances[currentNode]:
            continue
        for node, distance in graph[currentNode]:
            distance += currentDistance
            if distance < distances[node]:
                distances[node] = distance
                heapq.heappush(pq, (distance, node))
                previous[node] = currentNode

    path = []
    if previous[start] is not None and start != end:
        return path
    else:
        while end is not None:
            path.append(end)
            end = previous[end]

        return path[::-1]
