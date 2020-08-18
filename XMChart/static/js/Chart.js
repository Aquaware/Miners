const MINUTE = 'M';
const HOUR = 'H';
const DAY = 'D';

const zip = (arr1, arr2) => arr1.map((k, i) => [k, arr2[i]]);

function minmaxOfArray(array) {
    if (array.length == 0) {
        return [NaN, NaN];
    }
    var min = NaN;
    var max = NaN;
    for (let i = 0; i < array.length; i++) {
        if (array[i]) {
            if (!min || !max) {
                min = array[i];
                max = array[i];
            } else {
                if (array[i] < min) {
                    min = array[i];
                }
                if (array[i] > max) {
                    max = array[i];
                }
            }
        }
    }
    return [min, max];
}

function separate(value) {
    if (value == 0.0) {
        return [0.0, 0.0];
    }
    if (value >= 1.0 && value < 10.0) {
        return [value, 1.0];
    }
    if (value >= 10.0) {
        for (let base = 1; base < 100; base++) {
            let v =  value / Math.pow(10, base);
            if (v < 10.0) {
                return [v, Math.pow(10, base)];
            }
        }
    } else {
        for (let base = 1; base < 100; base++) {
            let v = value * Math.pow(10, base);
            if (v >= 1.0) {
                return [v, 1.0 / Math.pow(10, base)];
            }
        }
    }
    return [0.0, 0.0];
}

function nice(niceNumbers, value) {
    let [mantissa, exponent] = separate(value);
    var dif = []
    for (let num of niceNumbers) {
        dif.push(Math.abs(mantissa - num))
    }
    let index = dif.indexOf(Math.min.apply(null, dif));
    return niceNumbers[index] * exponent;
}

function niceRange(a, b, divide) {
    let niceNumbers = [1.0, 2.0, 2.5, 5.0, 10.0];
    let d = Math.abs((a - b) / divide);
    let division = nice(niceNumbers, d);
    let aa = parseInt(a / division) * division;
    if (aa >= a) {
        aa -= division;
    }
    let bb = parseInt (b / division) * division;
    if (bb <= b) {
        bb += division;
    }
    var array = []
    for (let v = aa; v <= bb; v += division) {
        if (v >= a && v <= b) {
            array.push(v);
        }
    }
    return array;
}

function deltaMinutes(time, minutes) {
    var out = new Date(time.getTime());
    out.setMinute(out.getMinutes() + minutes);
    return out;
}

function deltaHours(time, hours) {
    var out = new Date(time.getTime());
    out.setHours(out.getHours() + hours);
    return out;
}

function deltaDays(time, days) {
    var out = new Date(time.getTime());
    out.setDate(out.getDate() + days);
    return out;
}

function dateFormat(date, format) {
    let adate = new Date(date);
    format = format.replace(/yyyy/g, adate.getFullYear());
    format = format.replace(/MM/g, ('0' + (adate.getMonth() + 1)).slice(-2));
    format = format.replace(/dd/g, ('0' + adate.getDate()).slice(-2));
    format = format.replace(/HH/g, ('0' + adate.getHours()).slice(-2));
    format = format.replace(/mm/g, ('0' + adate.getMinutes()).slice(-2));
    format = format.replace(/ss/g, ('0' + adate.getSeconds()).slice(-2));
    format = format.replace(/SSS/g, ('00' + adate.getMilliseconds()).slice(-3));
    return format;
}

function date2Str (date, timeframe) {
    let [value, unit, minutes] = timeframe;
    var format1 = null;
    var format2 = null;
    if (unit == DAY) {
        format1 = "MM-dd";
        format2 = "yyyy";
    } else if (unit == HOUR) {
        format1 = "MM-dd HH";
        format2 = "yyyy"
    } else if (unit == MINUTE) {
        format1 = 'HH:mm';
        format2 = "MM-dd"
    }

    let str1 = dateFormat(date, format1);
    let str2 = dateFormat(date, format2);
    return [str1, str2];
}

