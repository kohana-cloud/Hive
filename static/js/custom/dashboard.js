// Data and template declerations
var honeypotData = null;

sortSetting = "health";


// Define base card templates
function cardRenderTemplate(id) {
    return `<card id="card-${id}" class="card" onclick="cardExistingClicked(this)" style="padding: 0; margin: 20px; width: 200px;"></card>`
}

// Build header
function cardRenderHeader(id, attributes) {
    switch (attributes.health) {
        case 0:
            var headerTitle = "Healthy";
            var headerBackgroundColor = "rgb(0,200,0)";
            var headerTextColor = "rgb(255,255,255)";
            break;
        case 1:
            var headerTitle = "Degraded";
            var headerBackgroundColor = "rgb(237,130,14)";
            var headerTextColor = "rgb(255,255,255)";
            break;
        case 2:
            var headerTitle = "Compromised";
            var headerBackgroundColor = "rgb(200,0,0)";
            var headerTextColor = "rgb(255,255,255)";
            break;
        case 3:
            var headerTitle = "Live Attacker";
            var headerBackgroundColor = "rgb(200,0,0)";
            var headerTextColor = "rgb(255,255,255)";
            break;
    }
    return `<div id="card-header-${id}" class="card-header" style="background-color: ${headerBackgroundColor}; color: ${headerTextColor}; text-align: center;">
    ${headerTitle}
    </div>`
}

// Define card body
function cardRenderBody(id, attributes) {
    switch (attributes.health) {
        case 0: var bodyBackgroundColor = null; break;
        case 1: var bodyBackgroundColor = null; break;
        case 2: var bodyBackgroundColor = "rgb(255,220,220)"; break;
        case 3: var bodyBackgroundColor = "rgb(255,220,220)"; break;
    }

    switch (attributes.type) {
        case "EC2":
            var cardGraphic = "ec2_grey.svg";
            var cardTitle = "EC2 Compute";
            break;
        case "BOTTLEROCKET":
            var cardGraphic = "bottlerocket_grey.svg";
            var cardTitle = "Bottlerocket";
            break;
        case "ECS":
            var cardGraphic = "ecs_grey.svg";
            var cardTitle = "ECS Container";
            break;
        case "FROST":
            var cardGraphic = "thinkbox_frost_grey.svg";
            var cardTitle = "TB Frost";
            break;
        case "LAMBDA":
            var cardGraphic = "lambda_grey.svg";
            var cardTitle = "Lambda";
            break;
        case "S3":
            var cardGraphic = "s3_grey.svg";
            var cardTitle = "S3 Bucket";
            break;
        case "OUTPOST":
            var cardGraphic = "outpost_grey.svg";
            var cardTitle = "Outpost";
            break;
        case "PARALLEL":
            var cardGraphic = "parallel_grey.svg";
            var cardTitle = "Parallel";
            break;
        case "SERVERLESS":
            var cardGraphic = "serverless_grey.svg";
            var cardTitle = "Serverless";
            break;
    }

    // Set tile configurations based on health and stateful/stateless
    if (attributes.health == 0) {
        var buttonImageDisabled = "disabled";
        var buttonResetDisabled = "disabled";
    }
    
    return `
    <div id="card-body-${id}" class="card-body" style="background-color:${bodyBackgroundColor}">
        <img src="static/graphics/endpoint-images/${cardGraphic}" height=75 style="display: block; margin:auto; border-radius:15px;">
        <h5 class="card-title" style=" text-align: center; margin-top: 10px;">${cardTitle}</h5>
        <h6 class="card-subtitle mb-2 text-muted" style="text-align: center;">${id.split('-')[0]}</h6>

        <table class="table" style="font-size: 10px;">
            <thead class="thead-dark">
                <tr>
                    <th scope="col" style="text-align:left">Target</th>
                    <th scope="col" style="text-align:right;">Assignment</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <th scope="row">eno0</th>
                    <td scope="row">
                        <div style="text-align:right;">192.168.0.1/24</div>
                        <div style="text-align:right;">192.168.1.1/24</div>
                    </td>
                </tr>
                <tr>
                    <th scope="row">tun33</th>
                    <td style="text-align:right;">192.168.1.1/24</td>
                </tr>
            </tbody>
        </table>

        <p style="font-size:12px; text-align: center;"><b>HP Owner:</b> Nate Singer</p>
        <p style="font-size:7px; text-align:center; margin-top: -10px;"><i>c6f72742-f765-11ec-8c7a-75e0b7943059</i></p>

        <form class="form-grid" style="margin:auto; display:block; margin-top: 10px;">
            <div class="row" style="margin-bottom: 5px;">
                <button type="button" ${buttonResetDisabled} id="buttonUUID" class="btn btn-dark btn-sm" style="margin:auto; width: 90%;">Image</button>
            </div>
            <div class="row" style="margin-top: 0px;">
                <button type="button" ${buttonImageDisabled} id="buttonUUID" class="btn btn-danger btn-sm" style="margin:auto; width: 90%;">Reset</button>
            </div>
        </form>
    </div>`
}

