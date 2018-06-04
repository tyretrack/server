jQuery(document).ready(function () {


    var ws = new WebSocket("ws://"+window.location.hostname+":8765/");
    var out = jQuery('#output');

    var place = jQuery('#place');
    var lap = jQuery('#lap');

    var rpm = jQuery('#sRpm');

    var fuel = jQuery('#fuel');
    var fuelLevel = jQuery('#sFuelLevel');
    var speed = jQuery('#sSpeed');
	
	var numParticipants = jQuery('#sNumParticipants');
	var sEventTimeRemaining = jQuery('#sEventTimeRemaining');
	var sCurrentTime = jQuery('#sCurrentTime');
	var sSplitTimeAhead = jQuery('#sSplitTimeAhead');
	var sSplitTimeBehind = jQuery('#sSplitTimeBehind');
    var sGear = jQuery('#sGear');
    var fuelPercent = jQuery('#fuelPercent');
	var fuelLitres = jQuery('#fuelLitres')
	var rpmPercent = jQuery('#rpmPercent');

    var map = jQuery('#map');
    // x: -1700 - 4364
    // 1800 - 4400
    // y: 0 - 5372
    // 0 - 5400
    var maxX = 1800, maxY = 0, minX = -1700, minY = 5400;

    var mapWidth = map[0].width;
    var mapHeight = map[0].height;

    var xModulator = ((maxX - minX) + mapWidth / 2);
    var yModulator = ((maxY - minY) + mapHeight / 2);

    var reqLog = 0;
    var currRpmColor = "progress-success";
    var currFuelColor = "progress-success";

    var tyreGripProbes = [];

    var logged = false;
    ws.onopen = function (event) {
        out.text("connected");
    };
    ws.onmessage = function (ev) {

        reqLog++;
        if (reqLog % 10 != 0) { // ony process every 10th update
            return;
        }

        var parsed = JSON.parse(ev.data);
        var c = parsed.c;
        var m = parsed.m;

        if (!logged) {
            console.log(c);
            logged = true;
        }

        place.html(c.sParticipationInfo[0].sRacePosition);
        lap.html(c.sParticipationInfo[0].sCurrentLap);

        rpm.html(c.sRpm);
        var rpmPercentValue = ((c.sRpm / c.sMaxRpm) * 100);
		rpmPercent.width(rpmPercentValue + "%");

        var newRpmColor = "progress-bar-success";
        if (rpmPercentValue > 90) {
            newRpmColor = "progress-bar-danger";
        } else if (rpmPercentValue > 70) {
            newRpmColor = "progress-bar-warning";
        }

        if (newRpmColor != currRpmColor) {
            rpmPercent.removeClass("progress-bar-success");
            rpmPercent.removeClass("progress-bar-warning");
            rpmPercent.removeClass("progress-bar-danger");
            rpmPercent.addClass(newRpmColor);
        }

        var fuel = Math.round(c.sFuelLevel * 100);
        fuelLevel.html(fuel  + "%");

        var newFuelColor = "progress-bar-success";
        if (fuel < 10) {
            newFuelColor = "progress-bar-danger";
        }

        if (newFuelColor != currFuelColor) {
            fuelPercent.removeClass("progress-bar-success");
            fuelPercent.removeClass("progress-bar-warning");
            fuelPercent.removeClass("progress-bar-danger");
            fuelPercent.addClass(newFuelColor);
        }

        fuelPercent.width(fuel + "%");
        fuelLitres.html(Math.round((fuel / c.sFuelCapacity) * 100));
        speed.html(Math.round((c.sSpeed * 60 * 60) / 1000));
		numParticipants.html(c.sNumParticipants);
		
		sEventTimeRemaining.html(Math.round(c.sEventTimeRemaining / 60));
		sCurrentTime.html(Math.round(c.sCurrentTime));
		sSplitTimeAhead.html(Math.round(c.sSplitTimeAhead));
	    sSplitTimeBehind.html(Math.round(c.sSplitTimeBehind));
		sGear.html(c.sGear);

        // process data for the tyres
        for (var idx = 0; idx <= 4; idx++) {

            if (typeof tyreGripProbes[idx] === 'undefined') {
                tyreGripProbes[idx] = [];
            }

            if (tyreGripProbes[idx].length >= 200) {
                tyreGripProbes.pop();
            }

            tyreGripProbes[idx].shift(c.sTyreGrip[idx]);

            var tyreGripAvg = 0;
            var tyreGripSum = 0;
            for (var i in tyreGripProbes) {
                tyreGripSum += tyreGripProbes[i];
            }
            tyreGripAvg = tyreGripSum / tyreGripProbes[idx].length;

            jQuery('#sTyreTemp' + idx).html(c.sTyreTemp[idx]);
            jQuery('#sTyreWear' + idx).html(c.sTyreWear[idx]);
            jQuery('#sTyreGrip' + idx).html(tyreGripAvg);
        }

        // MAP

        var ctx = map[0].getContext("2d", {alpha: false});

        ctx.fillStyle = "black";
        ctx.fillRect(0, 0, width, height);

        ctx.strokeStyle = "white";
        ctx.fillStyle = "white";
        ctx.textAlign = "center";
        ctx.textBaseline = 'middle';
        ctx.font="14px sans";

        function draw(info, idx) {
            var pos = info.sWorldPosition;

            var x = (pos[0] + xModulator);
            var y = (pos[2] + yModulator);

            ctx.beginPath();
            ctx.arc(x, y, 12, 0, 2 * Math.PI);
            ctx.stroke();

            ctx.fillText(idx, x, y);
        }

        for (var i = 0; i < c.sParticipationInfo.length; i++) {
            draw(c.sParticipationInfo[i], i);
        }

        ctx.fillStyle = "red";
        ctx.strokeStyle = "red";
        draw(c.sParticipationInfo[0], 0);

    };

    var ctx = map[0].getContext("2d", {alpha: false});
    var width = map[0].width;
    var height = map[0].height;
    ctx.fillStyle = "black";
    ctx.fillRect(0, 0, width, height);
});