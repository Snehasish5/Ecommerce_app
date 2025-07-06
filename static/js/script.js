// script.js - polished UI interactions

document.addEventListener("DOMContentLoaded", () => {
  console.log("ShopEase: Ready");

  // Animate flash alerts fade out after 4 seconds
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(alert => {
    setTimeout(() => {
      alert.classList.add('fade-out');
      alert.addEventListener('transitionend', () => alert.remove());
    }, 4000);
  });

  // Simple "Add to Cart" feedback
  const addToCartForms = document.querySelectorAll('form[action^="/add_to_cart"]');
  addToCartForms.forEach(form => {
    form.addEventListener('submit', e => {
      e.preventDefault();
      const btn = form.querySelector('button[type="submit"]');
      btn.disabled = true;
      btn.innerText = "Adding...";
      
      // simulate server response delay for UX
      setTimeout(() => {
        btn.disabled = false;
        btn.innerText = "Added!";
        setTimeout(() => {
          btn.innerText = "Add to Cart";
        }, 1500);
      }, 1000);
      
      // Actually submit the form after delay
      setTimeout(() => form.submit(), 1200);
    });
  });
});
document.getElementById("rzp-button1").onclick = function (e) {
  rzp1.open();
  e.preventDefault();
};
