function selectSize(button, size, price) {
    // Remove active class from all size buttons in the same card
    const sizeButtons = button.parentElement.querySelectorAll('.size-btn');
    sizeButtons.forEach(btn => btn.classList.remove('active'));
    // Add active class to clicked button
    button.classList.add('active');
    // Update price display
    const priceElement = button.closest('.product-card').querySelector('.price');
    priceElement.textContent = `$${price}`;
    // Update hidden variant_id input
    const variantInput = button.closest('.product-card').querySelector('.variant-id');
    variantInput.value = button.dataset.variantId || size; // Adjust based on variant ID
}