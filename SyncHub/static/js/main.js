// PROJECT UNITE - Main JavaScript

// Smooth scroll for anchor links
function initSmoothScroll() {
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
}

// Form enhancements
function initFormEnhancements() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input');
        const submitButton = form.querySelector('button[type="submit"]');
        
        // Add input focus effects
        inputs.forEach(input => {
            input.addEventListener('focus', function() {
                this.parentElement.classList.add('focused');
                this.style.transform = 'scale(1.02)';
                this.style.borderColor = 'var(--primary-blue)';
            });
            
            input.addEventListener('blur', function() {
                this.parentElement.classList.remove('focused');
                this.style.transform = 'scale(1)';
                this.style.borderColor = 'var(--border-color)';
            });
            
            // Real-time validation feedback
            input.addEventListener('input', function() {
                if (this.value.trim() !== '') {
                    this.classList.add('has-value');
                } else {
                    this.classList.remove('has-value');
                }
            });
        });
        
        // Form submission with loading state
        form.addEventListener('submit', function(e) {
            if (submitButton) {
                const originalText = submitButton.textContent;
                submitButton.textContent = 'Processing...';
                submitButton.disabled = true;
                
                // Re-enable after 3 seconds if form hasn't redirected
                setTimeout(() => {
                    submitButton.textContent = originalText;
                    submitButton.disabled = false;
                }, 3000);
            }
        });
    });
}

// Card animations
function initCardAnimations() {
    const cards = document.querySelectorAll('.dashboard-card');
    
    cards.forEach((card, index) => {
        // Stagger entrance animation
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.6s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 200 + 300);
        
        // Enhanced hover effects
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px) scale(1.03)';
            this.style.boxShadow = '0 20px 40px rgba(0, 120, 255, 0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
            this.style.boxShadow = '0 10px 30px rgba(0, 120, 255, 0.1)';
        });
        
        // Make entire card clickable
        card.addEventListener('click', function(e) {
            if (e.target.tagName !== 'A') {
                const link = this.querySelector('.card-button');
                if (link) {
                    // Add click animation
                    this.style.transform = 'scale(0.95)';
                    setTimeout(() => {
                        this.style.transform = 'scale(1)';
                        link.click();
                    }, 150);
                }
            }
        });
    });
}

// Navigation enhancements
function initNavigation() {
    const navLinks = document.querySelectorAll('.nav-links a');
    
    navLinks.forEach(link => {
        link.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        link.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

// Button enhancements
function initButtonEnhancements() {
    const buttons = document.querySelectorAll('.cta-button, .card-button, .login-button');
    
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-3px) scale(1.05)';
            this.style.boxShadow = '0 8px 25px rgba(0, 120, 255, 0.3)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
            this.style.boxShadow = 'none';
        });
        
        button.addEventListener('mousedown', function() {
            this.style.transform = 'translateY(0) scale(0.95)';
        });
        
        button.addEventListener('mouseup', function() {
            this.style.transform = 'translateY(-3px) scale(1.05)';
        });
    });
}

// Intersection Observer for scroll animations
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, observerOptions);
    
    // Observe elements that should animate on scroll
    document.querySelectorAll('.dashboard-card, .login-card, .landing-container').forEach(el => {
        observer.observe(el);
    });
}

// Initialize all enhancements when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initSmoothScroll();
    initFormEnhancements();
    initCardAnimations();
    initNavigation();
    initButtonEnhancements();
    initScrollAnimations();
    
    // Add global fade-in to body
    document.body.style.opacity = '0';
    setTimeout(() => {
        document.body.style.transition = 'opacity 0.5s ease';
        document.body.style.opacity = '1';
    }, 100);
});

// Handle browser back/forward navigation
window.addEventListener('pageshow', function(event) {
    if (event.persisted) {
        // Page was loaded from cache, reinitialize animations
        initCardAnimations();
    }
});