function round(value, order) {
    return Math.floor(value * Math.pow(10, order ) + 0.5) / Math.pow(10, order);
}

function number2Str(value) {
    const order = 3;
    if (value == 0) {
        return "0";
    }
    if (Number.isInteger(value)) {
        return String(value);
    }
    let v = round(value, order);
    return String(v);
}

function nearest1(value, nears) {
    var dif = [];
    for( let v of nears) {
        dif.push(Math.abs(value - v));
    }
    let index = dif.indexOf(Math.min.apply(null, dif));
    return nears[index];
}

function nearest2(value, begin, delta) {
    var difmin, min;
    for(let v = begin; v < begin + 1000 * delta; v+= delta) {
        dif = Math.abs(value - v);
        if (v == begin) {
            difmin = dif;
            min = v;
        }
        if (dif > difmin) {
            break;
        }
    }
    return min;
}

function roundMinute(time, minutes) {
    var array = [];
    for (let m of minutes) {
        let t = new Date(time.getFullYear(), time.getMonth(), time.getDate(), time.getHours(), m);
        array.push(t);
        array.push(deltaHours(t, -1));
        array.push(deltaHours(t, 1));
    }
    var dif = [];
    for (let v of array) {
        dif.push(Math.abs(time.getTime() - v.getTime()));
    }
    let index = dif.indexOf(Math.min.apply(null, dif));
    return array[index];
}

function roundHour(time, hours) {
    var array = [];
    for (let h of hours) {
        let t = new Date(time.getFullYear(), time.getMonth(), time.getDate(), h);
        array.push(t);
        array.push(deltaDays(t, -1));
        array.push(deltaDays(t, 1));
    }
    var dif = [];
    for (let v of array) {
        dif.push(Math.abs(time.getTime() - v.getTime()));
    }
    let index = dif.indexOf(Math.min.apply(null, dif));
    return array[index];
}

function roundDay(time, days) {
    var array = [];
    for (let d of days) {
        let t = new Date(time.getFullYear(), time.getMonth(), d);
        array.push(t);
        array.push(deltaDays(t, -1));
        array.push(deltaDays(t, 1));
    }
    var dif = [];
    for (let v of array) {
        dif.push(Math.abs(time.getTime() - v.getTime()));
    }
    let index = dif.indexOf(Math.min.apply(null, dif));
    return array[index];
}

function niceTimeRange(iMin, iMax, time, timeframe, divide) {
    let [value, unit, minutes] = timeframe;
    let division = parseInt(iMax / divide);
    var delta, interval, tbegin;

    if (unit == DAY) {
        delta = nearest2(division, 10, 10);
        tbegin = time[0];
        array = [];
        for (let i = 0; i <= iMax; i += parseInt(delta)) {
            array.push([i, time[i]]);
        }
        return array;
    }
    
    if(unit == MINUTE) {
        if (value == 1) {
            delta = nearest1(division, [5, 10, 15]);
            tbegin = roundMinute(time[0], [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]);
        } else {
            delta = nearest2(division, value * 6, 30);
            tbegin = roundMinute(time[0], [0, 15, 30, 45]);
        }
        interval = delta * (60 * 1000);
    } else if (unit == HOUR) {
        delta = nearest2(division, value * 6, 12);
        interval = delta * (60 * 60 * 1000);
        tbegin = time[0]; //roundHour(time[0], [0, 4, 8, 12, 16, 20]);
    }
    var array = [];
    var t = tbegin.getTime();
    for (var i = 0; i < division + 1; i++) {
        t += interval;
        let t0 = new Date(t);
        if (t >= time[time.length - 1].getTime()) {
            array.push([array[array.length - 1][0] + delta / value, null])
            break;
        }
        for (var j = 0; j < time.length; j++) {
            if (t == time[j].getTime()) {
                if (i == 0) {
                    let ibefore = j - parseInt(delta / value);
                    if (ibefore >= iMin) {
                        array.push([ibefore, new Date(t - interval)]);
                    }
                }
                array.push([j, t0]);
            }
        }
    }

    return array;
}

