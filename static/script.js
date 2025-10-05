function toPascalCase(str) {
  return str
    .split(" ")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join("");
}


document
  .getElementById("predictForm")
  .addEventListener("submit", async function (e) {
    e.preventDefault();

    let inputs = document.querySelectorAll("#predictForm input");
    let features = [];
    inputs.forEach((input) => features.push(parseFloat(input.value)));

    let res = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ features: features }),
    });

    let data = await res.json();
    const modal = document.getElementById("resultModal");
    const resultsBox = document.getElementById("resultsBox");

    if (data.prediction) {
      let probText = "";
      if (data.probabilities) {
        probText = "<p><strong>Class Probabilities:</strong></p>";
        for (let key in data.probabilities) {
          probText += `
          <div class="prob-bar-container mb-2">
            <span>${toPascalCase(key)}: ${(
            data.probabilities[key] * 100
          ).toFixed(2)}%</span>
            <div class="bg-gray-200 h-2 rounded">
              <div class="bg-blue-500 h-2 rounded" style="width:${
                data.probabilities[key] * 100
              }%"></div>
            </div>
          </div>
        `;
        }
      }
      resultsBox.innerHTML = `<h3 class="font-bold">Prediction: ${data.prediction
        .toLowerCase()
        .split(" ")
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join("")}</h3>${probText}`;
    } else {
      resultsBox.innerHTML = `<h3 class="text-red-600">Error: ${data.error}</h3>`;
    }
    modal.classList.remove("hidden");
  });
document.getElementById("closeModal").addEventListener("click", () => {
  document.getElementById("resultModal").classList.add("hidden");
});

resultsBox.classList.remove("show");
void resultsBox.offsetWidth;
resultsBox.classList.add("show");
const formLabel = document.querySelector(".form-label");
const formInputs = document.querySelectorAll("#predictForm input");

formInputs.forEach((input) => {
  input.addEventListener("input", () => {
    const anyFilled = Array.from(formInputs).some((i) => i.value.trim() !== "");
    formLabel.textContent = anyFilled ? "Remove details" : "Enter the details";
    formLabel.style.cursor = anyFilled ? "pointer" : "default";
  });
});

formLabel.addEventListener("click", () => {
  if (formLabel.textContent === "Remove details") {
    formInputs.forEach((input) => (input.value = ""));
    formLabel.textContent = "Enter the details";
  }
});

document.querySelector("#animated-btn").addEventListener("click", (e) => {
  e.preventDefault(); // prevent default if it's a link
  document.querySelector("#form-section").scrollIntoView({
    behavior: "smooth",
  });
});
