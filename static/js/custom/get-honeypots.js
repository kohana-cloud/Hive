// Data and template declerations
var jsonData = null;

function cardTemplate(id, attributes) {
    return `
    <div id="card-${id}" class="card" style="padding: 0; margin: 20px; width: 200px; background-color: rgb(252, 252, 252);"></div>`
}

function cardHeaderTemplate(id, attributes) {
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

    return `
    <div id="card-header-${id}" class="card-header" style="background-color: ${headerBackgroundColor}; color: ${headerTextColor}; text-align: center;">
        ${headerTitle}
    </div>`
}

function cardBodyTemplate(id, attributes) {
    switch (attributes.type) {
        case "VPS":
            var cardGraphic = "vps-fill.svg";
            var cardTitle = "VPS";
            break;
        case "Database":
            var cardGraphic = "db-fill.svg";
            var cardTitle = "DB";
            break;
        case "NAS":
            var cardGraphic = "nas-fill.svg";
            var cardTitle = "NAS";
            break;
    }

    if (attributes.health == 0) {
        var buttonImageDisabled = "disabled";
    }
    
    return `
    <div id="card-body-${id}" class="card-body">
        <img src="static/graphics/endpoint-images/${cardGraphic}" height=75 class="card-img-top">
        <h5 class="card-title" style=" text-align: center; margin-top: 10px;">${cardTitle}</h5>
        <h6 class="card-subtitle mb-2 text-muted" style="text-align: center;">${id}</h6>

        placeholder
        placeholder
        placeholder

        <form class="form-grid" style="margin:auto; display:block; margin-top: 30px;">
            <div class="row" style="margin-bottom: 5px;">
                <button type="button" id="buttonUUID" class="btn btn-dark btn-sm" style="margin:auto; width: 90%;">Image</button>
            </div>
            <div class="row" style="margin-top: 0px;">
                <button type="button"${buttonImageDisabled} id="buttonUUID" class="btn btn-danger btn-sm" style="margin:auto; width: 90%;">Reset</button>
            </div>
        </form>
    </div>`
}

function cardFooterTemplate(id, attributes) {
    switch (attributes.health) {
        case 0:
            var footerText = "loading"
            var footerTextColor = "#6c757d";
            var footerBackgroundColor = "rgba(0,0,0,.03)";
            break;
        case 1:
            var footerText = "loading"
            var footerTextColor = "#6c757d";
            var footerBackgroundColor = "rgba(0,0,0,.03)";
            break;
        case 2:
            var footerText = "loading"
            var footerTextColor = "#6c757d";
            var footerBackgroundColor = "rgba(0,0,0,.03)";
            break;
        case 3:
            var footerText = "loading"
            var footerTextColor = "#6c757d";
            var footerBackgroundColor = "rgba(0,0,0,.03)";
            break;
    }

    return `
    <div id="card-footer-${id}" class="card-footer text-muted" style="text-align: center; color: ${footerTextColor}; background-color: ${footerBackgroundColor};">
        ${footerText}
    </div>`;
}


// Generate HTML from JSON and render
function updateAllCards() {
    let honeypot_cards = "";

    // Derive the card shells
    $.each(jsonData, function (hpId, hpAttributes) {
        honeypot_cards += cardTemplate(hpId);
    });

    // Render the card shells
    document.getElementById("card-container").innerHTML = honeypot_cards;
    
    // Derive Card Attributes
    $.each(jsonData, function (hpId, hpAttributes) {
        let honeypot_card = "";

        // Derive card segments
        honeypot_card += cardHeaderTemplate(hpId, hpAttributes);
        honeypot_card += cardBodyTemplate(hpId, hpAttributes);
        honeypot_card += cardFooterTemplate(hpId, hpAttributes);

        // Render card HTML
        document.getElementById("card-" + hpId).innerHTML = honeypot_card;
        honeypot_cards += honeypot_card
    });

    // Update CSS to center cards
    let cardContainer = document.getElementById("card-container");
    cardContainer.style.justifyContent = "center";
}

// Generate HTML from JSON and render
function updateCardFooters() {
    var dtNow = new Date().getTime();

    // Update Text
    $.each(jsonData, function (hpId, hpAttributes) {
        // Convert last update timestamp of target
        var dtTarget = new Date(hpAttributes.updated*1000).getTime();
        var dtDelta = dtNow - dtTarget;

        var days = Math.floor(dtDelta / (1000 * 60 * 60 * 24));
        var hours = Math.floor((dtDelta % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        var minutes = Math.floor((dtDelta % (1000 * 60 * 60)) / (1000 * 60));
        var seconds = Math.floor((dtDelta % (1000 * 60)) / 1000);

        let finalText = "";
        if (days !== 0) {
            finalText = `${days} days ago`
        } else if (hours !== 0) {
            finalText = `${hours} hours ago`
        } else if (minutes !== 0) {
            finalText = `${minutes} minutes ago`
        } else {
            finalText = `${seconds} seconds ago`
        }

        // Render card HTML
        document.getElementById("card-footer-" + hpId).textContent = finalText;
    });

    // Update CSS to center cards
    let cardContainer = document.getElementById("card-container");
    cardContainer.style.justifyContent = "center";
}

// Execute on page load
$(document).ready(function() {

    // Get JSON from server
    $.getJSON("api/v1/honeypots", function(data) {
        jsonData = data;
    }) // Build the HTML objects
     .done(function() {
        updateAllCards();
        updateCardFooters();
    });
});

// Start updating card footer times every second
function updateDate() {
    updateCardFooters();

} var run = setInterval(updateDate, 1000);

var flashOn = false;
function flashLive() {
    var d = new Date()
    
    $.each(jsonData, function (id, attributes) {
        // Verify card represents a honeypot under attack
        if (attributes.health == 3) {
            // Update component colors
            document.getElementById("card-body-" + id).style.backgroundColor = "rgb(255,220,220)";
            document.getElementById("card-footer-" + id).style.backgroundColor = "rgb(250,180,180)";

            // Update background
            if (!flashOn) {
                //set title here with document.title
                document.getElementById("card-" + id).style.border = "1px solid rgba(0, 0, 0, 0.125)";
                document.getElementById("card-" + id).style["boxShadow"] = null
                flashOn = true
            } else {
                document.getElementById("card-" + id).style.border = "1px solid red";
                document.getElementById("card-" + id).style["boxShadow"] = "0 0 5px red";
                flashOn = false
            }
            
        } // reversion should be handled elsewhere
    });
} var run = setInterval(flashLive, 250);