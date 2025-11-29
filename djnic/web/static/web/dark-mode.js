document.addEventListener('DOMContentLoaded', function () {
  function setDarkMode(on) {
    if (on) {
      document.body.classList.add('dark-mode');
      localStorage.setItem('darkMode', 'on');
    } else {
      document.body.classList.remove('dark-mode');
      localStorage.setItem('darkMode', 'off');
    }
  }
  // On load, default to dark unless explicitly off
  if (localStorage.getItem('darkMode') !== 'off') {
    setDarkMode(true);
  }
  var btn = document.getElementById('darkModeToggle');
  if (btn) {
    btn.onclick = function (e) {
      e.preventDefault();
      setDarkMode(!document.body.classList.contains('dark-mode'));
    };
  }
});
