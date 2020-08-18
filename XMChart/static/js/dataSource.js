
function replaceAll(str, beforeStr, afterStr){
    var reg = new RegExp(beforeStr, "g");
    return str.replace(reg, afterStr);
}

function dataConvert(dic) {
    format = d3.time.format("%Y/%M/%d %H:%M:%S");
    let data = dic.map(function(d){
    return  {time: new Date(d.time),
            open: parseFloat(d.open),
            high: parseFloat(d.high),
            low: parseFloat(d.low),
            close: parseFloat(d.close),
            volume: parseFloat(d.volume)};
    });
    return data;
}

function parse(json) {
    let jsonString = replaceAll(json, '&#34;', '"');
    let obj = JSON.parse(jsonString);
    let name = obj['name'];
    let timeframe = obj['timeframe'];
    let length = obj['length'];
    let d = obj['data'];
    let data = dataConvert(d);
    return [name, timeframe, length, data];
}

