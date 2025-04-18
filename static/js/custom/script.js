$(function () {
    $("#table").bootstrapTable();
});

document.addEventListener("click", function (e) {
    const row = e.target.closest("tr[data-url]");
    if (row) {
        row.style.cursor = "pointer";
        window.location.href = row.dataset.url;
    }
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === name + "=") {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
