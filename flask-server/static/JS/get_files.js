document.addEventListener("DOMContentLoaded", function() {
    const imageList = document.getElementById("image-list");

    function fetchFiles() {
        fetch("/get_file_data")
        .then(response => response.json())
        .then(data => {
            data.files.forEach(file => {
                const imgHTML = `
                <div class="col-md-4 col-sm-6"> 
                    <img src="/static/storage/${file.file_name}" id="${file.file_id}" 
                        data-tags="${file.file_prediction}"
                        class="clickable img-thumbnail">
                </div>`;

                imageList.innerHTML += imgHTML;
            });

            assignClickEvents();
        })
        .catch(error => {
            console.error("Error:", error);
        });
    }

    function assignClickEvents() {
        document.querySelectorAll(".clickable").forEach(img => {
            img.addEventListener("click", function () {                
                document.getElementById("modalImage").src = this.src;

                const tags = JSON.parse(this.getAttribute("data-tags").replace(/'/g, '"'));
                const tagList = document.getElementById("tagList");

                tagList.innerHTML = "";

                Object.entries(tags).forEach(([label, probability]) => {
                    tagList.innerHTML += `
                    <div class="mb-3">
                        <span class="fw-semibold">${label}</span>
                        <div class="progress">
                        <div class="progress-bar bg-info" style="width: ${probability}%;">${probability}%</div>
                        </div>
                    </div>
                    `
                });
        
                const modal = new bootstrap.Modal(document.getElementById("imageModal"));
                modal.show();
            });
        });
    }

    document.getElementById("analyze-image").addEventListener("click", function() {
        const imgSrc = document.getElementById("modalImage").src;
        const fileName = imgSrc.split("/").pop(); // Get the file name from the src
        const documentID = document.getElementById("modalImage").id // Get the image ID

        fetch("/analyze_image", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ imgSrc: imgSrc })
        })
        .then(response => response.json())
        .then(data => {
            console.log(data)
        })
        .catch(error => {
            console.error("Error:", error);
        });
    })

    fetchFiles();
});