// ---- draw primitives ----
function line(context, pos1, pos2, lineWidth=1.0, style="solid") {
    context.lineWidth = lineWidth;
    if (style.toLowerCase() == "dot") {
        let dash = [1, 1];
        context.setLineDash(dash);
    }
    context.beginPath();
    context.moveTo(pos1[0], pos1[1]);
    context.lineTo(pos2[0], pos2[1]);
    context.closePath();
    context.stroke();
}

function boxedText(context, point, text, color) {



}

// ------


class Scale {
    constructor(domain, range, type, time, timeframe) {
        this.domain = domain;
        this.range = range;
        if (type === undefined) {
            type = "linear"
        }
        this.type = type;
        if (type == "linear" || type == "bartime") {
            let delta1 = range[1] - range[0];
            let delta2 = domain[1] - domain[0];
            if (delta1 == 0.0 || delta2 == 0.0) {
                this.rate = 1.0;
            } else {
                this.rate = delta1 / delta2;
            }
        } else if (type == "time") {
            let delta1 = range[1] - range[0];
            let delta2 = domain[1].getTime() - domain[0].getTime();
            if (delta1 == 0.0 || delta2 == 0.0) {
                this.rate = 0.0;
            } else {
                this.rate = delta1 / delta2;
            }            
        } 

        if (type == "bartime") {
            this.time = time;
            this.timeframe = timeframe;
        } else{
            this.time = null;
            this.timeframe = null;
        }
    }
    
    pos(value) {
        if (this.type == "linear" || this.type == "bartime") {
            // pos = (value - real0) * (screen1 - screen0) / (real1 - real0) + screen0
            let v = value - this.domain[0];
            return v * this.rate + this.range[0];
        } else if (this.type == "time") {
            let v = value.getTime() - this.domain[0].getTime();
            return v * this.rate + this.range[0];
        }
    }

    value(pos) {
        if (this.type == "linear" || this.type == "bartime") {
            // value = (pos - screen0) / (screen1 - screen0) * (real1 - real0) + real0
            if (this.rate == 0.0) {
                return 0.0;
            }
            let v = (pos - this.range[0]) / this.rate + this.domain[0];
            if (this.type == "bartime") {
                return parseInt(v + 0.5);
            } else {
                return v;
            }
        } else if (this.type == "time") {
            let v = (pos - this.range[0]) / this.rate + this.domain[0];
            return new Date(v);
        }
    }

    rangeWidth() {
        let w = Math.abs(this.range[0] - this.range[1]);
        return w;
    }

    domainWidth() {
        let w = Math.abs(this.domain[0] - this.domain[1]);
        return w;
    }

    rangeLowerUpper() {
        let lower = this.range[0];
        let upper = this.range[1];
        if (upper < lower) {
            let tmp = lower;
            lower = upper;
            upper = tmp;
        }
        return [lower, upper];
    }

    domainLowerUpper() {
        let lower = this.domain[0];
        upper = this.domain[1];
        if (upper < lower) {
            let tmp = lower;
            lower = upper;
            upper = tmp;
        }
        return [lower, upper];
    }

}

class GraphicObject {

    style(prop) {
        try {
            this.context.globalAlpha = prop['opacity'];
        } catch(e) {
        }
        try {
            this.context.lineColor = prop['lineColor'];
        } catch(e) {
        }
        try {
            this.context.fillStyle = prop['fillColor'];
        } catch(e) {
        }
    }

    draw(context, xScale, yScale) {
    }
}

class Square extends GraphicObject {
    constructor(cx, cy, width, height, prop) {
        this.cx = cx;
        this.cy = cy;
        this.width = width;
        this.height = height;
        this.prop = prop;
    }
    
