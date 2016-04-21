var __version__ = "0.1.1"

function openPdfs(urls, openPdfCallback) {
    var pdfs = []
    var endsWithPDF = /pdf$/;
    urls.forEach(function(url) {
        if (endsWithPDF.test(url.toLowerCase())) {
            // console.log("is pdf:", url)
            pdfs.push(url)
        }
    });

    if (pdfs.length === 0) {
        console.log("No PDFs!")
        return false
    }

    openPdfCallback(pdfs)
    return true
}
