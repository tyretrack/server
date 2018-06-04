document.addEventListener("DOMContentLoaded", function () {

    var ws;

    var data = {};

    var out = document.getElementById('output');

    var place = document.getElementById('place');
    var lap = document.getElementById('lap');

    var rpm = document.getElementsByClassName('sRpm');
    var rpmPercent = document.getElementsByClassName('rpmPercent');

    var fuel = document.getElementById('fuel');
    var fuelLevel = document.getElementById('sFuelLevel');
    var speed = document.getElementById('sSpeed');

    var abs = document.getElementById('sABS');
    var tractionControl = document.getElementById('sTractionControl');
    var stability = document.getElementById('sStability');

    var numParticipants = document.getElementById('sNumParticipants');
    var sEventTimeRemaining = document.getElementById('sEventTimeRemaining');
    var sCurrentTime = document.getElementById('sCurrentTime');
    var sSplitTimeAhead = document.getElementById('sSplitTimeAhead');
    var sSplitTimeBehind = document.getElementById('sSplitTimeBehind');
    var sGear = document.getElementById('sGear');
    var fuelPercent = document.getElementById('fuelPercent');
    var fuelLitres = document.getElementById('fuelLitres');

    var sAmbientTemperature = document.getElementById('sAmbientTemperature');
    var sCurrentLapDistance = document.getElementById('sCurrentLapDistance');
    var sectorName = document.getElementById('sectorName');

    var map = document.getElementById('map');

    var sTyreTemp = document.getElementsByClassName('sTyreTemp');
    // x: -1700 - 4364
    // 1800 - 4400
    // y: 0 - 5372
    // 0 - 5400
    var maxX = 1800, maxY = 0, minX = -1700, minY = 5400;

    var mapWidth = map.width;
    var mapHeight = map.height;

    var xModulator = ((maxX - minX) + mapWidth / 2);
    var yModulator = ((maxY - minY) + mapHeight / 2);

    var currRpmColor = "progress-success";
    var currFuelColor = "progress-success";

    var tyreGripProbes = [];

    var dists = [
        0,
        1560,
        1900,
        2110,
        3280,
        3650,
        3940,
        4880,
        5450,
        6240,
        7100,
        7550,
        8340,
        9460,
        10570,
        11700,
        12330,
        13100,
        13540,
        13800,
        14010,
        14750,
        15420,
        16450,
        17010,
        17520,
        19140,
        19900,
        20250
    ];

    var names = ["Hatzenbach",
        "Hoheneichen",
        "Quidellbacher Höhe",
        "Flugplatz",
        "Schwedenkreuz",
        "Aremberg",
        "Fuchsröhre",
        "Adenauer Forst",
        "Metzgesfeld",
        "Kallenhard",
        "Wehrseifen",
        "ExMühle",
        "Bergwerk",
        "Kesselchen",
        "Klostertal",
        "Karussel",
        "Hohe Acht",
        "Hedwigshöhe",
        "Wipperman",
        "Eschbach",
        "Brünnchen",
        "Pflanzgarten",
        "Plfanzgarten II",
        "Schwalbenschwanz",
        "Galgenkopf",
        "Döttinger Höhe",
        "Antoniusbuche",
        "Tiergarten",
        "Hohenrain"];

    function findName(dist) {
        var i;
        for (i = 0; i < dists.length && dists[i] < dist; i++) {
        }

        return names[--i];
    }

    function prettyPrintSeconds(seconds, subseconds) {
        var hours = Math.floor(seconds / 3600);
        seconds %= 3600;
        var minutes = Math.floor(seconds / 60);
        seconds %= 60;
        if (subseconds !== "undefined")
            seconds = seconds.toFixed(subseconds);
        if (hours > 0)
            return hours + ":" + minutes + ":" + seconds;
        else if (minutes > 0)
            return minutes + ":" + seconds;
        else
            return "" + seconds;
    }

    function drawMap(c) {
        var ctx = map.getContext("2d", {alpha: true});

        ctx.clearRect(0, 0, mapWidth, mapHeight);

        ctx.strokeStyle = "black";
        ctx.fillStyle = "black";
        ctx.textAlign = "center";
        ctx.textBaseline = 'middle';
        ctx.font = "12px sans";

        function draw(info, idx) {
            var pos = info.sWorldPosition;

            // x: -1700 - 4364
            // 1800 - 4400
            // y: 0 - 5372
            // 0 - 5400

            var x = (pos[0] + 1900) / 10.0;
            var y = (pos[2] - 5500) / -10.0;

            x *= 0.6025;
            y *= 0.61;

            x += 46;
            y += 58;

            ctx.fillStyle = "white";
            ctx.beginPath();
            ctx.arc(x, y, 10, 0, 2 * Math.PI);
            ctx.fill();

            ctx.fillStyle = "black";

            ctx.beginPath();
            ctx.arc(x, y, 10, 0, 2 * Math.PI);
            ctx.stroke();

            ctx.fillText(idx, x, y);
        }

        for (var i = 0; i < c.sParticipationInfo.length; i++) {
            draw(c.sParticipationInfo[i], i);
        }

        ctx.fillStyle = "red";
        ctx.strokeStyle = "red";
        draw(c.sParticipationInfo[0], 0);
    }

    function funcUpdate() {
        var i;
        var c = data;

        //place.textContent = c.sParticipationInfo[0].sRacePosition;
        //lap[0].textContent = c.sParticipationInfo[0].sCurrentLap;

        for (i = 0; i < rpm.length; i++) {
            rpm[i].textContent = c.sRpm;
        }
        /*var rpmPercentValue = ((c.sRpm / c.sMaxRpm) * 100);
         rpmPercent.width(rpmPercentValue + "%");

         var newRpmColor = "progress-bar-success";
         if (rpmPercentValue > 90) {
         newRpmColor = "progress-bar-danger";
         } else if (rpmPercentValue > 70) {
         newRpmColor = "progress-bar-warning";
         }*/

        /*if (newRpmColor != currRpmColor) {
         rpmPercent.removeClass("progress-bar-success");
         rpmPercent.removeClass("progress-bar-warning");
         rpmPercent.removeClass("progress-bar-danger");
         rpmPercent.addClass(newRpmColor);
         }*/

        var fuel = Math.round(c.sFuelCapacity * c.sFuelLevel);
        fuelLevel.textContent = fuel + "%";

        var newFuelColor = "progress-bar-success";
        if (fuel < 10) {
            newFuelColor = "progress-bar-danger";
        }

        /*if (newFuelColor != currFuelColor) {
         fuelPercent.removeClass("progress-bar-success");
         fuelPercent.removeClass("progress-bar-warning");
         fuelPercent.removeClass("progress-bar-danger");
         fuelPercent.addClass(newFuelColor);
         }*/

        fuelLitres.textContent = (c.sFuelCapacity * c.sFuelLevel).toFixed(1) + " l";
        speed.textContent = Math.round((c.sSpeed * 60 * 60) / 1000);
        numParticipants.textContent = c.sNumParticipants;

        sEventTimeRemaining.textContent = prettyPrintSeconds(c.sEventTimeRemaining);
        sCurrentTime.textContent = prettyPrintSeconds(c.sCurrentTime, 1 );
        sSplitTimeAhead.textContent = prettyPrintSeconds(c.sSplitTimeAhead, 1);
        sSplitTimeBehind.textContent = prettyPrintSeconds(c.sSplitTimeBehind, 1);
        sGear.textContent = c.sGear;
        sAmbientTemperature.textContent = c.sAmbientTemperature + " °C";
        //sCurrentLapDistance.textContent = (c.sParticipationInfo[0]['sCurrentLapDistance'] / 1000).toFixed(2) + " km";
        //sectorName.textContent = findName(c.sParticipationInfo[0]['sCurrentLapDistance']);

        // process data for the tyres
        for (var idx = 0; idx < 4; idx++) {

            if (typeof tyreGripProbes[idx] === 'undefined') {
                tyreGripProbes[idx] = [];
            }

            if (tyreGripProbes[idx].length >= 200) {
                tyreGripProbes.pop();
            }

            //tyreGripProbes[idx].shift(c.sTyreGrip[idx]);

            var tyreGripAvg = 0;
            var tyreGripSum = 0;
            for (i = 0; i < tyreGripProbes.length; i++) {
                tyreGripSum += tyreGripProbes[i];
            }
            tyreGripAvg = tyreGripSum / tyreGripProbes[idx].length;

            sTyreTemp[idx].textContent = c['sTyreTemp'][idx];
            sTyreTemp[idx].style.backgroundSize = "100% " + (c['sTyreWear'][idx] / 255 * 100).toFixed() + "%";
            //jQuery('#sTyreGrip' + idx).html(tyreGripAvg);
        }

        //drawMap(c);
    }


    var lastUpdate = undefined;
    var logged = false;

    function funcConnect() {
        ws = new WebSocket("ws://" + window.location.hostname + ':' + window.location.port + "/stream");

        ws.onmessage = function (ev) {
            var parsed = JSON.parse(ev.data);
            var c = parsed['c'];
            for (var key in c) {
                if (c.hasOwnProperty(key)) {
                    data[key] = c[key];
                }
            }

            if (!logged) {
                console.log(c);
                logged = true;
            }

            window.cancelAnimationFrame(lastUpdate);
            lastUpdate = window.requestAnimationFrame(funcUpdate);
        };

        ws.onclose = function () {
            console.log("disconnected");
        };

        ws.onopen = function (event) {
            console.log("connected");
            var msg = {
                type: "subscribe",
                data: ["sRpm",
                    "sSpeed",
                    "sGear",
                    "sFuelLevel",
                    "sParticipationInfo",
                    "sTyreGrip",
                    "sTyreTemp",
                    "sTyreWear",
                    "sEventTimeRemaining",
                    "sNumParticipants",
                    "sCurrentTime",
                    "sSplitTimeAhead",
                    "sSplitTimeBehind",
                    "sAmbientTemperature",
                ]
            };
            ws.send(JSON.stringify(msg));
        };
    }

    document.addEventListener("visibilitychange", function (ev) {
        if (document['hidden']) {
            ws.close();
            document.title = "24h-of-pankow (paused)"
        } else {
            funcConnect();
            document.title = "24h-of-pankow"
        }
    });

    funcConnect();
});