    draw(context, xScale, yScale) {
        super.style(prop);
        let x = xScale.pos(this.cx);
        let y = yScale.pos(this.cy);
        let x0 = x - this.width / 2;
        let y0 = y - this.height / 2;
        context.fillRect(x0, y0, this.width, this.height);
    }
}

class Candle  {
    constructor(index, time, open, high, low, close, showLength, prop) {
        this.index = index;
        this.time = time;
        this.open = open;
        this.high = high;
        this.low = low;
        this.close = close;
        this.showLength = showLength;
        this.prop = prop;
    }
    
    draw(context, xScale, yScale) {
        let width = this.candleWidth(xScale.rangeWidth(), this.showLength);
        let x = xScale.pos(this.index);
        let x0 = x - width / 2;
        var upper, lower, bodyColor, lineColor;
        if (this.open < this.close) {
            upper = yScale.pos(this.close);
            lower = yScale.pos(this.open);
            bodyColor = "#007744";
            lineColor = "green"
        } else {
            upper = yScale.pos(this.open);
            lower = yScale.pos(this.close);
            bodyColor = "red";
            lineColor = "pink"    
        }
        // body
        context.globalAlpha = 0.5;
        context.fillStyle = bodyColor;
        context.fillRect(x0, lower, width, upper - lower);

        // upper line
        context.globalAlpha = 0.7;
        context.strokeStyle = lineColor;
        line(context, [x, yScale.pos(this.high)], [x, upper]);

        // lower line
        line(context, [x, lower], [x, yScale.pos(this.low)]);
    }


    candleWidth(range, barSize) {
        let w = parseInt(range / barSize / 2);
        if (w < 0) {
            w = 1;
        } else if (w > 10) {
            w = 10;
        }
        return w;
    }
}

class PolyLine extends GraphicObject {
    constructor(points, prop, shouldFill=false) {
        super();
        this.points = points;
        this.prop = prop;
        this.shouldFill= shouldFill;
    }
    
    draw(context, xScale, yScale) {
        context.globalAlpha = this.prop["opacity"];
        context.strokeStyle = this.prop["lineColor"];
        context.lineWidth = this.prop["lineWidth"];
        context.beginPath();
        let isFirst = true;
        for (let p of this.points) {
            let x = xScale.pos(p[0]);
            let y = yScale.pos(p[1]);
            if (isFirst) {
                context.moveTo(x, y);
                isFirst = false;
                continue;
            }
            context.lineTo(x, y);
        }
        //this.context.closePath();
        context.stroke();
        if (this.shouldFill) {
            context.fill();
        }
    }
}

class Axis {
    constructor(scale, level, mainDivision, subDivision, isHorizontal, time, timeframe) {
        this.scale = scale;
        this.level = level;
        this.mainDivision = mainDivision;
        this.subDivision = subDivision;
        this.isHorizontal = isHorizontal;
        if (time === undefined) {
            this.time = null;
            this.timeframe = null;
        } else {
            this.time = time;
            this.timeframe = this.parseTimeframe(timeframe);
        }
    }

    parseTimeframe(timeframe) {
        let unit = timeframe.substring(0, 1);
        let figure = parseInt(timeframe.substring(1));
        var minutes;
        if (unit == MINUTE) {
            minutes = figure;
        } else if(unit == HOUR) {
            minutes = figure * 60;
        } else if (unit == DAY) {
            minutes = figure * 24 * 60;
        }
        return [figure, unit, minutes];
    }

