
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
            window.location.href = routeUrl + id; // Redirect to the passed URL with the id
        }
    });
}



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
