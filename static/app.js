const form = document.querySelector("#convert-form");
const fileInput = document.querySelector("#files");
const dropZone = document.querySelector("#drop-zone");
const fileList = document.querySelector("#file-list");
const convertButton = document.querySelector("#convert-button");
const results = document.querySelector("#results");
const errorMessage = document.querySelector("#error-message");
const preview = document.querySelector("#preview");
const downloadButton = document.querySelector("#download-button");
let output = null;

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 ** 2) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 ** 2).toFixed(1)} MB`;
}

function renderFiles() {
  fileList.replaceChildren();
  [...fileInput.files].forEach((file) => {
    const item = document.createElement("div");
    const name = document.createElement("span");
    const size = document.createElement("small");
    name.textContent = file.name;
    size.textContent = formatBytes(file.size);
    item.append(name, size);
    fileList.append(item);
  });
}

["dragenter", "dragover"].forEach((eventName) => {
  dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.add("is-dragging");
  });
});

["dragleave", "drop"].forEach((eventName) => {
  dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.remove("is-dragging");
  });
});

dropZone.addEventListener("drop", (event) => {
  const csvFiles = [...event.dataTransfer.files].filter((file) => file.name.toLowerCase().endsWith(".csv"));
  const transfer = new DataTransfer();
  csvFiles.forEach((file) => transfer.items.add(file));
  fileInput.files = transfer.files;
  renderFiles();
});

fileInput.addEventListener("change", renderFiles);

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  errorMessage.hidden = true;
  results.hidden = true;
  convertButton.disabled = true;
  convertButton.textContent = "Processing…";

  try {
    const response = await fetch("/api/convert", { method: "POST", body: new FormData(form) });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Conversion failed.");

    output = data;
    document.querySelector("#included-count").textContent = data.stats.included.toLocaleString();
    document.querySelector("#undated-count").textContent = data.stats.undated.toLocaleString();
    document.querySelector("#outside-count").textContent = data.stats.out_of_range.toLocaleString();
    document.querySelector("#source-count").textContent = data.files.toLocaleString();
    document.querySelector("#output-name").textContent = data.filename;
    preview.textContent = data.markdown.slice(0, 30000) + (data.markdown.length > 30000 ? "\n\n… Preview limited to 30,000 characters. Download contains the complete archive." : "");
    results.hidden = false;
    results.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    errorMessage.textContent = error.message;
    errorMessage.hidden = false;
  } finally {
    convertButton.disabled = false;
    convertButton.textContent = "Clean and convert";
  }
});

downloadButton.addEventListener("click", () => {
  if (!output) return;
  const blob = new Blob([output.markdown], { type: "text/markdown;charset=utf-8" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = output.filename;
  link.click();
  URL.revokeObjectURL(link.href);
});
