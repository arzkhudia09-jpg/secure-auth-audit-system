/**
 * Secure Authentication Demo - Frontend JavaScript
 * Frontend interactions only - no backend security logic
 * Password validation, UI animations, and form interactions
 */

function togglePasswordVisibility(button) {
    const passwordField = document.getElementById('password');
    if (!passwordField || !button) {
        return;
    }

    if (passwordField.type === 'password') {
        passwordField.type = 'text';
        button.textContent = '🙈';
    } else {
        passwordField.type = 'password';
        button.textContent = '👁️';
    }
}

function toggleConfirmPasswordVisibility(button) {
    const confirmPasswordField = document.getElementById('confirm-password');
    if (!confirmPasswordField || !button) {
        return;
    }

    if (confirmPasswordField.type === 'password') {
        confirmPasswordField.type = 'text';
        button.textContent = '🙈';
    } else {
        confirmPasswordField.type = 'password';
        button.textContent = '👁️';
    }
}

function updatePasswordStrength() {
    const password = document.getElementById('password')?.value || '';
    const strengthBars = [
        document.getElementById('strengthBar1'),
        document.getElementById('strengthBar2'),
        document.getElementById('strengthBar3'),
        document.getElementById('strengthBar4'),
    ];
    const strengthText = document.getElementById('strengthText');

    strengthBars.forEach(bar => {
        if (bar) {
            bar.className = 'strength-bar';
        }
    });

    const hasMinLength = password.length >= 8;
    const hasUppercase = /[A-Z]/.test(password);
    const hasLowercase = /[a-z]/.test(password);
    const hasNumber = /[0-9]/.test(password);
    const hasSpecialChar = /[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/.test(password);

    const metRequirements = [hasMinLength, hasUppercase, hasLowercase, hasNumber, hasSpecialChar].filter(Boolean).length;

    if (strengthBars[0]) strengthBars[0].classList.add(metRequirements >= 1 ? 'weak' : '');
    if (strengthBars[1]) strengthBars[1].classList.add(metRequirements >= 2 ? 'fair' : '');
    if (strengthBars[2]) strengthBars[2].classList.add(metRequirements >= 3 ? 'good' : '');
    if (strengthBars[3]) strengthBars[3].classList.add(metRequirements >= 4 ? 'strong' : '');

    if (strengthText) {
        if (password.length === 0) {
            strengthText.textContent = 'Password strength: -';
        } else if (metRequirements <= 2) {
            strengthText.textContent = 'Password strength: Weak ⚠️';
        } else if (metRequirements === 3) {
            strengthText.textContent = 'Password strength: Fair ℹ️';
        } else if (metRequirements === 4) {
            strengthText.textContent = 'Password strength: Good ✓';
        } else {
            strengthText.textContent = 'Password strength: Strong 🔒';
        }
    }

    updatePolicyChecklist(hasMinLength, hasUppercase, hasLowercase, hasNumber, hasSpecialChar);
}

function updatePolicyChecklist(hasMinLength, hasUppercase, hasLowercase, hasNumber, hasSpecialChar) {
    const policyMap = [
        { id: 'minLength', condition: hasMinLength },
        { id: 'uppercase', condition: hasUppercase },
        { id: 'lowercase', condition: hasLowercase },
        { id: 'number', condition: hasNumber },
        { id: 'special', condition: hasSpecialChar },
    ];

    policyMap.forEach(policy => {
        const item = document.getElementById(policy.id);
        if (!item) return;
        const check = item.querySelector('.policy-check');
        if (policy.condition) {
            item.classList.add('met');
            if (check) check.textContent = '✓';
        } else {
            item.classList.remove('met');
            if (check) check.textContent = '○';
        }
    });
}

function checkPasswordMatch() {
    const password = document.getElementById('password')?.value || '';
    const confirmPassword = document.getElementById('confirm-password')?.value || '';
    const passwordMatchHint = document.getElementById('passwordMatchHint');
    const confirmPasswordField = document.getElementById('confirm-password');

    if (!confirmPasswordField || !passwordMatchHint) {
        return;
    }

    if (confirmPassword.length === 0) {
        confirmPasswordField.style.borderColor = '';
        passwordMatchHint.textContent = 'Passwords must match';
        passwordMatchHint.style.color = '';
        return;
    }

    if (password === confirmPassword) {
        confirmPasswordField.style.borderColor = 'var(--success-color)';
        passwordMatchHint.textContent = '✓ Passwords match';
        passwordMatchHint.style.color = 'var(--success-color)';
    } else {
        confirmPasswordField.style.borderColor = 'var(--alert-color)';
        passwordMatchHint.textContent = '✗ Passwords do not match';
        passwordMatchHint.style.color = 'var(--alert-color)';
    }
}

function validateLoginForm() {
    const identifier = document.getElementById('identifier')?.value.trim() || '';
    const password = document.getElementById('password')?.value || '';
    if (identifier.length < 3) {
        showAlert('Please enter your username or email.', 'error');
        return false;
    }
    if (password.length === 0) {
        showAlert('Please enter your password.', 'error');
        return false;
    }
    return true;
}

function validateRegisterForm() {
    const username = document.getElementById('username')?.value.trim() || '';
    const email = document.getElementById('email')?.value.trim() || '';
    const password = document.getElementById('password')?.value || '';
    const confirmPassword = document.getElementById('confirm-password')?.value || '';
    const termsChecked = document.getElementById('terms')?.checked;
    const privacyChecked = document.getElementById('privacy')?.checked;

    if (username.length < 3 || !/^[A-Za-z0-9_]+$/.test(username)) {
        showAlert('Username must be 3-20 characters and may use letters, numbers, and underscores.', 'error');
        return false;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        showAlert('Please enter a valid email address.', 'error');
        return false;
    }

    const hasMinLength = password.length >= 8;
    const hasUppercase = /[A-Z]/.test(password);
    const hasLowercase = /[a-z]/.test(password);
    const hasNumber = /[0-9]/.test(password);
    const hasSpecialChar = /[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/.test(password);

    if (!hasMinLength || !hasUppercase || !hasLowercase || !hasNumber || !hasSpecialChar) {
        showAlert('Password does not meet all security requirements.', 'error');
        return false;
    }

    if (password !== confirmPassword) {
        showAlert('Passwords do not match.', 'error');
        return false;
    }

    if (!termsChecked || !privacyChecked) {
        showAlert('You must agree to the Terms of Service and Privacy Policy.', 'error');
        return false;
    }

    return true;
}

function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.style.position = 'fixed';
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.maxWidth = '400px';
    alertDiv.style.zIndex = '9999';

    const icons = {
        error: '❌',
        success: '✅',
        warning: '⚠️',
        info: 'ℹ️',
    };

    alertDiv.innerHTML = `
        <span class="alert-icon">${icons[type] || icons.info}</span>
        <span>${message}</span>
    `;

    document.body.appendChild(alertDiv);

    setTimeout(() => {
        alertDiv.style.animation = 'fadeOut 0.3s ease-out forwards';
        setTimeout(() => alertDiv.remove(), 300);
    }, 5000);
}

document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.querySelector('.login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            if (!validateLoginForm()) {
                e.preventDefault();
            }
        });
    }

    const registerForm = document.querySelector('.register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            if (!validateRegisterForm()) {
                e.preventDefault();
            }
        });
    }

    const passwordField = document.getElementById('password');
    if (passwordField) {
        passwordField.addEventListener('input', updatePasswordStrength);
    }

    const confirmPasswordField = document.getElementById('confirm-password');
    if (confirmPasswordField) {
        confirmPasswordField.addEventListener('input', checkPasswordMatch);
    }
});
