document.addEventListener('DOMContentLoaded', function () {
  var header = document.querySelector('.glass-header');
  var lastScroll = 0;

  if (header) {
    window.addEventListener('scroll', function () {
      var currentScroll = window.pageYOffset;

      if (currentScroll > lastScroll && currentScroll > 100) {
        header.style.transform = 'translateY(-100%)';
      } else {
        header.style.transform = 'translateY(0)';
      }

      // Adjust header transparency based on scroll depth
      var opacity = Math.min(0.55 + currentScroll * 0.001, 0.85);
      header.style.background = 'rgba(10, 17, 40, ' + opacity + ')';

      lastScroll = currentScroll;
    });
  }

  // Intersection Observer for glass card reveal animations
  var cards = document.querySelectorAll('.glass-card');
  var observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
        }
      });
    },
    { threshold: 0.08 }
  );

  cards.forEach(function (card) {
    card.style.opacity = '0';
    card.style.transform = 'translateY(24px)';
    card.style.transition = 'opacity 0.7s cubic-bezier(0.25, 0.46, 0.45, 0.94), transform 0.7s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
    observer.observe(card);
  });

  // Staggered animation for multiple cards
  var grid = document.querySelector('.articles-grid');
  if (grid) {
    var gridCards = grid.querySelectorAll('.glass-card');
    gridCards.forEach(function (card, i) {
      card.style.transitionDelay = (i * 0.06) + 's';
    });
  }
});
