(function () {
    var path = window.location.pathname;
    var links = document.querySelectorAll('header nav a, .sidebar-nav a');

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
        var label = dark ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro';

        for (var j = 0; j < toggles.length; j++) {
            toggles[j].setAttribute('aria-pressed', dark ? 'true' : 'false');
            toggles[j].setAttribute('aria-label', label);
            toggles[j].setAttribute('title', label);
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

    var sidebar = document.getElementById('admin-sidebar');
    var sidebarToggles = document.querySelectorAll('[data-sidebar-toggle]');
    var sidebarClosers = document.querySelectorAll('[data-sidebar-close]');
    var mobileQuery = window.matchMedia('(max-width: 900px)');

    function isSidebarOpen() {
        return root.classList.contains('sidebar-open');
    }

    function updateSidebarControls() {
        var expanded = mobileQuery.matches
            ? isSidebarOpen()
            : !root.classList.contains('sidebar-collapsed');

        for (var m = 0; m < sidebarToggles.length; m++) {
            sidebarToggles[m].setAttribute('aria-expanded', expanded ? 'true' : 'false');
        }
    }

    function toggleSidebar() {
        if (!sidebar) {
            return;
        }

        if (mobileQuery.matches) {
            root.classList.toggle('sidebar-open');
        } else {
            var collapsed = root.classList.toggle('sidebar-collapsed');

            try {
                localStorage.setItem('sidebar', collapsed ? 'collapsed' : 'expanded');
            } catch (error) {
                void error;
            }
        }

        updateSidebarControls();
    }

    function closeSidebar() {
        if (root.classList.contains('sidebar-open')) {
            root.classList.remove('sidebar-open');
            updateSidebarControls();
        }
    }

    for (var n = 0; n < sidebarToggles.length; n++) {
        sidebarToggles[n].addEventListener('click', toggleSidebar);
    }

    for (var p = 0; p < sidebarClosers.length; p++) {
        sidebarClosers[p].addEventListener('click', closeSidebar);
    }

    var sidebarLinks = document.querySelectorAll('.sidebar-nav a, .sidebar-footer a');

    for (var q = 0; q < sidebarLinks.length; q++) {
        sidebarLinks[q].addEventListener('click', closeSidebar);
    }

    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape') {
            closeSidebar();
        }
    });

    if (typeof mobileQuery.addEventListener === 'function') {
        mobileQuery.addEventListener('change', function () {
            closeSidebar();
            updateSidebarControls();
        });
    }

    updateSidebarControls();
})();
