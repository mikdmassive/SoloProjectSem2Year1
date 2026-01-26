
  const burgerMenu = document.getElementById("burgerMenu");
  const mainNav = document.getElementById("navBar");

  if (burgerMenu && mainNav) {
    console.info(burgerMenu)
    burgerMenu.addEventListener("click", function () {
      burgerMenu.classList.toggle("active");
      mainNav.classList.toggle("active");
    });
  }
