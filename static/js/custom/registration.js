// script.js

document.addEventListener("DOMContentLoaded", () => {
    const dropArea = document.getElementById("drop-area");
    const fileInput = document.getElementById("photoUpload");
    const clickToBrowse = document.getElementById("clickToBrowse");

    clickToBrowse.addEventListener("click", () => fileInput.click());

    dropArea.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropArea.classList.add("border-primary");
    });

    dropArea.addEventListener("dragleave", () => {
        dropArea.classList.remove("border-primary");
    });

    dropArea.addEventListener("drop", (e) => {
        e.preventDefault();
        dropArea.classList.remove("border-primary");
        fileInput.files = e.dataTransfer.files;
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const photoUpload = document.getElementById("photoUpload");
    const clickToBrowse = document.getElementById("clickToBrowse");
    const photoPreview = document.getElementById("photoPreview");
  
    // Handle click to open file selector
    clickToBrowse.addEventListener("click", () => {
      photoUpload.click();
    });
  
    // Handle image file upload and preview
    photoUpload.addEventListener("change", function () {
      const file = this.files[0];
  
      if (file && file.type.startsWith("image/")) {
        if (file.size <= 2 * 1024 * 1024) { // 2MB size check
          const reader = new FileReader();
          reader.onload = function (e) {
            photoPreview.src = e.target.result;
            photoPreview.style.display = "block";
          };
          reader.readAsDataURL(file);
        } else {
          alert("The selected file exceeds 2MB. Please choose a smaller image.");
          this.value = ''; // Reset file input
          photoPreview.style.display = "none";
        }
      }
    });
  });
  