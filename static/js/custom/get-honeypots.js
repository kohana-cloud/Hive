// Data and template declerations
var jsonData = null;

function cardTemplate(id, attributes) {
    return `
    <card id="card-${id}" class="card" style="padding: 0; margin: 20px; width: 200px; background-color: rgb(252, 252, 252);"></card>`
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
            var cardTitle = "Thinkbox Frost";
            break;
        case "LAMBDA":
            var cardGraphic = "lambda_grey.svg";
            var cardTitle = "Lambda";
            break;
        case "DEADLINE":
            var cardGraphic = "thinkbox_deadline_grey.svg";
            var cardTitle = "Thinkbox Deadline";
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

    if (attributes.health == 0) {
        var buttonImageDisabled = "disabled";
    }
    
    return `
    <div id="card-body-${id}" class="card-body">
        <img src="static/graphics/endpoint-images/${cardGraphic}" height=75 style="display: block; margin:auto; border-radius:15px;">
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

function cardRenderNew() {
    return `
    <card id="card-new" class="card" style="min-height: 425px; padding: 0; margin: 20px; width: 200px; background-color: rgb(252, 252, 252);">
        <img id="card-new-img" src="static/graphics/endpoint-images/plus-dotted.svg" height=100 class="width: max-content; card-img-top" style="position: absolute; top: 50%; -ms-transform: translateY(-50%);transform: translateY(-50%);"/>
    </card>`
}


// Generate HTML from JSON and render
function updateAllCards() {
    let honeypot_cards = "";

    // Derive the card shells
    $.each(jsonData, function (hpId, hpAttributes) {
        honeypot_cards += cardTemplate(hpId);
    });

    // Add new block
    honeypot_cards += cardRenderNew()

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
    let dtNow = new Date().getTime();

    // Update Text
    $.each(jsonData, function (hpId, hpAttributes) {
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

        //This bug is due to not having up to date context, need to revise this all, will likely do it when i do the sorting

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
                document.getElementById("card-" + id).style.border = "1px solid rgba(0, 0, 0, 0.125)";
                document.getElementById("card-" + id).style["boxShadow"] = null

                document.title = "The Hive  🔴"
            } else {
                document.getElementById("card-" + id).style.border = "1px solid red";
                document.getElementById("card-" + id).style["boxShadow"] = "0 0 5px red";

                document.title = "The Hive"
            }
            
        } // reversion should be handled elsewhere
    });

    // Flip state
    if (flashOn) {
        flashOn = false;
    } else {
        flashOn = true;
    }
    
} var run = setInterval(flashLive, 250);


function delay(time) {
    return new Promise(resolve => setTimeout(resolve, time));
  }

// Hover if element exists
function registerCardHover() {
    if (document.getElementById('card-new')) {
        $("card").hover(
            function() {
                this.style.border = "1px solid rgba(0, 0, 0, 0.5)";
                this.style["boxShadow"] = "0 0 5px grey";
            }, function() {
                this.style.border = null;
                this.style["boxShadow"] = null;
            }
        );

        $("#card-new").off('click').on('click', function() {
            $("#createHoneypot").modal('show');
        });
    }

    if (document.getElementById('card-new-img')) {
        $("#card-new").hover(
            function() {
                this.style.backgroundColor = "rgba(240,240,240)";
            }, function() {
                this.style.backgroundColor = "rgba(252,252,252)";
            }
        );
    }

    //need to update the column arangement so it doesnt move when borders change
    if (document.getElementById('hp-ec2')) {
        $("#hp-ec2").off('click').on('click', async function() {
            //if we want to protect CSRF here we need to set that up, currently excluded
            $.post('/api/v1/honeypots', { type: 'ec2' });

            $("#createHoneypot").modal('hide');
            await delay(1000);
            newhp = true;

            // Get JSON from server
            $.getJSON("api/v1/honeypots", function(data) {jsonData = data});
            await delay(1000); 

            updateAllCards();
            updateCardFooters();
        });
        
        $("#hp-bottlerocket").off('click').on('click', async function() {
            //if we want to protect CSRF here we need to set that up, currently excluded
            $.post('/api/v1/honeypots', { type: 'bottlerocket' });
            $("#createHoneypot").modal('hide');
            await delay(1000);
            newhp = true;

            // Get JSON from server
            $.getJSON("api/v1/honeypots", function(data) {jsonData = data});
            await delay(1000); 

            updateAllCards();
            updateCardFooters();
        });
        
        $("#hp-ecs").off('click').on('click', async function() {
            //if we want to protect CSRF here we need to set that up, currently excluded
            $.post('/api/v1/honeypots', { type: 'ecs' });
            $("#createHoneypot").modal('hide');
            await delay(1000);
            newhp = true;

            // Get JSON from server
            $.getJSON("api/v1/honeypots", function(data) {jsonData = data});
            await delay(1000); 

            updateAllCards();
            updateCardFooters();
        });

        $("#hp-frost").off('click').on('click', async function() {
            //if we want to protect CSRF here we need to set that up, currently excluded
            $.post('/api/v1/honeypots', { type: 'frost' });
            $("#createHoneypot").modal('hide');
            await delay(1000);
            newhp = true;

            // Get JSON from server
            $.getJSON("api/v1/honeypots", function(data) {jsonData = data});
            await delay(1000); 

            updateAllCards();
            updateCardFooters();
        });

        $("#hp-lambda").off('click').on('click', async function() {
            //if we want to protect CSRF here we need to set that up, currently excluded
            $.post('/api/v1/honeypots', { type: 'lambda' });
            $("#createHoneypot").modal('hide');
            await delay(1000);
            newhp = true;

            // Get JSON from server
            $.getJSON("api/v1/honeypots", function(data) {jsonData = data});
            await delay(1000); 

            updateAllCards();
            updateCardFooters();
        });

        $("#hp-deadline").off('click').on('click', async function() {
            //if we want to protect CSRF here we need to set that up, currently excluded
            $.post('/api/v1/honeypots', { type: 'deadline' });
            $("#createHoneypot").modal('hide');
            await delay(1000);
            newhp = true;

            // Get JSON from server
            $.getJSON("api/v1/honeypots", function(data) {jsonData = data});
            await delay(1000); 

            updateAllCards();
            updateCardFooters();
        });

        $("#hp-outpost").off('click').on('click', async function() {
            //if we want to protect CSRF here we need to set that up, currently excluded
            $.post('/api/v1/honeypots', { type: 'outpost' });
            $("#createHoneypot").modal('hide');
            await delay(1000);
            newhp = true;

            // Get JSON from server
            $.getJSON("api/v1/honeypots", function(data) {jsonData = data});
            await delay(1000); 

            updateAllCards();
            updateCardFooters();
        });

        $("#hp-parallel").off('click').on('click', async function() {
            //if we want to protect CSRF here we need to set that up, currently excluded
            $.post('/api/v1/honeypots', { type: 'parallel' });
            $("#createHoneypot").modal('hide');
            await delay(1000);
            newhp = true;

            // Get JSON from server
            $.getJSON("api/v1/honeypots", function(data) {jsonData = data});
            await delay(1000); 

            updateAllCards();
            updateCardFooters();
        });

        $("#hp-serverless").off('click').on('click', async function() {
            //if we want to protect CSRF here we need to set that up, currently excluded
            $.post('/api/v1/honeypots', { type: 'serverless' });
            $("#createHoneypot").modal('hide');
            await delay(1000);
            newhp = true;

            // Get JSON from server
            $.getJSON("api/v1/honeypots", function(data) {jsonData = data});
            await delay(1000); 

            updateAllCards();
            updateCardFooters();
        });
    }

    
   
} var run = setInterval(registerCardHover, 500);
