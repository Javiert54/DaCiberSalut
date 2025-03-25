document.addEventListener("DOMContentLoaded", function() {
    const fileList = document.getElementById("fileList");

    function fetchFiles() {
        fetch("/get_file_data")
        .then(response => response.json())
        .then(data => {
            fileList.innerHTML = "";
            data.files.forEach(file => {
                const listItem = document.createElement("li");
                const link = document.createElement("a");
                link.href = `/get_files/${file}`;
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