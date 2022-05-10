// Data and template declerations
var jsonData = null;

const cardTemplate = ({ id }) => 
`<div class="card" id="card-${id}" style="padding: 0; margin: 20px; width: 350px; background-color: rgb(252, 252, 252);">
${id}
</div>`;

const cardHeaderTemplate = ({ health, rgb }) => 
`<div class="card-header" style="background-color: rgb(${rgb}); color: rgb(255, 255, 255); text-align: center;">
    <state>${health}</state>
</div>`

// BODY TODO
const cardBodyTemplate = ({ placeholder }) => 
`<p>${placeholder}</p>`;
// ---

const cardFooterTemplate = ({ epoch }) => 
`<div class="card-footer text-muted" style="text-align: center;">
${epoch}
</div>`;


// Generate HTML from JSON and render
function updateCards() {
    let honeypot_cards = "";

    // Derive the card shells
    $.each(jsonData, function (hpId, hpAttributes) {
        honeypot_cards += [{ id: hpId }].map(cardTemplate).join();
    });

    // Render the card shells
    document.getElementById("card-container").innerHTML = honeypot_cards;
    
    // Derive Card Attributes
    $.each(jsonData, function (hpId, hpAttributes) {
        let honeypot_card = "";

        // Derive card headers relative to health
        switch (hpAttributes.health) {
            case "Healthy":
                honeypot_card += [{ health: "Healthy", rgb: [0, 200, 0]}].map(cardHeaderTemplate).join();
                break;
            case "Degraded":
                honeypot_card += [{ health: "Degraded", rgb: [200, 200, 0]}].map(cardHeaderTemplate).join();
                break;
            case "Compromised":
                honeypot_card += [{ health: "Compromised", rgb: [200, 0, 0]}].map(cardHeaderTemplate).join();
                break;
            case "Attacker Present":
                honeypot_card += [{ health: "Attacker Present", rgb: [200, 0, 0]}].map(cardHeaderTemplate).join();
                break;
        }
        
        // Derive card body relative to type
        switch (hpAttributes.type) {
            case "VPS":
                honeypot_card += [{ placeholder: "VPS Placeholder"}].map(cardBodyTemplate).join();
                break;
            case "Database":
                honeypot_card += [{ placeholder: "Database Placeholder"}].map(cardBodyTemplate).join();
                break;
        }

        // Derive card footer relative to state
        if (hpAttributes.type == "Healthy") {
            honeypot_card += [{ epoch: hpAttributes.updated }].map(cardFooterTemplate).join();
        } else { //TODO
            honeypot_card += [{ epoch: hpAttributes.updated }].map(cardFooterTemplate).join();
        }

        // Render card HTML
        document.getElementById("card-" + hpId).innerHTML = honeypot_card;
        honeypot_cards += honeypot_card
    });
}


// Execute on page load
$(document).ready(function() {

    // Get JSON from server
    $.getJSON("api/v1/honeypots", function(data) {
        jsonData = data;
    }) // Build the HTML objects
     .done(function() {
        updateCards();
    });
});