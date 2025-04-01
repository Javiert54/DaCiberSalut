document.addEventListener("DOMContentLoaded", function() {
    const imageList = document.getElementById("image-list");

    function fetchFiles() {
        fetch("/get_file_data")
        .then(response => response.json())
        .then(data => {
            data.files.forEach(file => {
                const imgHTML = `
                <div class="col-md-4 col-sm-6"> 
                    <img src="/static/storage/${file.file_name}" 
                        data-tags='[{"label": "Persona", "confidence": 0.8}, {"label": "Otra etiqueta", "confidence": 0.2}]' 
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

                let tags = JSON.parse(this.getAttribute("data-tags"));
                
                let tagList = document.getElementById("tagList");
                tagList.innerHTML = ""; 
                tags.forEach(tag => {
                    let li = document.createElement("li");
                    li.className = "list-group-item";
                    li.textContent = `${tag.label} - Confianza: ${(tag.confidence * 100).toFixed(2)}%`;
                    tagList.appendChild(li);
                });

                let modal = new bootstrap.Modal(document.getElementById("imageModal"));
                modal.show();
            });
        });
    }

    fetchFiles();
});