
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}


async function degradeS3() {
    document.getElementById("c1").classList.add("circle-degraded-immediate");
}


async function degradeEC2() {
    document.getElementById("l1").classList.add("line-degraded");
    document.getElementById("c2").classList.add("circle-degraded");
}

async function degradeEC2Immediate() {
    document.getElementById("l1").classList.add("line-degraded-immediate");
    document.getElementById("c2").classList.add("circle-degraded-immediate");
}


async function degradeECS() {
    document.getElementById("l2").classList.add("line-degraded");
    document.getElementById("c3").classList.add("circle-degraded");
}

async function degradeECSImmediate() {
    document.getElementById("l2").classList.add("line-degraded-immediate");
    document.getElementById("c3").classList.add("circle-degraded-immediate");
}


// Update status on page load
$(document).ready(function() {

    $.getJSON("api/v1/honeypots", function(honeypotData) {

        //Check S3 health
        if (honeypotData["92c75190-f3ff-11ec-a661-000c2970a8e4"].health > 1) { degradeS3(); }

        //Check EC2 health
        if (honeypotData["859a277c-f3ff-11ec-a661-000c2970a8e4"].health > 1) { degradeEC2Immediate(); }

        //Check ECS health
        if (honeypotData["b5dd020a-0652-11ed-8900-000c2970a8e4"].health > 1) { degradeECSImmediate(); }
    })

    

});

firstLoad = true;

// Update status in realtime
async function checkPlotStatus() {
    if (firstLoad) {
        sleep(1000);
        firstLoad = false;
    }
    

    $.getJSON("api/v1/honeypots", function(honeypotData) {

        //Check S3 health
        if (honeypotData["92c75190-f3ff-11ec-a661-000c2970a8e4"].health > 1) {
            // Ensure not already degraded
            if (!document.getElementById("c1").classList.contains("circle-degraded-immediate")) {
                degradeS3();
            }
        }

        //Check EC2 health
        if (honeypotData["859a277c-f3ff-11ec-a661-000c2970a8e4"].health > 1) {
            // Ensure not already degraded
            if (!document.getElementById("c2").classList.contains("circle-degraded")) {
                degradeEC2();
            }
        }

        //Check ECS health
        if (honeypotData["b5dd020a-0652-11ed-8900-000c2970a8e4"].health > 1) {
            // Ensure not already degraded
            if (!document.getElementById("c3").classList.contains("circle-degraded")) {
                degradeECS();
            }
        }
    })

    

} var run = setInterval(checkPlotStatus, 1000);