    draw(context) {
        context.globalAlpha = 0.3;
        context.fillStyle = "black";
        var lower, upper, value;

        if (this.scale.type == "linear") {
            lower = this.scale.domain[0];
            upper = this.scale.domain[1];
            if (upper < lower) {
                let tmp = lower;
                lower = upper;
                upper = tmp;
            }
        } else if (this.scale.type == "time") {
            lower = this.scale.domain[0].getTime();
            upper = this.scale.domain[1].getTime();   
        }

        // grid
        context.lineWidth = 0.2;
        context.font = 'bold 10px Times Roman';
        context.strokeStyle = "grey";
        var range;
        if (this.scale.type == "linear") {
            range = niceRange(lower, upper, this.mainDivision);
        } else if (this.scale.type == "bartime") {
            range = niceTimeRange(this.scale.domain[0], this.scale.domain[1], this.time, this.timeframe, this.mainDivision);
        } else if (this.scale.type == "time") {
            range = niceTimeRange(this.scale.domain[0], this.scale.domain[1]);
        }
        for (let v of range) {

            if (this.scale.type == "linear") {
                value = this.scale.pos(v);
            } else if (this.scale.type == "bartime") {
                value = this.scale.pos(v[0]);
            } else if (this.scale.type == "time") {
                value = this.scale.pos(new Date(v));
            }
            if (this.isHorizontal) {
                const labelMargin = 5;
                context.textAlign = "center";
                context.textBaseline = "top";
                line(context, [value, this.level[0]], [value, this.level[1]])
                context.globalAlpha = 1.0;
                var s = [null, null];
                if (this.scale.type == "linear") {
                    s = [number2Str(v), ""];
                } else if (this.scale.type == "bartime") {
                    if (v[1]) {
                        s = date2Str(v[1], this.timeframe);
                    } else {
                        s = "";
                    }
                } else if (this.scale.type == "time") {
                    s = date2Str(new Date(v), "HH:mm");
                }
                if (s[0]) {
                    context.fillText(s[0], value, this.level[0] + labelMargin);
                }
                if (s[1]) {
                    context.fillText(s[1], value, this.level[0] + labelMargin + 15);
                }
                context.globalAlpha = 0.3;
            } else {
                context.textAlign = "right";
                context.textBaseline = "middle";
                line(context, [this.level[0], value], [this.level[1], value])
                context.globalAlpha = 1.0;
                context.fillText(number2Str(v), this.level[0], value);
                context.globalAlpha = 0.3;
            }
            context.stroke();
        }

        if (this.isHorizontal) {
            line(context, [this.scale.range[0], this.level[0]], [this.scale.range[1], this.level[0]], 2.0);
            line(context, [this.scale.range[0], this.level[1]], [this.scale.range[1], this.level[1]], 2.0);
        } else {
            line(context, [this.level[0], this.scale.range[0]], [this.level[0], this.scale.range[1]], 2.0);
            line(context, [this.level[1], this.scale.range[0]], [this.level[1], this.scale.range[1]], 2.0);
        }
        context.stroke();
    }
}

class Graph {
    constructor(context, timeScale, scales) {
        this.context = context;
        this.timeScale = timeScale;
        this.scales = scales;
    }

    isInner(point) {
        let [x, y] = point;
        var index = -1;
        for (let i = 0; i < this.scales.length; i++) {
            let scale = this.scales[i];
            let xval = this.timeScale.value(x);
            let [lower, upper] = scale.rangeLowerUpper();
            let tmp = this.timeScale.domain;
            if (xval >= 0 && xval <= this.timeScale.domain[1]) {
                if (y >= lower && y <= upper) {
                    index = i;
                    break;
                }
            }
        }
        return index;
    }

    updateScaleDomain(index, domain) {
        let oldScale = this.scales[index];
        let scale = new Scale(domain, oldScale.range, oldScale.type);
        this.scales[index] = scale;
    }

    draw(index, graphicObject) {
        graphicObject.draw(this.context, this.timeScale, this.scales[index]);
    }

