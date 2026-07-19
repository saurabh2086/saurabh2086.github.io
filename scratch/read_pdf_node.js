const fs = require('fs');

const path = require('path');
const data = fs.readFileSync(path.join(__dirname, '..', 'bda3', 'book', 'Solution_BDA3.pdf'));
console.log('Solution_BDA3.pdf read successfully. Size:', data.length);

// Let's search for "Exchangeable models" or similar in the PDF file
const searchStr = "Exchangeable";
let index = 0;
let count = 0;
while ((index = data.indexOf(searchStr, index)) !== -1) {
    count++;
    console.log(`Found occurrence ${count} at index ${index}`);
    // Print 300 characters around the index
    const start = Math.max(0, index - 100);
    const end = Math.min(data.length, index + 400);
    const snippet = data.slice(start, end);
    console.log("ASCII representation:");
    console.log(snippet.toString('ascii').replace(/[^\x20-\x7E\n]/g, '.'));
    console.log("-".repeat(40));
    index += searchStr.length;
}
