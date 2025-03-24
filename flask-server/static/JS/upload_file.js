document.addEventListener("DOMContentLoaded", function() {
    const uploadForm = document.getElementById("uploadForm");
    const fileInput = document.getElementById("fileInput");

    uploadForm.addEventListener("submit", function(event) {
        event.preventDefault();
        const formData = new FormData();
        formData.append("file", fileInput.files[0]);
        fileExtension = fileInput.files[0].name.split('.').pop().toLowerCase();
        if ( !['jpg', 'jpeg', 'png', 'bmp'].includes(fileExtension) ) {
            console.log("The only extensions allowed are jpg, jpeg, png, bmp");
            document.getElementById("message").innerHTML = "The only extensions allowed are jpg, jpeg, png, bmp";
            return false;
        } else {
            document.getElementById("message").innerHTML = "The Image has been uploaded successfully";
        }
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