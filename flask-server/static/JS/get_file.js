document.addEventListener("DOMContentLoaded", function() {
    const uploadForm = document.getElementById("uploadForm");
    const fileInput = document.getElementById("fileInput");
    const fileList = document.getElementById("fileList");

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
            if (data.message) {
                fetchFiles();
            }
        })
        .catch(error => {
            console.error("Error:", error);
        });
    });

    function fetchFiles() {
        fetch("/list_files")
        .then(response => response.json())
        .then(data => {
            fileList.innerHTML = "";
            data.files.forEach(file => {
                const listItem = document.createElement("li");
                const link = document.createElement("a");
                link.href = `/get_file/${file}`;
                link.textContent = file;
                listItem.appendChild(link);
                fileList.appendChild(listItem);
            });
        })
        .catch(error => {
            console.error("Error:", error);
        });
    }

    fetchFiles();
});