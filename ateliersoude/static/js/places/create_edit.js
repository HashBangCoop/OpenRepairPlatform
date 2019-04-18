let addressesToCoordinates = {};

// Used to stop old ongoing request
let fetchController = new AbortController();
let signal = fetchController.signal;

function addrSelected(event, addr, item) {
    let longitude = document.getElementById("id_longitude");
    let latitude = document.getElementById("id_latitude");
    longitude.value = addressesToCoordinates[addr].longitude;
    latitude.value = addressesToCoordinates[addr].latitude;
}

function queryGovAddrAPI(lookupAddresses, suggest) {
    fetch(lookupAddresses, {
        method: 'get',
        signal: signal,
    }).then(function (res) {
        return res.json();
    }).then(function (data) {
        if (!data.features) {
            suggest([]);
            return;
        }
        let addrSuggestions = data.features.map(
            f => {
                label = f.properties.label;
                addressesToCoordinates[label] = {
                    longitude: f.geometry.coordinates[0],
                    latitude: f.geometry.coordinates[1],
                };
                return label;
            }
        );
        suggest(addrSuggestions);
    }).catch(function (err) {
        if (err.name !== "AbortError") {
            console.error(` Err: ${err}`);
        }
    });
}

new autoComplete({
    selector: '#id_address',
    onSelect: addrSelected,
    delay: 30,
    source: function(addr, suggest){
        let search = encodeURIComponent(addr);
        let lookupAddresses = "https://api-adresse.data.gouv.fr/search/?limit=15&lat=45.76&lon=4.84&q=" + search;

        // abort running fetch requests
        fetchController.abort();
        fetchController = new AbortController();
        signal = fetchController.signal;

        queryGovAddrAPI(lookupAddresses, suggest);
    }
});
