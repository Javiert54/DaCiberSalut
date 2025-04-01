document.addEventListener("DOMContentLoaded", function() {
    const fileInput = document.getElementById('fileInput');
    const uploadForm = document.getElementById("uploadForm");

    uploadForm.addEventListener("submit", function(event) {
        event.preventDefault();
        const fileExtension = fileInput.files[0].name.split('.').pop().toLowerCase();
        const formData = new FormData();
        formData.append("file", fileInput.files[0]);
        
        if (!['jpg', 'jpeg', 'png', 'bmp'].includes(fileExtension)) {
            console.log("The only extensions allowed are jpg, jpeg, png, bmp");
            document.getElementById("message").classList.remove("alert-success");
            document.getElementById("message").classList.add("alert-danger");
            document.getElementById("message").innerHTML = "The only extensions allowed are jpg, jpeg, png, bmp";
            document.getElementById("message").hidden = false;
            return; 
        } else {
            document.getElementById("message").classList.remove("alert-danger");
            document.getElementById("message").classList.add("alert-info"); 
            document.getElementById("message").innerHTML = "Processing image...";
            document.getElementById("message").hidden = false;
        }
   
        fetch("/upload_file", {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then((data) => {
            console.log(data)
        })
        .catch(() => {
            document.getElementById("message").classList.remove("alert-info");
            document.getElementById("message").classList.add("alert-danger");
            document.getElementById("message").innerHTML = "An error occurred while processing the image.";
            document.getElementById("message").hidden = false;
        });
    });   
});