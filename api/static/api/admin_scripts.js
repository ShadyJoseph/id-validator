// API Key Admin JavaScript Functions

function copyKey(key, btn) {
  navigator.clipboard
    .writeText(key)
    .then(() => {
      btn.textContent = "Copied!";
      btn.style.background = "#28a745";
      setTimeout(() => {
        btn.textContent = "Copy";
        btn.style.background = "#007bff";
      }, 2000);
    })
    .catch(() => {
      alert("Copy failed. Select and copy manually.");
    });
}

function hideKeyBox() {
  const keyBox = document.getElementById("key-box");
  if (keyBox) {
    keyBox.style.display = "none";
  }
}
