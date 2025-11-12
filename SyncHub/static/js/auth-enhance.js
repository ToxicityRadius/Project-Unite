(function(){
  if (window.__authEnhanceInitialized) return;
  window.__authEnhanceInitialized = true;

  document.addEventListener('DOMContentLoaded', function() {
    var pw1 = document.getElementById('id_new_password1');
    var pw2 = document.getElementById('id_new_password2');

    if (pw1) {
      pw1.classList.add('figma-input');
      pw1.classList.add('auth-input');
      if (!pw1.getAttribute('placeholder')) pw1.setAttribute('placeholder', 'New password');
      pw1.setAttribute('aria-label', 'New password');
      pw1.setAttribute('autocomplete', 'new-password');
    }

    if (pw2) {
      pw2.classList.add('figma-input');
      pw2.classList.add('auth-input');
      pw2.setAttribute('placeholder', 'Confirm your New Password');
      pw2.setAttribute('aria-label', 'Confirm your New Password');
      pw2.setAttribute('autocomplete', 'new-password');
    }

    function toggleInputVisibility(icon) {
      if (!icon) return;
      var wrapper = icon.closest ? icon.closest('.input_box') : null;
      var input = wrapper ? wrapper.querySelector('input') : null;
      if (!input) return;
      if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
        icon.setAttribute('aria-label', 'Hide password');
      } else {
        input.type = 'password';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
        icon.setAttribute('aria-label', 'Show password');
      }
    }

    document.addEventListener('click', function(e) {
      var target = e.target;
      var icon = target.closest && target.closest('.toggle-password');
      if (icon) {
        e.preventDefault();
        toggleInputVisibility(icon);
      }
    });

    document.addEventListener('keydown', function(e) {
      var isToggleKey = e.key === 'Enter' || e.key === ' ';
      if (!isToggleKey) return;
      var icon = e.target.closest && e.target.closest('.toggle-password');
      if (icon) {
        e.preventDefault();
        toggleInputVisibility(icon);
      }
    });
  });
})();
