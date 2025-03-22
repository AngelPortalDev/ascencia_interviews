
function confirmDelete(id, routeUrl) {
    Swal.fire({
        title: 'Are you sure you want to delete this?',
        text: "This action cannot be undone!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Yes, delete it!',
        cancelButtonText: 'No, keep it'
    }).then((result) => {
        if (result.isConfirmed) {
            window.location.href = routeUrl + id + '/'; // Redirect to the passed URL with the id
        }
    });
}

// Track refresh count in localStorage
if (!localStorage.getItem("refreshData")) {
    localStorage.setItem("refreshData", JSON.stringify({ count: 0, lastTime: Date.now() }));
}

function preventExcessiveRefresh() {
    let refreshData = JSON.parse(localStorage.getItem("refreshData")) || { count: 0, lastTime: 0 };
    let now = Date.now();

    // If the last refresh was within 1 second, increase count
    if (now - refreshData.lastTime < 1000) {
        refreshData.count++;
    } else {
        refreshData.count = 1; // Reset count if more than 1 sec passed
    }

    refreshData.lastTime = now;

    // Block page reload if exceeded 2 refreshes within 1 second
    if (refreshData.count > 2) {
        history.pushState(null, "", location.href); // Prevent browser refresh
        return false;
    }

    // Store updated data
    localStorage.setItem("refreshData", JSON.stringify(refreshData));
}

// Call function on page load
preventExcessiveRefresh();




// document.addEventListener("DOMContentLoaded", function () {
    
// });

// $("#updateUserProfile").on("click", function (e) {
//     e.preventDefault();
//     showAlerts(); 
// });

// function showAlerts() {
//     const successMessage = document.querySelector("#success-message")?.value;
//     const errorMessage = document.querySelector("#error-message")?.value;

//     if (successMessage) {
//         Swal.fire({
//             title: "Success!",
//             text: successMessage,
//             icon: "success",
//             confirmButtonText: "OK",
//         });
//     }

//     if (errorMessage) {
//         Swal.fire({
//             title: "Error!",
//             text: errorMessage,
//             icon: "error",
//             confirmButtonText: "OK",
//         });
//     }
// }
