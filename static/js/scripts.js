const body = document.querySelector("body");
const sidebar = body.querySelector(".sidebar");
const toggle = body.querySelector(".toggle");
const searchButton = document.getElementById("search-button");
const searchBox = document.getElementById("search");
const searchInput = document.getElementById("search-input");
const searchData = document.getElementById("search-data");
const clearSearch = document.getElementById("clear-search");
const searchSubmit = document.getElementById("search-submit");


toggle.addEventListener("click", () => {
    sidebar.classList.toggle("close");
});

document.addEventListener('DOMContentLoaded', async function() {
    const checkServiceConnection = async () => {
        try {
            const response = await fetch('/check_service_connection');

            if (response.ok) {
                const data = await response.json();

                if (data && data.status === 'success') {
                    document.getElementById('info-status').style.display = 'none';
                } else {
                    throw new Error('Erro ao conectar. Status: ' + data.status);
                }
            } else {
                throw new Error('Erro ao conectar. Erro: ' + response.status);
            }
        } catch (error) {
            document.getElementById('info-status').style.display = 'block';
            return;
        }
    };

    checkServiceConnection();
});

clearSearch.addEventListener("click", () => {
    searchData.value = "";
    $(".dados .row.click").show();
});

searchButton.addEventListener("click", (event) => {
    event.preventDefault();
    if (searchBox.style.display === "none" || searchBox.style.display === "") {
        searchBox.style.display = "block";
    } else {
        searchBox.style.display = "none";
    }
});

function goBack() {
    window.history.back();
}

function reloadPage() {
    setInterval(function() {    
        if(searchBox.style.display != "block"){
            location.reload(true);
        }
    }, 15000);
}

document.addEventListener('DOMContentLoaded', function() {
    var select = document.getElementById('items_per_page');

    // Set the selected value based on the current page URL parameter
    var urlParams = new URLSearchParams(window.location.search);
    var itemsPerPage = urlParams.get('items');
    if (itemsPerPage) {
        select.value = itemsPerPage;
    }

    // Update the URL when the selection changes
    select.addEventListener('change', function() {
        var selectedValue = this.value;
        var currentUrl = new URL(window.location.href);
        currentUrl.searchParams.set('items', selectedValue);

        // Ensure other search parameters are kept
        var page = urlParams.get('pag');
        var search = urlParams.get('search');
        if (page) {
            currentUrl.searchParams.set('pag', page);
        }
        if (search) {
            currentUrl.searchParams.set('search', search);
        }

        window.location.href = currentUrl.toString();
    });
});
