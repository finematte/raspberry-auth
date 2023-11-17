window.onload = function() {
  const passwordInput = document.getElementById("password");
  const textPasswordInput = document.getElementById("text-password");
  const revealPasswordCheckbox = document.getElementById("reveal-password");

  // Synchronize the password and text inputs whenever the value changes
  passwordInput.addEventListener("input", function() {
    textPasswordInput.value = this.value;
  });

  textPasswordInput.addEventListener("input", function() {
    passwordInput.value = this.value;
  });

  // Reveal or hide the password when the checkbox is clicked
  revealPasswordCheckbox.addEventListener("change", function() {
    if (this.checked) {
      passwordInput.style.display = "none";
      textPasswordInput.style.display = "block";
    } else {
      textPasswordInput.style.display = "none";
      passwordInput.style.display = "block";
    }
  });
};