    drawAxis() {
        let time = this.timeScale.time;
        let timeframe = this.timeScale.timeframe;
        for (let i = 0; i < this.scales.length; i++) {
            let scale = this.scales[i];
            let xAxis = new Axis(this.timeScale, scale.range, 5, 2, true, time, timeframe);
            xAxis.draw(this.context);
            let yAxis = new Axis(scale, this.timeScale.range, 5, 2, false);
            yAxis.draw(this.context); 
        }
    }

    drawCursor(index, candle) {
        this.context.globalAlpha = 1.0;
        let scale = this.scales[index];
        let y = scale.pos(candle.close);
        this.context.strokeStyle = "#ccaaff";
        line(this.context, [this.timeScale.range[0], y], [this.timeScale.range[1], y], 0.5);
        this.context.font = "12px Arial";
        this.context.textAlign = "right";
        this.context.textBaseline = "middle";
        this.context.fillStyle = "#aaaaff";
        let [lower, upper] = this.timeScale.rangeLowerUpper();
        this.context.fillRect(upper - 45, y - 5, 45, 16);
        this.context.fillStyle = "#444444";
        this.context.fillText(String(round(candle.close, 4)), upper -5 , y + 4);
    }

    drawCross(index, point, candles) {
        let scale = this.scales[index];
        let [lower, upper] = this.timeScale.rangeLowerUpper();
        let [x, y] = point;

        let color = "#ccdd77";
        this.context.globalAlpha = 0.5;
        let xvalue = this.timeScale.value(x);
        this.context.strokeStyle = color;
        line(this.context, [x, scale.range[0]], [x, scale.range[1]]);
        let yvalue = scale.value(y);
        line(this.context, [this.timeScale.range[0], y], [this.timeScale.range[1], y]);

        this.context.globalAlpha = 0.8;
        this.context.font = "11px Arial";
        this.context.textAlign = "left";
        this.context.textBaseline = "middle";
        this.context.fillStyle = color;
        let dispx = lower + 5;
        this.context.fillRect(dispx, y - 10, 40, 20);
        this.context.fillStyle = "#000000";
        this.context.fillText(String(round(yvalue, 4)), dispx, y + 3);
        if (xvalue < 0 || xvalue > candles.length - 1) {
            return;
        }
        let candle = candles[xvalue];
        dispx = upper - 150;
        this.context.fillStyle = "black";
        this.context.font = "11px Arial";
        this.context.fillText("Time: " + dateFormat(candle.time, "yyyy/MM/dd HH:mm"), dispx, 45);
        this.context.fillText("Open: " + String(round(candle.open, 5)), dispx, 60);
        this.context.fillText("Close: " + String(round(candle.close, 5)), dispx + 80, 60);
        this.context.fillText("High: " + String(round(candle.high, 5)), dispx, 75);
        this.context.fillText("Low: " + String(round(candle.low, 5)), dispx + 80, 75);
    }
}

class Chart {
    constructor(canvas, size) {
        this.canvas = canvas;
        this.width = size.size.width;
        this.height = size.size.height;
        this.margin = size.margin;
        this.context = canvas.getContext('2d');
        canvas.width = size.size.width;
        canvas.height = size.size.height;
        this.graphHeights = size.heights;
        this.timeframe = null;
        this.showLength = 30;
        this.tohlc = null;
        this.graph = null;
        this.crossPoint = null;
        this.eventControl();
        this.showLength = 30;
    }

    setBarNumber(number) {
        this.showLength = number;
        this.update()
    }

    load(name, tohlc, timeframe) {
        this.name = name;
        this.tohlc = tohlc;
        this.timeframe = timeframe;
        this.render();
    }

    update() {
        var self = this;
        setInterval(function(e) {
            self.render();}
        , 1000 / 30);
    }

