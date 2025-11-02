// Form validation and enhancements
document.addEventListener('DOMContentLoaded', function() {
    // Add loading states to buttons
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.innerHTML = 'Processing...';
                submitButton.disabled = true;
            }
        });
    });

    // SIN validation (basic format check)
    const sinInput = document.getElementById('sin');
    if (sinInput) {
        sinInput.addEventListener('blur', function() {
            const sin = this.value.trim();
            if (sin.length < 3) {
                showFieldError(this, 'SIN must be at least 3 characters long');
            } else {
                clearFieldError(this);
            }
        });
    }

    // Email validation
    const emailInput = document.getElementById('email');
    if (emailInput) {
        emailInput.addEventListener('blur', function() {
            const email = this.value.trim();
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            
            if (email && !emailRegex.test(email)) {
                showFieldError(this, 'Please enter a valid email address');
            } else {
                clearFieldError(this);
            }
        });
    }

    // Phone number validation
    const phoneInput = document.getElementById('phone_number');
    if (phoneInput) {
        phoneInput.addEventListener('blur', function() {
            const phone = this.value.trim();
            const phoneRegex = /^\+?[\d\s-()]{10,}$/;
            
            if (phone && !phoneRegex.test(phone)) {
                showFieldError(this, 'Please enter a valid phone number');
            } else {
                clearFieldError(this);
            }
        });
    }
});

function showFieldError(field, message) {
    clearFieldError(field);
    field.style.borderColor = '#dc3545';
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.style.color = '#dc3545';
    errorDiv.style.fontSize = '0.875em';
    errorDiv.style.marginTop = '5px';
    errorDiv.textContent = message;
    
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(field) {
    field.style.borderColor = '';
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
}