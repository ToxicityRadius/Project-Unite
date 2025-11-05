# TODO: Implement Show/Hide Password Functionality

## Steps to Complete

- [ ] Update `SyncHub/SyncHub/templates/partials/auth_modal.html`: Remove existing `pw_hide` icons and add new `fa-eye-slash` icons next to each password input (signup_password, confirm_password, login_password).
- [ ] Update `SyncHub/static/js/main.js`: Remove existing password toggle logic and add new clean toggle function that switches between `fa-eye-slash` (hide) and `fa-eye` (show), toggling input type and ensuring accessibility.
- [ ] Test the functionality: Open the auth modal and verify clicking the icons toggles password visibility correctly.