    createGraph(data, minmax) {
        const bar_left_margin = 5;
        const bar_right_margin = 10;
        if (!data) {
            return;
        }

        let length = data.length;
        let time = keyListOfJson(data, "time");
        let timeScale = new Scale([-bar_left_margin, length + bar_right_margin], [this.margin.left, this.width - this.margin.right], "bartime", time, this.timeframe);
        let height = this.height - this.margin.bottom - this.margin.top;
        let y = this.margin.top;
        let scales = [];
        let padding = 50;
        for (let i = 0; i < this.graphHeights.length; i++) {
            let rate = this.graphHeights[i];
            let h = rate * height;
            if (i == 0) {
                let scale = new Scale(minmax, [y + h, y]);
                scales.push(scale);
            } else {
                let scale = new Scale([0, 1], [y + h, y + padding]);
                scales.push(scale);
            }
            y += h;
        }
        let graph = new Graph(this.context, timeScale, scales);
        return graph;
    }

    render() {
        if (!this.tohlc) {
            return;
        }
        let end = this.tohlc.length - 1;
        let begin = end - this.showLength + 1;
        let data = slice(this.tohlc, begin, end);
        if (!data) {
            return;
        }
        //this.currentIndex = this.showLength - data.length;
        this.graph = this.createGraph(data, minmax(data, 100));
        this.context.clearRect(0, 0, this.width, this.height);
        let candles = []
        let prop = {"color": "green", "opacity": 0.5};
        
        for (var i = 0; i < data.length; i++){
            let value = data[i];
            if (value) {
                let candle = new Candle(i, value.time, value.open, value.high, value.low, value.close, this.showLength, prop);
                candles.push(candle);
                this.graph.draw(0, candle);
            }
        }
        //let time = keyListOfJson(data, "time");
        this.candles = candles;
        this.drawTitle(this.name + ' [' + this.timeframe + ']', {});
        //this.drawXtitle("Time", {});

        this.graph.drawAxis();
        
        if (candles.length > 0) {
            this.graph.drawCursor(0, candles[candles.length - 1]);
        }
        if (this.crossPoint) {
            let index = this.graph.isInner(this.crossPoint);
            if (index == 0) {
                this.graph.drawCross(0, this.crossPoint, candles);
            }
        }

        this.drawMA(20);
        this.drawRSI(14);
    }

    drawPoints(points, prop) {
        let width = 10;
        let height = 10;
        for(let p of points) {
            let point = new Square(this.context, this.xScale, this.yScale);
            point.draw(p[0], p[1], width, height, prop);
        }
    }

    drawTitle(title, prop) {
        this.context.font = "20px Arial";
        this.context.textAlign = "left";
        this.context.textBaseline = "top";
        this.context.fillStyle = "#444444";
        this.context.fillRect(this.margin.left, this.margin.top, 160, 30);
        this.context.fillStyle = "#ffffff";
        this.context.fillText(title, this.margin.left + 5, this.margin.top + 5);
        this.context.globalAlpha = 1.0;
        
    }

    drawXtitle(title, prop) {
        this.context.textAlign = "center";
        this.context.textBaseline = "top";
        this.context.globalAlpha = 1.0;
        this.context.fillText(title, this.canvas.width / 2, this.height - 50);
    }

    eventControl(){
        this.canvas.onmousemove = e => {
            let rect = this.canvas.getBoundingClientRect();
            let point = [e.clientX - rect.left, e.clientY - rect.top];
            this.updateCurorPoint(point);
        };
    }

    updateCurorPoint(point) {
        this.crossPoint = point;
        for (let i = 0; i < this.graph.scales.length; i++) {
            let index = this.graph.isInner(point);
            if (index == 0) {
                this.crossPoint = point;
                break;
            }
        } 
    }

    drawMA(windowWidth) {
        var close = []
        for (let v of this.tohlc) {
            close.push(v.close);
        }
        let ma0 = MA(close, windowWidth);
        let end = this.tohlc.length - 1;
        let begin = end - this.showLength + 1;
        let ma = slice(ma0, begin, end);

        var points = [];
        for (let i = 0; i < ma.length; i++) {
            let value = ma[i];
            if (value) {
                points.push([i, value]);
            }
        }

        let lines = new PolyLine(points, {opacity: 0.5, lineColor: "red", lineWidth: 2.0});
        this.graph.draw(0, lines);
    }

