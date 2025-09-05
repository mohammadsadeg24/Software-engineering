// Pure Honey Shop - JavaScript Functions

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeToasts();
    initializeCartCounter();
    initializeSearchForm();
    initializeProductFilters();
    initializeLazyLoading();
    initializeScrollEffects();
    
    console.log('Pure Honey Shop - Scripts loaded successfully');
});

// Toast Notification System
function initializeToasts() {
    // Create toast container if it doesn't exist
    if (!document.querySelector('.toast-container')) {
        const toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container';
        document.body.appendChild(toastContainer);
    }
}

function showToast(message, type = 'info', duration = 5000) {
    const toastContainer = document.querySelector('.toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    let icon = 'fas fa-info-circle';
    switch(type) {
        case 'success':
            icon = 'fas fa-check-circle';
            break;
        case 'error':
            icon = 'fas fa-exclamation-circle';
            break;
        case 'warning':
            icon = 'fas fa-exclamation-triangle';
            break;
    }
    
    toast.innerHTML = `
        <div class="toast-icon">
            <i class="${icon}"></i>
        </div>
        <div class="toast-message">${message}</div>
        <button class="toast-close" onclick="closeToast(this)">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    toastContainer.appendChild(toast);
    
    // Show toast with animation
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);
    
    // Auto remove toast
    setTimeout(() => {
        closeToast(toast.querySelector('.toast-close'));
    }, duration);
}

function closeToast(button) {
    const toast = button.closest('.toast');
    toast.classList.remove('show');
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 300);
}

// Cart Management
function initializeCartCounter() {
    updateCartCount();
}

function updateCartCount() {
    fetch('/api/cart/count/', {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        const cartCount = document.getElementById('cart-count');
        if (cartCount) {
            cartCount.textContent = data.count || 0;
            cartCount.style.display = data.count > 0 ? 'block' : 'none';
        }
    })
    .catch(error => {
        console.error('Error updating cart count:', error);
    });
}

function addToCart(productId, variantId = null, quantity = 1) {
    const formData = new FormData();
    formData.append('product_id', productId);
    formData.append('quantity', quantity);
    if (variantId) {
        formData.append('variant_id', variantId);
    }
    
    fetch('/cart/add/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Product added to cart!', 'success');
            updateCartCount();
        } else {
            showToast(data.message || 'Error adding product to cart', 'error');
        }
    })
    .catch(error => {
        console.error('Error adding to cart:', error);
        showToast('Error adding product to cart', 'error');
    });
}

// Search Functionality
function initializeSearchForm() {
    const searchForm = document.querySelector('.search-form');
    const searchInput = document.querySelector('.search-input');
    
    if (searchForm && searchInput) {
        // Add search suggestions functionality
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length >= 3) {
                searchTimeout = setTimeout(() => {
                    fetchSearchSuggestions(query);
                }, 300);
            } else {
                hideSearchSuggestions();
            }
        });
        
        // Hide suggestions when clicking outside
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.search-container')) {
                hideSearchSuggestions();
            }
        });
    }
}

function fetchSearchSuggestions(query) {
    fetch(`/api/search/suggestions/?q=${encodeURIComponent(query)}`)
    .then(response => response.json())
    .then(data => {
        showSearchSuggestions(data.suggestions || []);
    })
    .catch(error => {
        console.error('Error fetching search suggestions:', error);
    });
}

function showSearchSuggestions(suggestions) {
    hideSearchSuggestions(); // Remove existing suggestions
    
    if (suggestions.length === 0) return;
    
    const searchContainer = document.querySelector('.search-container');
    const suggestionsDiv = document.createElement('div');
    suggestionsDiv.className = 'search-suggestions';
    suggestionsDiv.innerHTML = suggestions.map(suggestion => 
        `<div class="search-suggestion" onclick="selectSuggestion('${suggestion}')">${suggestion}</div>`
    ).join('');
    
    searchContainer.appendChild(suggestionsDiv);
}

function hideSearchSuggestions() {
    const suggestions = document.querySelector('.search-suggestions');
    if (suggestions) {
        suggestions.remove();
    }
}

function selectSuggestion(suggestion) {
    const searchInput = document.querySelector('.search-input');
    searchInput.value = suggestion;
    hideSearchSuggestions();
    searchInput.closest('form').submit();
}

// Product Filters
function initializeProductFilters() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const sortSelect = document.getElementById('sortSelect');
    
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            const url = new URL(window.location);
            if (this.value) {
                url.searchParams.set('sort', this.value);
            } else {
                url.searchParams.delete('sort');
            }
            window.location = url.toString();
        });
    }
    
    // Initialize price range filter if exists
    initializePriceFilter();
}

function initializePriceFilter() {
    const priceRange = document.getElementById('priceRange');
    const priceDisplay = document.getElementById('priceDisplay');
    
    if (priceRange && priceDisplay) {
        priceRange.addEventListener('input', function() {
            priceDisplay.textContent = `$0 - $${this.value}`;
        });
        
        priceRange.addEventListener('change', function() {
            const url = new URL(window.location);
            url.searchParams.set('max_price', this.value);
            window.location = url.toString();
        });
    }
}

// Lazy Loading for Images
function initializeLazyLoading() {
    const images = document.querySelectorAll('img[loading="lazy"]');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src || img.src;
                    img.classList.remove('lazy');
                    observer.unobserve(img);
                }
            });
        });
        
        images.forEach(img => {
            imageObserver.observe(img);
        });
    }
}

// Scroll Effects
function initializeScrollEffects() {
    // Navbar scroll effect
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Back to top button
    createBackToTopButton();
}

function createBackToTopButton() {
    const backToTop = document.createElement('button');
    backToTop.className = 'btn btn-honey back-to-top';
    backToTop.innerHTML = '<i class="fas fa-arrow-up"></i>';
    backToTop.style.cssText = `
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: none;
        z-index: 1000;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    `;
    
    backToTop.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > 500) {
            backToTop.style.display = 'block';
        } else {
            backToTop.style.display = 'none';
        }
    });
    
    document.body.appendChild(backToTop);
}

// Product Variants
function selectSize(button, size, price) {
    // Remove active class from all size buttons
    button.parentNode.querySelectorAll('.size-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Add active class to clicked button
    button.classList.add('active');
    
    // Update price display
    const productCard = button.closest('.product-card');
    const priceElement = productCard.querySelector('.price');
    if (priceElement) {
        priceElement.textContent = '$' + price;
    }
    
    // Update hidden variant field
    const variantField = productCard.querySelector('.variant-id');
    if (variantField && button.dataset.variantId) {
        variantField.value = button.dataset.variantId;
    }
}

function selectVariant(button) {
    // Remove active class from all variant buttons
    button.parentNode.querySelectorAll('.variant-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Add active class to clicked button
    button.classList.add('active');
    
    // Update price if data attributes exist
    if (button.dataset.price) {
        const priceElement = button.closest('.product-detail-section, .product-card').querySelector('.current-price, .variant-price');
        if (priceElement) {
            priceElement.textContent = '$' + button.dataset.price;
        }
    }
    
    // Update hidden variant field
    if (button.dataset.variantId) {
        const variantField = document.getElementById('selectedVariantId') || 
                            button.closest('form').querySelector('.variant-id');
        if (variantField) {
            variantField.value = button.dataset.variantId;
        }
    }
}

// Quantity Controls
function increaseQuantity(button) {
    const input = button.previousElementSibling || button.parentNode.querySelector('.qty-input');
    if (input) {
        const currentValue = parseInt(input.value) || 1;
        const maxValue = parseInt(input.getAttribute('max')) || 99;
        if (currentValue < maxValue) {
            input.value = currentValue + 1;
            input.dispatchEvent(new Event('change'));
        }
    }
}

function decreaseQuantity(button) {
    const input = button.nextElementSibling || button.parentNode.querySelector('.qty-input');
    if (input) {
        const currentValue = parseInt(input.value) || 1;
        const minValue = parseInt(input.getAttribute('min')) || 1;
        if (currentValue > minValue) {
            input.value = currentValue - 1;
            input.dispatchEvent(new Event('change'));
        }
    }
}

// Form Validation
function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function validatePhone(phone) {
    const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
    return phoneRegex.test(phone.replace(/\s/g, ''));
}

function validateForm(formElement) {
    let isValid = true;
    const requiredFields = formElement.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            showFieldError(field, 'This field is required');
            isValid = false;
        } else {
            clearFieldError(field);
            
            // Additional validation based on field type
            if (field.type === 'email' && !validateEmail(field.value)) {
                showFieldError(field, 'Please enter a valid email address');
                isValid = false;
            } else if (field.type === 'tel' && !validatePhone(field.value)) {
                showFieldError(field, 'Please enter a valid phone number');
                isValid = false;
            }
        }
    });
    
    return isValid;
}

function showFieldError(field, message) {
    clearFieldError(field);
    
    field.classList.add('is-invalid');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(field) {
    field.classList.remove('is-invalid');
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

// Wishlist Functions
function addToWishlist(productId) {
    fetch('/wishlist/add/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
            'X-Requested-With': 'XMLHttpRequest',
        },
        body: JSON.stringify({ product_id: productId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Added to wishlist!', 'success');
            // Update wishlist icon if exists
            const wishlistBtn = document.querySelector(`[data-product-id="${productId}"] .wishlist-btn`);
            if (wishlistBtn) {
                wishlistBtn.querySelector('i').className = 'fas fa-heart';
                wishlistBtn.setAttribute('onclick', `removeFromWishlist(${productId})`);
            }
        } else {
            showToast(data.message || 'Error adding to wishlist', 'error');
        }
    })
    .catch(error => {
        console.error('Error adding to wishlist:', error);
        showToast('Error adding to wishlist', 'error');
    });
}

function removeFromWishlist(productId) {
    fetch('/wishlist/remove/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
            'X-Requested-With': 'XMLHttpRequest',
        },
        body: JSON.stringify({ product_id: productId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Removed from wishlist', 'success');
            // Update wishlist icon if exists
            const wishlistBtn = document.querySelector(`[data-product-id="${productId}"] .wishlist-btn`);
            if (wishlistBtn) {
                wishlistBtn.querySelector('i').className = 'far fa-heart';
                wishlistBtn.setAttribute('onclick', `addToWishlist(${productId})`);
            }
        } else {
            showToast(data.message || 'Error removing from wishlist', 'error');
        }
    })
    .catch(error => {
        console.error('Error removing from wishlist:', error);
        showToast('Error removing from wishlist', 'error');
    });
}

// Product Quick View
function showQuickView(productId) {
    fetch(`/api/products/${productId}/quick-view/`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            createQuickViewModal(data.product);
        } else {
            showToast('Error loading product details', 'error');
        }
    })
    .catch(error => {
        console.error('Error loading quick view:', error);
        showToast('Error loading product details', 'error');
    });
}

function createQuickViewModal(product) {
    const modalHtml = `
        <div class="modal fade" id="quickViewModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${product.name}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-6">
                                <img src="${product.image}" alt="${product.name}" class="img-fluid rounded">
                            </div>
                            <div class="col-md-6">
                                <p>${product.description}</p>
                                <div class="product-price mb-3">
                                    <span class="price">$${product.price}</span>
                                </div>
                                <button class="btn btn-honey" onclick="addToCart(${product.id})">
                                    Add to Cart
                                </button>
                                <a href="/products/${product.id}/" class="btn btn-outline-honey ms-2">
                                    View Details
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal
    const existingModal = document.getElementById('quickViewModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add new modal
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('quickViewModal'));
    modal.show();
}

// Utility Functions
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}

