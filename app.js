document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("prediction-form");
  if (form) {
    form.addEventListener("submit", () => {
      const button = form.querySelector('button[type="submit"]');
      if (button) {
        button.disabled = true;
        button.innerHTML = 'Running model <span class="spinner"></span>';
      }
    });
  }

  document.querySelectorAll('input[type="number"]').forEach((input) => {
    input.addEventListener("input", () => {
      const min = Number(input.min);
      const max = Number(input.max);
      const value = Number(input.value);
      input.classList.toggle("invalid", input.value !== "" && (value < min || value > max));
    });
  });
});
