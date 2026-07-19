const jStat = require('jstat');

const nSimulations = 10000;

function getBetaParams(mean, stdDev) {
    if (stdDev <= 0.001) return null;
    let maxStdDev = Math.sqrt(mean * (1 - mean));
    if (stdDev >= maxStdDev) stdDev = maxStdDev * 0.99;
    let v = stdDev * stdDev;
    let nu = (mean * (1 - mean) / v) - 1;
    return { alpha: mean * nu, beta: (1 - mean) * nu };
}

function simulate() {
    const sections = [
        { q: 10, m: 1, mean: 0.95, stdDev: 0.05 },
        { q: 10, m: 2, mean: 0.85, stdDev: 0.04 }, // changed from 0.10 to 0.04
        { q: 2, m: 5, mean: 0.70, stdDev: 0.10 }
    ];
    let totalMarks = 0;
    let totalScores = new Float32Array(nSimulations);
    
    for (let sec of sections) {
        let marks = sec.q * sec.m;
        totalMarks += marks;
        let params = getBetaParams(sec.mean, sec.stdDev);
        
        for (let i = 0; i < nSimulations; i++) {
            let acc = params ? jStat.beta.sample(params.alpha, params.beta) : sec.mean;
            if (acc < 0) acc = 0;
            if (acc > 1) acc = 1;
            totalScores[i] += acc * marks;
        }
    }
    
    let percentageScores = new Float32Array(nSimulations);
    let sum = 0;
    
    for (let i = 0; i < nSimulations; i++) {
        let pct = (totalScores[i] / totalMarks) * 100;
        percentageScores[i] = pct;
        sum += pct;
    }
    
    percentageScores.sort();
    let simMean = sum / nSimulations;
    
    let credMass = 0.94;
    let intervalCount = Math.floor(credMass * nSimulations);
    let minWidth = Infinity;
    let hdiLow = 0, hdiHigh = 0;
    
    for (let i = 0; i <= nSimulations - intervalCount; i++) {
        let width = percentageScores[i + intervalCount - 1] - percentageScores[i];
        if (width < minWidth) {
            minWidth = width;
            hdiLow = percentageScores[i];
            hdiHigh = percentageScores[i + intervalCount - 1];
        }
    }
    
    let p10 = percentageScores[Math.floor(nSimulations * 0.10)];
    console.log("Mean:", simMean.toFixed(1) + '%');
    console.log("HDI Low:", hdiLow.toFixed(1) + '%');
    console.log("HDI High:", hdiHigh.toFixed(1) + '%');
    console.log("p10:", p10.toFixed(1) + '%');
}

simulate();
