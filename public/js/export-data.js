document.getElementById("export-csv").onclick=async ()=>{
    const response = await fetch('./hero_data/herolist.json')
    const txt = await response.text()
    const items = txt
    const replacer = (key, value) => value === null ? '' : value // specify how you want to handle null values here
    const header = ["hero","skills","talents","limiter","blessings"]
    const csv = [
    header.join(','), // header row first
    ...items.map(row => header.map(fieldName => JSON.stringify(row[fieldName], replacer)).join(','))
    ].join('\r\n')
    console.log(csv)

    var exportedFilenmae = 'OPM_Data' + '.csv' || 'export.csv';
    var blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    if (navigator.msSaveBlob) { // IE 10+
        navigator.msSaveBlob(blob, exportedFilenmae);
    } else {
        var link = document.createElement("a");
        if (link.download !== undefined) { // feature detection
            // Browsers that support HTML5 download attribute
            var url = URL.createObjectURL(blob);
            link.setAttribute("href", url);
            link.setAttribute("download", exportedFilenmae);
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            //link.click();
            document.body.removeChild(link);
        }
    }
}
