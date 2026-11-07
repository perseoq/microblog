(function () {
    var path = window.location.pathname;
    var links = document.querySelectorAll('header nav a');

    for (var i = 0; i < links.length; i++) {
        var href = links[i].getAttribute('href');

        if (!href || href === '/') {
            continue;
        }

        if (path === href || path.indexOf(href + '/') === 0) {
            links[i].setAttribute('aria-current', 'page');
        }
    }

    var root = document.documentElement;
    var toggles = document.querySelectorAll('[data-theme-toggle]');

    function isDark() {
        return root.getAttribute('data-theme') === 'dark';
    }

    function render() {
        var dark = isDark();

        for (var j = 0; j < toggles.length; j++) {
            toggles[j].textContent = dark ? 'Modo claro' : 'Modo oscuro';
            toggles[j].setAttribute('aria-pressed', dark ? 'true' : 'false');
        }
    }

    function apply(theme) {
        if (theme === 'dark') {
            root.setAttribute('data-theme', 'dark');
        } else {
            root.removeAttribute('data-theme');
        }

        try {
            localStorage.setItem('theme', theme);
        } catch (error) {
            void error;
        }

        render();
    }

    for (var k = 0; k < toggles.length; k++) {
        toggles[k].addEventListener('click', function () {
            apply(isDark() ? 'light' : 'dark');
        });
    }

    render();
})();
