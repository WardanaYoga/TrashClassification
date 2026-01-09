const labelEl = document.getElementById("label");
const confidenceEl = document.getElementById("confidence");

// Polling hasil klasifikasi dari Raspberry Pi
setInterval(() => {
  fetch("http://10.39.30.211:5000/label")
    .then((response) => response.json())
    .then((data) => {
      labelEl.innerText = data.label;
      confidenceEl.innerText = `Confidence: ${(data.confidence * 100).toFixed(
        1
      )}%`;

      // Pewarnaan label
      if (data.label === "Organik") {
        labelEl.style.color = "green";
      } else if (data.label === "Anorganik") {
        labelEl.style.color = "blue";
      } else if (data.label === "Logam") {
        labelEl.style.color = "red";
      } else {
        labelEl.style.color = "black";
      }
    })
    .catch((err) => {
      labelEl.innerText = "Koneksi terputus";
      console.error(err);
    });
}, 500); // update setiap 500 ms

//10.39.30.211