    drawRSI(windowWidth) {
        var close = []
        for (let v of this.tohlc) {
            close.push(v.close);
        }
        let rsi0 = RSI(close, windowWidth);
        let end = this.tohlc.length - 1;
        let begin = end - this.showLength + 1;
        let rsi = slice(rsi0, begin, end);
        var points = [];
        for (let i = 0; i < rsi.length; i++) {
            let value = rsi[i];
            if (value) {
                points.push([i, value]);
            }
        }
        let lines = new PolyLine(points, {opacity: 0.5, lineColor: "blue", lineWidth: 2.0});
        let domain = minmaxOfArray(rsi);
        this.graph.updateScaleDomain(1, domain);
        this.graph.draw(1, lines);
    }
}

// -----

function keyListOfJson(jsonArray, key){
    var dates = []
    for (var i = 0; i < jsonArray.length; i++) {
        let v = jsonArray[i];
        if (v) {
            var d = jsonArray[i][key]
            dates.push(d);
        } else {
            dates.push(null);
        }
    }
    return dates;
}

function minmaxDate(d) {
    var mindate, maxdate;
    for (var i = 0; i < d.length; i++){
        if (i == 0) {
            mindate = d[0];
            maxdate = d[0];
        } else {
            if (d[i] > maxdate) {
                maxdate = d[i]
            }
            if (d[i] < mindate) {
                mindate = d[i]
            }
        }
    }
    return [mindate, maxdate];
}

function minmax(jsonArray, margin) {
    let lows = keyListOfJson(jsonArray, "low");
    let min = Math.min.apply(null, lows);
    min -= margin;
    let highs = keyListOfJson(jsonArray, "high");
    let max = Math.max.apply(null, highs);
    max += margin;
    return [min, max];
}

function slice(data, begin, last) {
    if (last < 0) {
        last = data.length + last;
    }
    d = []
    for (var i = begin; i <= last; i++) {
        if (i >= 0) {
            d.push(data[i]);
        } else {
            d.push(null);
        }
    }
    return d;
}

// -----

function httpValues(ids) {
    var out = [];
    for (let e of ids) {
        let v = document.getElementById(e).value;
        out.push(parseInt(v));
    }
    return out;
}

var chart1 = null;
var shouldLoop = true;
function load(json) {
    let size = {size: {width: 1200, height: 600}, margin: {top:50, bottom: 100, left: 60, right: 60}, heights:[0.8, 0.4]};
    if (!chart1) {
        chart1 = new Chart(document.getElementById("canvas1"), size);
    }
    let [name, timeframe, length, tohlc] = parse(json);
    chart1.setBarNumber(100);
    chart1.load(name, tohlc, timeframe);
    if (shouldLoop) {
        setTimeout(function(){begin();}, 50);
    }
}


function updateBarNumber() {
    let [barNumber, priceRange] = httpValues(["barnumber", "pricerange"]);
    chart1.setBarNumber(barNumber);
    chart2.setBarNumber(barNumber);

}

function begin() {
    let [market, timeframe] = httpValues(["market", "timeframe"]); 
    market = 'US30Cash';
    timeframe = 'M5';
    post('/xmdata', {"market": market, "timeframe": timeframe});
}

function pause() {
    shouldLoop = false;
}

function post(action, data) {
    var form = document.createElement("form");
    form.setAttribute("action", action);
    form.setAttribute("method", "post");
    form.style.display = "none";
    document.body.appendChild(form);
    if (data !== undefined) {
        for (var paramName in data) {
            var input = document.createElement('input');
            input.setAttribute('type', 'hidden');
            input.setAttribute('name', paramName);
            input.setAttribute('value', data[paramName]);
            form.appendChild(input);
        }
    }
    form.submit();
   }