// Build card footer
function cardRenderFooter(id, attributes) {
    switch (attributes.health) {
        case 0: var footerBackgroundColor = "rgb(240,240,240)"; break;
        case 1: var footerBackgroundColor = "rgb(240,240,240)"; break;
        case 2: var footerBackgroundColor = "rgb(250,180,180)"; break;
        case 3: var footerBackgroundColor = "rgb(250,180,180)"; break;
    }

    return `<div id="card-footer-${id}" class="card-footer text-muted" style="text-align: center; color: rgb(108, 117, 125); background-color: ${footerBackgroundColor};">loading</div>`;
}

// Build new card
function cardRenderNew() {
    return `
    <card id="card-new" class="card card-new" onclick="cardNewClicked()" style="min-height: 425px; padding: 0; margin: 20px; width: 200px;">
        <img id="card-new-img" src="static/graphics/endpoint-images/plus-dotted.svg" height=100 class="width: max-content; card-img-top" style="position: absolute; top: 50%; -ms-transform: translateY(-50%);transform: translateY(-50%);"/>
    </card>`
}

// Generate HTML from JSON and render
async function createAllCards() {
    let honeypot_cards = "";

    // Create items array and sort high to low
    var sortedHoneypots = Object.keys(honeypotData).map(function(key) { return [key, honeypotData[key]["health"]] });
    sortedHoneypots.sort(function(first, second) { return second[1] - first[1] });

    // Render the card shells and manual add
    $.each(sortedHoneypots, function (index) {
        hpId = sortedHoneypots[index][0];
        honeypot_cards += cardRenderTemplate(hpId);
    });
    honeypot_cards += cardRenderNew()

    // Create the rendered card shells
    document.getElementById("card-container").innerHTML = honeypot_cards;
    
    // Render card contents, shells are sorted in the page already
    $.each(honeypotData, function (hpId, hpAttributes) {
        document.getElementById("card-" + hpId).innerHTML = cardRenderHeader(hpId, hpAttributes) 
                                                            + cardRenderBody(hpId, hpAttributes) 
                                                          + cardRenderFooter(hpId, hpAttributes);
    });
}

