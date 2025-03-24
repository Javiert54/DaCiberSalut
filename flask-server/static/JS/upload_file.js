document.addEventListener("DOMContentLoaded", function() {
    const uploadForm = document.getElementById("uploadForm");
    const fileInput = document.getElementById("fileInput");

    uploadForm.addEventListener("submit", function(event) {
        event.preventDefault();
        const formData = new FormData();
        formData.append("file", fileInput.files[0]);

        fetch("/upload_file", {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log("Success:", data);
        })
        .catch(error => {
            console.error("Error:", error);
        });
    });
});