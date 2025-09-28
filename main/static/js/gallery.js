// Category Filtering
const filterButtons = document.querySelectorAll('.filter-button');
const galleryItems = document.querySelectorAll('.gallery-item');

filterButtons.forEach(button => {
  button.addEventListener('click', () => {
    // Update active button
    filterButtons.forEach(btn => btn.classList.remove('active'));
    button.classList.add('active');

    const category = button.getAttribute('data-category');

    galleryItems.forEach(item => {
      if (category === 'all' || item.getAttribute('data-category') === category) {
        item.style.display = 'block';
      } else {
        item.style.display = 'none';
      }
    });
  });
});

// Simple Lightbox (Optional enhancement)
document.querySelectorAll('.lightbox').forEach(link => {
  link.addEventListener('click', function (e) {
    e.preventDefault();
    const src = this.getAttribute('href');
    const overlay = document.createElement('div');
    overlay.classList.add('lightbox-overlay');
    overlay.innerHTML = `<img src="${src}" alt="Enlarged image"><span class="close-lightbox">&times;</span>`;
    document.body.appendChild(overlay);

    document.querySelector('.close-lightbox').onclick = () => overlay.remove();
    overlay.onclick = (event) => {
      if (event.target === overlay) overlay.remove();
    };
  });
});