function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            timeout = null;
            if (!immediate) func(...args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func(...args);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Loading States
function showLoading(element) {
    if (element) {
        element.disabled = true;
        const originalContent = element.innerHTML;
        element.setAttribute('data-original-content', originalContent);
        element.innerHTML = '<span class="loading-spinner"></span> Loading...';
    }
}

function hideLoading(element) {
    if (element && element.hasAttribute('data-original-content')) {
        element.disabled = false;
        element.innerHTML = element.getAttribute('data-original-content');
        element.removeAttribute('data-original-content');
    }
}

// Local Storage Helpers
function setLocalStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
        console.warn('LocalStorage not available:', error);
    }
}

function getLocalStorage(key, defaultValue = null) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
        console.warn('Error reading from LocalStorage:', error);
        return defaultValue;
    }
}

function removeLocalStorage(key) {
    try {
        localStorage.removeItem(key);
    } catch (error) {
        console.warn('Error removing from LocalStorage:', error);
    }
}

// Analytics Tracking (placeholder for future implementation)
function trackEvent(eventName, eventData = {}) {
    // Placeholder for analytics tracking
    console.log('Event tracked:', eventName, eventData);
    
    // Example: Google Analytics 4
    // if (typeof gtag !== 'undefined') {
    //     gtag('event', eventName, eventData);
    // }
}

// Performance Monitoring
function measurePerformance(name, func) {
    const startTime = performance.now();
    const result = func();
    const endTime = performance.now();
    console.log(`${name} took ${endTime - startTime} milliseconds`);
    return result;
}

// Error Handling
window.addEventListener('error', function(e) {
    console.error('Global error caught:', e.error);
    // Optionally send error to logging service
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
    // Optionally send error to logging service
});

// Export functions for use in other scripts
window.HoneyShop = {
    showToast,
    addToCart,
    updateCartCount,
    selectSize,
    selectVariant,
    increaseQuantity,
    decreaseQuantity,
    validateForm,
    addToWishlist,
    removeFromWishlist,
    showQuickView,
    getCsrfToken,
    formatCurrency,
    debounce,
    throttle,
    showLoading,
    hideLoading,
    trackEvent
};

console.log('Pure Honey Shop - All scripts initialized successfully');