// Export functions for use in other scripts
window.ProjectUnite = {
    initSmoothScroll,
    initFormEnhancements,
    initCardAnimations,
    initNavigation,
    initButtonEnhancements,
    initScrollAnimations
};

// --- Auth modal and form validation logic (enhanced) ---
document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const home = document.querySelector('.home');
    const formContainer = document.querySelector('.form_container');
    const formCloseBtn = document.querySelector('.form_close');
    const signupBtn = document.querySelector('#signup');
    const loginBtn = document.querySelector('#login');
    const openLoginBtn = document.getElementById('openLogin');
    const openSignupBtn = document.getElementById('openSignup');
    const logoutBtn = document.getElementById('logoutBtn');
    const pwShowHideIcons = document.querySelectorAll('.pw_hide');

    const profileInfo = document.getElementById('profile-info');
    const navAvatarImg = document.getElementById('nav-avatar-img');
    const navUsernameDisplay = document.getElementById('nav-username-display');

    function togglePasswordIcon(icon) {
        const input = icon.parentElement.querySelector('input') || icon.previousElementSibling;
        if (!input) return;
        if (input.type === 'password') {
            input.type = 'text';
            icon.textContent = '🙈';
        } else {
            input.type = 'password';
            icon.textContent = '👁️';
        }
    }

    pwShowHideIcons.forEach(icon => {
        icon.addEventListener('click', () => togglePasswordIcon(icon));
        icon.addEventListener('keydown', e => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                togglePasswordIcon(icon);
            }
        });
    });

    function setFocusToFirstInput(formSelector) {
        const form = document.querySelector(formSelector);
        if (!form) return;
        const firstInput = form.querySelector('input, button, select, textarea, [tabindex]:not([tabindex="-1"])');
        if (firstInput) firstInput.focus();
    }

    function showError(input, message) {
        if (!input) return;
        let errorElem = input.parentElement.querySelector('.error-message');
        if (!errorElem) {
            errorElem = document.createElement('div');
            errorElem.className = 'error-message';
            input.parentElement.appendChild(errorElem);
        }
        errorElem.textContent = message;
        input.setAttribute('aria-invalid', 'true');
    }

    function clearError(input) {
        if (!input) return;
        const errorElem = input.parentElement.querySelector('.error-message');
        if (errorElem) errorElem.textContent = '';
        input.removeAttribute('aria-invalid');
    }

    function isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    function isStrongPassword(password) {
        const re = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$/;
        return re.test(password);
    }

    function toggleAuthButtons() {
        if (localStorage.getItem('loggedIn') === 'true') {
            if (openLoginBtn) openLoginBtn.style.display = 'none';
            if (openSignupBtn) openSignupBtn.style.display = 'none';
            if (logoutBtn) logoutBtn.style.display = 'inline-block';
            if (profileInfo) profileInfo.style.display = 'flex';
            if (navAvatarImg) {
                const avatar = localStorage.getItem('avatar') || '';
                if (avatar) {
                    navAvatarImg.src = avatar; navAvatarImg.style.display = 'block';
                }
            }
            if (navUsernameDisplay) {
                const username = localStorage.getItem('username') || localStorage.getItem('email') || 'User';
                navUsernameDisplay.textContent = username;
            }
        } else {
            if (openLoginBtn) openLoginBtn.style.display = 'inline-block';
            if (openSignupBtn) openSignupBtn.style.display = 'inline-block';
            if (logoutBtn) logoutBtn.style.display = 'none';
            if (profileInfo) profileInfo.style.display = 'none';
            if (navAvatarImg) { navAvatarImg.src = ''; navAvatarImg.style.display = 'none'; }
            if (navUsernameDisplay) navUsernameDisplay.textContent = '';
        }
    }

    toggleAuthButtons();

    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            localStorage.removeItem('loggedIn');
            localStorage.removeItem('username');
            localStorage.removeItem('avatar');
            localStorage.removeItem('email');
            toggleAuthButtons();
            window.location.href = '/';
        });
    }

    if (openSignupBtn) {
        openSignupBtn.addEventListener('click', e => {
            e.preventDefault();
            if (home) home.style.display = 'flex';
            if (formContainer) formContainer.classList.add('active');
            document.querySelector('.login_form').setAttribute('aria-hidden', 'true');
            document.querySelector('.signup_form').setAttribute('aria-hidden', 'false');
            // hide login prompt when viewing signup
            const loginPrompt = document.getElementById('login_signup_prompt');
            if (loginPrompt) loginPrompt.classList.add('hidden');
            setFocusToFirstInput('.signup_form');
        });
    }

    if (openLoginBtn) {
        openLoginBtn.addEventListener('click', e => {
            e.preventDefault();
            if (home) home.style.display = 'flex';
            if (formContainer) formContainer.classList.remove('active');
            document.querySelector('.login_form').setAttribute('aria-hidden', 'false');
            document.querySelector('.signup_form').setAttribute('aria-hidden', 'true');
            // show prompt to sign up if user hasn't registered
            const loginPrompt = document.getElementById('login_signup_prompt');
            try {
                if (loginPrompt) {
                    if (localStorage.getItem('registered') !== 'true') loginPrompt.classList.remove('hidden');
                    else loginPrompt.classList.add('hidden');
                }
            } catch (e) {}
            setFocusToFirstInput('.login_form');
        });
    }

    if (signupBtn) {
        signupBtn.addEventListener('click', e => {
            e.preventDefault();
            if (formContainer) formContainer.classList.add('active');
            document.querySelector('.login_form').setAttribute('aria-hidden', 'true');
            document.querySelector('.signup_form').setAttribute('aria-hidden', 'false');
            setFocusToFirstInput('.signup_form');
        });
    }

    if (loginBtn) {
        loginBtn.addEventListener('click', e => {
            e.preventDefault();
            if (formContainer) formContainer.classList.remove('active');
            document.querySelector('.login_form').setAttribute('aria-hidden', 'false');
            document.querySelector('.signup_form').setAttribute('aria-hidden', 'true');
            setFocusToFirstInput('.login_form');
        });
    }

    if (formCloseBtn) {
        formCloseBtn.addEventListener('click', () => {
            if (home) home.style.display = 'none';
            if (openLoginBtn) openLoginBtn.focus();
        });
    }

    // Close modal if clicking outside the form_container (overlay click)
    if (home) {
        home.addEventListener('click', (e) => {
            // If the click target is the overlay itself (not inside the form), close
            if (e.target === home) {
                home.style.display = 'none';
                if (openLoginBtn) openLoginBtn.focus();
            }
        });
    }

    // Prevent clicks inside the form container from bubbling to the overlay
    if (formContainer) {
        formContainer.addEventListener('click', (e) => {
            e.stopPropagation();
        });
    }

    // link in login form to open signup
    const goToSignup = document.getElementById('goToSignup');
    if (goToSignup) {
        goToSignup.addEventListener('click', (e) => {
            e.preventDefault();
            if (formContainer) formContainer.classList.add('active');
            document.querySelector('.login_form').setAttribute('aria-hidden', 'true');
            document.querySelector('.signup_form').setAttribute('aria-hidden', 'false');
            const loginPrompt = document.getElementById('login_signup_prompt');
            if (loginPrompt) loginPrompt.classList.add('hidden');
            setFocusToFirstInput('.signup_form');
        });
    }

    window.addEventListener('keydown', e => {
        if ((e.key === 'Escape' || e.key === 'Esc') && home && home.style.display !== 'none') {
            home.style.display = 'none';
            if (openLoginBtn) openLoginBtn.focus();
        }
    });

    // Signup form submission
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        signupForm.addEventListener('submit', e => {
            e.preventDefault();
            const usernameInput = document.getElementById('signup_username');
            const emailInput = document.getElementById('signup_email');
            const passwordInput = document.getElementById('signup_password');
            const confirmPasswordInput = document.getElementById('confirm_password');

            let valid = true;
            clearError(usernameInput); clearError(emailInput); clearError(passwordInput); clearError(confirmPasswordInput);

            if (usernameInput.value.trim() === '') { showError(usernameInput, 'Please enter a username.'); valid = false; }
            if (!isValidEmail(emailInput.value.trim())) { showError(emailInput, 'Please enter a valid email address.'); valid = false; }
            if (!isStrongPassword(passwordInput.value.trim())) { showError(passwordInput, 'Password must be at least 8 characters long and include at least one letter and one number.'); valid = false; }
            if (passwordInput.value.trim() !== confirmPasswordInput.value.trim()) { showError(confirmPasswordInput, 'Passwords do not match.'); valid = false; }

            if (valid) {
                const submitBtn = signupForm.querySelector('button[type="submit"]');
                submitBtn.disabled = true; submitBtn.textContent = 'Signing up...';
                fetch('/api/signup', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username: usernameInput.value.trim(), email: emailInput.value.trim(), password: passwordInput.value.trim() })
                })
                .then(res => res.json().then(data => ({status: res.status, body: data})))
                .then(({status, body}) => {
                    alert(body.message);
                    if (status === 200) {
                        // mark registered locally
                        try { localStorage.setItem('registered', 'true'); } catch (e) {}

                        document.querySelector('.signup_form').setAttribute('aria-hidden', 'true');
                        document.querySelector('.login_form').setAttribute('aria-hidden', 'false');
                        if (formContainer) formContainer.classList.remove('active');
                        if (home) home.style.display = 'none';
                        const identifierInput = document.getElementById('login_identifier');
                        const passwordInputLogin = document.getElementById('login_password');
                        if (identifierInput) identifierInput.value = usernameInput.value.trim();
                        if (passwordInputLogin) passwordInputLogin.value = passwordInput.value.trim();
                        if (identifierInput) identifierInput.focus();
                    }
                    submitBtn.disabled = false; submitBtn.textContent = 'Sign Up Now';
                })
                .catch(err => { alert('Error: ' + err.message); submitBtn.disabled = false; submitBtn.textContent = 'Sign Up Now'; });
            }
        });
    }

    // Login form submission
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', e => {
            e.preventDefault();
            const identifierInput = document.getElementById('login_identifier');
            const passwordInput = document.getElementById('login_password');

            let valid = true;
            clearError(identifierInput); clearError(passwordInput);
            if (identifierInput.value.trim() === '') { showError(identifierInput, 'Please enter your username or email.'); valid = false; }
            if (passwordInput.value.trim() === '') { showError(passwordInput, 'Please enter your password.'); valid = false; }

            if (valid) {
                const submitBtn = loginForm.querySelector('button[type="submit"]');
                submitBtn.disabled = true; submitBtn.textContent = 'Logging in...';
                fetch('/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ identifier: identifierInput.value.trim(), password: passwordInput.value.trim() })
                })
                .then(res => res.json().then(data => ({status: res.status, body: data})))
                .then(({status, body}) => {
                    alert(body.message);
                    if (status === 200) {
                        if (home) home.style.display = 'none';
                        localStorage.setItem('loggedIn', 'true');
                        const identifier = identifierInput.value.trim();
                        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                        if (emailRegex.test(identifier)) { localStorage.setItem('email', identifier); localStorage.removeItem('username'); }
                        else { localStorage.setItem('username', identifier); localStorage.removeItem('email'); }
                        toggleAuthButtons();
                        // Redirect to dashboard
                        window.location.href = '/dashboard/';
                    }
                    submitBtn.disabled = false; submitBtn.textContent = 'Login Now';
                })
                .catch(err => { alert('Error: ' + err.message); submitBtn.disabled = false; submitBtn.textContent = 'Login Now'; });
            }
        });
    }
});