// Update footer timestamps every second
async function updateFooterTimeStamp() {
    if (document.getElementsByClassName("card")) {
        let dtNow = new Date().getTime();

        // Update Text
        $.each(honeypotData, function (hpId, hpAttributes) {
            // Convert last update timestamp of target
            let dtTarget = new Date(hpAttributes.updated*1000).getTime();
            let dtDelta = dtNow - dtTarget;
    
            let days = Math.floor(dtDelta / (1000 * 60 * 60 * 24));
            let hours = Math.floor((dtDelta % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            let minutes = Math.floor((dtDelta % (1000 * 60 * 60)) / (1000 * 60));
            let seconds = Math.floor((dtDelta % (1000 * 60)) / 1000);
    
            let finalText = "";
            if (days == 1) {
                finalText = `1 day ago`
            } else if (days !== 0) {
                finalText = `${days} days ago`
            } else if (hours == 1) {
                finalText = `1 hour ago`
            } else if (hours !== 0) {
                finalText = `${hours} hours ago`
            } else if (minutes == 1) {
                finalText = `1 minute ago`
            } else if (minutes !== 0) {
                finalText = `${minutes} minutes ago`
            } else if (seconds == 1) {
                finalText = `1 second ago`
            } else {
                finalText = `${seconds} seconds ago`
            }
    
            // Render card HTML
            if (document.getElementById(`card-footer-${hpId}`)) {
                document.getElementById(`card-footer-${hpId}`).textContent = finalText;
            }
        });
    }
} var run = setInterval(updateFooterTimeStamp, 1000);


// Render all cards once page has loaded
$(document).ready(function() {
    // Get JSON from server
    $.getJSON("api/v1/honeypots", function(data) { honeypotData = data })

    // Build the HTML objects
    .done(function() { createAllCards() });
});

// Flash page title if any HP has been compromised
var pageFlashState = false;
function flashTitle () {
    var pageFlash = false;

    // Check if any honeypots are compromised
    $.each(honeypotData, function (id, attributes) {
        if (attributes.health == 3 || attributes.health == 2) { pageFlash = true }
    });

    // If there is a compromised hp alter the flash state, else default
    if (pageFlash && !pageFlashState) { 
        document.title = "The Hive 🔴";
        pageFlashState = true;
    } else {
        document.title = "The Hive"
        pageFlashState = false;
    }
} var run = setInterval(flashTitle, 500);


// Flash HP border and shadow if it has been compromised
var flashOn = false;
function flashLive() {
    var d = new Date()
    $.each(honeypotData, function (id, attributes) {
        if (attributes.health == 3) {
            if (!flashOn) {
                document.getElementById("card-" + id).style.border = "1px solid rgba(0, 0, 0, 0.125)";
                document.getElementById("card-" + id).style["boxShadow"] = null
            } else {
                document.getElementById("card-" + id).style.border = "1px solid red";
                document.getElementById("card-" + id).style["boxShadow"] = "0 0 5px red";
            }
        }
    });

    // Flip flash state
    if (flashOn) { flashOn = false } else { flashOn = true }
} var run = setInterval(flashLive, 250);


function cardExistingClicked(card) {
    hpid = card.id.substring(5)

    /*$.getJSON("api/v1/details/" + hpid, function(response) { 
        currentHpData = response
    })*/

    // Set controls based on health
    document.getElementById("observerTitle").innerHTML = hpid;
    hpHealth = honeypotData[hpid].health

    if (hpHealth == 0) {
        // Healthy
        document.getElementById("hpStatusToggle").classList.add('hp-control-stop');
        document.getElementById("hpStatusToggle").classList.remove('hp-control-start');
        document.getElementById("hpStatusToggle").innerText = "Stop";
    } else if (hpHealth == 1) {
        // Degraded
        document.getElementById("hpStatusToggle").classList.add('hp-control-start');
        document.getElementById("hpStatusToggle").classList.remove('hp-control-stop');
        document.getElementById("hpStatusToggle").innerText = "Start";
    }
    
    // Display card
    $("#observeHoneypot").modal('show');
}


function cardNewClicked() {
    $("#createHoneypot").modal('show');
}


// Define delay function
function delay(time) { return new Promise(resolve => setTimeout(resolve, time)) }


// Create a new honeypot
function newHP(hptype) {
    $.post('/api/v1/honeypot/create', { type: hptype }, function(data) {
        $("#createHoneypot").modal('hide');
        createAllCards();
    })
}


// Delete a honeypot
function deleteHP(card) {
    $.post('/api/v1/honeypot/delete', { hpid: document.getElementById("observerTitle").innerHTML }, function(data) {
        $("#observeHoneypot").modal('hide');
    })
}

// Reset a honeypot
function resetHP(card) {
    $.post('/api/v1/honeypot/reset', { hpid: document.getElementById("observerTitle").innerHTML }, function(data) {
        $("#observeHoneypot").modal('hide');
    })
}

// Stop Attack, Triage
function stopAttack(card) {
    $.post('/api/v1/honeypot/stopattack', { hpid: document.getElementById("observerTitle").innerHTML }, function(data) {
        $("#observeHoneypot").modal('hide');
    })
}


// Start a honeypot
function toggleHP(card) {
    // Set controls based on health
    document.getElementById("observerTitle").innerHTML = hpid;
    hpHealth = honeypotData[hpid].health

    if (hpHealth == 0) {
        // Healthy - stophp
        $.post('/api/v1/honeypot/stop', { hpid: document.getElementById("observerTitle").innerHTML }, function(data) {
            $("#observeHoneypot").modal('hide');
        })
    } else if (hpHealth == 1) {
        $.post('/api/v1/honeypot/start', { hpid: document.getElementById("observerTitle").innerHTML }, function(data) {
            console.log('start')
            $("#observeHoneypot").modal('hide');
            console.log('stop')
        })
    }    
}

// Stop a honeypot
function stopHP(card) {
    
}


async function updateAllCards() {
    let honeypot_cards = "";

    // Get JSON from server
    $.getJSON("api/v1/honeypots", function(data) { honeypotData = data })

    // Create items array and sort high to low
    if (sortSetting == "health") {
        var sortedHoneypots = Object.keys(honeypotData).map(function(key) { return [key, honeypotData[key]["health"]] });
    } else if (sortSetting == "type") {
        var sortedHoneypots = Object.keys(honeypotData).map(function(key) { return [key, honeypotData[key]["type"]] });
    } else if (sortSetting == "component") {
        //unimplemented
        var sortedHoneypots = Object.keys(honeypotData).map(function(key) { return [key, honeypotData[key]["health"]] });
    } else if (sortSetting == "timestamp") {
        var sortedHoneypots = Object.keys(honeypotData).map(function(key) { return [key, honeypotData[key]["updated"]] });
    } else if (sortSetting == "hpid") {
        var sortedHoneypots = Object.keys(honeypotData).map(function(key) { return [key, honeypotData[key]] });
    } else if (sortSetting == "cid") {
        var sortedHoneypots = Object.keys(honeypotData).map(function(key) { return [key, honeypotData[key]["owner"]] });
    } else {
        console.log("[!] WARNING: Unknown sort type used")
        var sortedHoneypots = Object.keys(honeypotData).map(function(key) { return [key, honeypotData[key]["health"]] });
    }
    
    // Swap the last two values here to sort high low or low high
    sortedHoneypots.sort(function(first, second) { return second[1]  - first[1]});

    
    
    // Render the card shells and manual add
    $.each(sortedHoneypots, function (index) {
        hpId = sortedHoneypots[index][0];
        honeypot_cards += cardRenderTemplate(hpId);
    });
    honeypot_cards += cardRenderNew()

    // Create the rendered card shells
    document.getElementById("card-container").innerHTML = honeypot_cards;

    
    
    // Render card contents, shells are sorted in the page already
    $.each(honeypotData, function (hpId, hpAttributes) {
        document.getElementById("card-" + hpId).innerHTML = cardRenderHeader(hpId, hpAttributes) 
                                                            + cardRenderBody(hpId, hpAttributes) 
                                                          + cardRenderFooter(hpId, hpAttributes);
    });

    // Update the timestamp
    updateFooterTimeStamp();
} var run = setInterval(updateAllCards, 1000);


async function updateSorting(newSortSetting) {
    document.getElementById("targetHealth").checked = false;
    document.getElementById("targetType").checked = false;
    document.getElementById("profileComponent").checked = false;
    document.getElementById("updateTimestamp").checked = false;
    document.getElementById("honeypotID").checked = false;
    document.getElementById("creatorID").checked = false;

    if (newSortSetting == "health") {
        document.getElementById("targetHealth").checked = true;
        sortSetting = "health";
    } else if (newSortSetting == "type") {
        document.getElementById("targetType").checked = true;
        sortSetting = "type";
    } else if (newSortSetting == "component") {
        document.getElementById("profileComponent").checked = true;
        sortSetting = "component";
    } else if (newSortSetting == "timestamp") {
        document.getElementById("updateTimestamp").checked = true;
        sortSetting = "timestamp";
    } else if (newSortSetting == "hpid") {
        document.getElementById("honeypotID").checked = true;
        sortSetting = "hpid";
    } else if (newSortSetting == "cid") {
        document.getElementById("creatorID").checked = true;
        sortSetting = "cid";
    }

    console.log(sortSetting);
    updateAllCards();
}