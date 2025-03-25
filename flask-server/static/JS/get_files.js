document.addEventListener("DOMContentLoaded", function() {
    const fileList = document.getElementById("fileList");

    function fetchFiles() {
        fetch("/get_file_data")
        .then(response => response.json())
        .then(data => {
            fileList.innerHTML = "";
            data.files.forEach(file => {
                console.log(file);
                const listItem = document.createElement("li");
                const link = document.createElement("a");
                link.href = `/get_files/${file.file_id}`;
                link.textContent = file.file_name;
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