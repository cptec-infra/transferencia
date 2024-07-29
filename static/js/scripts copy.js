// const body = document.querySelector("body");
// const sidebar = body.querySelector(".sidebar");
// const toggle = body.querySelector(".toggle");
// const searchButton = document.getElementById("search-button");
// const searchBox = document.getElementById("search");
// const searchInput = document.getElementById("search-data");
// const clearSearch = document.getElementById("clearSearch");
// const rowsPerPage = 20;  
// let currentPage = 1;
// let totalPages = 1;
// let rows = [];

// toggle.addEventListener("click", () => {
//     sidebar.classList.toggle("close");
// });

// document.addEventListener('DOMContentLoaded', async function() {
//     const checkServiceConnection = async () => {
//         try {
//             const response = await fetch('/check_service_connection');
//             if (response.ok) {
//                 const data = await response.json();
//                 if (data && data.status === 'success') {
//                     document.getElementById('info-status').style.display = 'none';
//                 } else {
//                     throw new Error('Erro ao conectar. Status: ' + data.status);
//                 }
//             } else {
//                 throw new Error('Erro ao conectar. Erro: ' + response.status);
//             }
//         } catch (error) {
//             document.getElementById('info-status').style.display = 'block';
//             return;
//         }
//     };

//     checkServiceConnection();
//     initPagination();
// });

// function initPagination() {
//     rows = Array.from(document.querySelectorAll(".dados .dado-row"));
//     updatePagination();
//     displayRows();
// }

// function updatePagination() {
//     const visibleRows = rows.filter(row => row.style.display !== 'none');
//     totalPages = Math.ceil(visibleRows.length / rowsPerPage);
//     updatePageInfo();
// }

// // function displayRows() {
// //     const visibleRows = rows.filter(row => row.style.display !== 'none');
// //     const start = (currentPage - 1) * rowsPerPage;
// //     const end = start + rowsPerPage;

// //     rows.forEach(row => row.style.display = 'none'); // Hide all rows
// //     visibleRows.slice(start, end).forEach(row => row.style.display = ""); // Show only rows for the current page
// // }

// function displayRows() {
//     const start = (currentPage - 1) * rowsPerPage;
//     const end = start + rowsPerPage;

//     rows.forEach((row, index) => {
//         if (index >= start && index < end && row.style.display !== 'none') {
//             row.style.display = ""; // Exibir a linha se estiver dentro do intervalo de exibição e não estiver oculta
//         } else {
//             row.style.display = "none"; // Ocultar a linha se estiver fora do intervalo de exibição ou estiver oculta
//         }
//     });
// }

// function updatePageInfo() {
//     document.getElementById("page-info").textContent = `Página ${currentPage} de ${totalPages}`;
//     document.getElementById("prev-page").disabled = currentPage === 1;
//     document.getElementById("next-page").disabled = currentPage === totalPages;
// }

// document.getElementById("prev-page").addEventListener("click", () => {
//     if (currentPage > 1) {
//         currentPage--;
//         displayRows();
//         updatePageInfo();
//     }
// });

// document.getElementById("next-page").addEventListener("click", () => {
//     if (currentPage < totalPages) {
//         currentPage++;
//         displayRows();
//         updatePageInfo();
//     }
// });

// clearSearch.addEventListener("click", () => {
//     searchInput.value = "";
//     rows.forEach(row => row.style.display = ""); // Show all rows
//     currentPage = 1;
//     // updatePagination();
//     // displayRows();
// });

// searchButton.addEventListener("click", (event) => {
//     event.preventDefault();
//     if (searchBox.style.display === "none" || searchBox.style.display === "") {
//         searchBox.style.display = "block";
//     } else {
//         searchBox.style.display = "none";
//     }
// });

// searchInput.addEventListener("keyup", () => {
//     const value = searchInput.value.toLowerCase();
//     rows.forEach(row => {
//         const text = row.textContent.toLowerCase();
//         row.style.display = text.includes(value) ? "" : "none";
//     });
//     currentPage = 1;
//     updatePagination();
//     displayRows();
// });





const body = document.querySelector("body");
const sidebar = body.querySelector(".sidebar");
const toggle = body.querySelector(".toggle");
const searchButton = document.getElementById("search-button");
const searchBox = document.getElementById("search");
const searchInput = document.getElementById("search-data");
const clearSearch = document.getElementById("clearSearch");
// const rowsPerPage = 20;  
// let currentPage = 1;
// let totalPages = 1;
// let rows = [];

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
    // initPagination();
});

// function initPagination() {
//     rows = Array.from(document.querySelectorAll(".dados .dado-row"));
//     updatePagination();
//     displayRows();
// }

// function updatePagination() {
//     const visibleRows = rows.filter(row => row.style.display !== 'none');
//     totalPages = Math.ceil(visibleRows.length / rowsPerPage);
//     updatePageInfo();
// }

// function displayRows() {
//     const start = (currentPage - 1) * rowsPerPage;
//     const end = start + rowsPerPage;

//     rows.forEach((row, index) => {
//         if (index >= start && index < end && row.style.display !== 'none') {
//             row.style.display = ""; // Exibir a linha se estiver dentro do intervalo de exibição e não estiver oculta
//         } else {
//             row.style.display = "none"; // Ocultar a linha se estiver fora do intervalo de exibição ou estiver oculta
//         }
//     });
// }

// function updatePageInfo() {
//     document.getElementById("page-info").textContent = `Página ${currentPage} de ${totalPages}`;
//     document.getElementById("prev-page").disabled = currentPage === 1;
//     document.getElementById("next-page").disabled = currentPage === totalPages;
// }

// document.getElementById("prev-page").addEventListener("click", () => {
//     if (currentPage > 1) {
//         currentPage--;
//         displayRows();
//         updatePageInfo();
//     }
// });

// document.getElementById("next-page").addEventListener("click", () => {
//     if (currentPage < totalPages) {
//         currentPage++;
//         displayRows();
//         updatePageInfo();
//     }
// });

// clearSearch.addEventListener("click", () => {
//     searchInput.value = "";
//     rows.forEach(row => row.style.display = ""); // Show all rows
//     currentPage = 1;
//     updatePagination();
//     displayRows();
// });

searchButton.addEventListener("click", (event) => {
    event.preventDefault();
    if (searchBox.style.display === "none" || searchBox.style.display === "") {
        searchBox.style.display = "block";
    } else {
        searchBox.style.display = "none";
    }
});

searchInput.addEventListener("keyup", () => {
    const value = searchInput.value.toLowerCase();
    const filteredVisibleRows = rows.filter(row => {
        const text = row.textContent.toLowerCase();
        return text.includes(value) && row.style.display !== 'none';
    });

    // totalPages = Math.ceil(filteredVisibleRows.length / rowsPerPage);
    // currentPage = 1;
    // displayRows();
    // updatePageInfo();
});

