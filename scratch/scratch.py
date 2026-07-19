import math
import random

nSimulations = 100000

def getBetaParams(mean, stdDev):
    if stdDev <= 0.001: return None
    maxStdDev = math.sqrt(mean * (1 - mean))
    if stdDev >= maxStdDev: stdDev = maxStdDev * 0.99
    v = stdDev * stdDev
    nu = (mean * (1 - mean) / v) - 1
    return {'alpha': mean * nu, 'beta': (1 - mean) * nu}

sections = [
    {'q': 10, 'm': 1, 'mean': 0.95, 'stdDev': 0.05},
    {'q': 10, 'm': 2, 'mean': 0.85, 'stdDev': 0.075},
    {'q': 2, 'm': 5, 'mean': 0.70, 'stdDev': 0.10}
]

totalMarks = 0
totalScores = [0] * nSimulations

for sec in sections:
    marks = sec['q'] * sec['m']
    totalMarks += marks
    params = getBetaParams(sec['mean'], sec['stdDev'])
    
    for i in range(nSimulations):
        if params:
            acc = random.betavariate(params['alpha'], params['beta'])
        else:
            acc = sec['mean']
            
        if acc < 0: acc = 0
        if acc > 1: acc = 1
        totalScores[i] += acc * marks

percentageScores = sorted([(score / totalMarks) * 100 for score in totalScores])

simMean = sum(percentageScores) / nSimulations

credMass = 0.94
intervalCount = int(credMass * nSimulations)
minWidth = float('inf')
hdiLow = 0
hdiHigh = 0

for i in range(nSimulations - intervalCount + 1):
    width = percentageScores[i + intervalCount - 1] - percentageScores[i]
    if width < minWidth:
        minWidth = width
        hdiLow = percentageScores[i]
        hdiHigh = percentageScores[i + intervalCount - 1]

p10 = percentageScores[int(nSimulations * 0.10)]

print(f"Mean: {simMean:.1f}%")
print(f"HDI Low: {hdiLow:.1f}%")
print(f"HDI High: {hdiHigh:.1f}%")
print(f"p10: {p10:.1f}%")
