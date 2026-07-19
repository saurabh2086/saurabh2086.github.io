ObjC.import('PDFKit');
ObjC.import('Foundation');

function run() {
    var bdaPath = '/Users/turtle/Documents/projects/saurabh2086.github.io/bda3/book/BDA3.pdf';
    var pdfUrl = $.NSURL.fileURLWithPath(bdaPath);
    var pdfDoc = $.PDFDocument.alloc.initWithURL(pdfUrl);
    if (!pdfDoc) {
        return "Could not load PDF";
    }
    
    var pageCount = pdfDoc.pageCount;
    var occurrences = [];
    
    for (var i = 0; i < pageCount; i++) {
        var page = pdfDoc.pageAtIndex(i);
        var text = page.string.js;
        if (text.indexOf('Nevada') !== -1 && text.indexOf('Utah') !== -1 && text.indexOf('divorce') !== -1) {
            occurrences.push("=== PDF PAGE " + i + " ===\n" + text);
        }
    }
    
    return occurrences.join("\n\n=========================================\n\n");
}
