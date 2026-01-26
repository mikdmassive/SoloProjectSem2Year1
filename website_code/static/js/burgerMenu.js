
const burgerMenu = document.getElementById("burgerMenu");
const mainNav = document.getElementById("navBar");
const ProfileDiv = document.getElementById("ProfileDiv");
  if (burgerMenu && mainNav&&ProfileDiv) {
    console.info(burgerMenu)
    burgerMenu.addEventListener("click", function () {
      burgerMenu.classList.toggle("active");
      mainNav.classList.toggle("active");
  
      ProfileDiv.classList.toggle("active");
    });
  }
