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

    var searchInput = document.querySelector('[data-search-input]');

    if (searchInput) {
        var searchForm = searchInput.closest('form');
        var suggestUrl = searchForm ? searchForm.getAttribute('data-search-url') : null;
        var suggestionList = document.createElement('ul');
        var suggestions = [];
        var activeIndex = -1;
        var suggestTimer = null;

        suggestionList.className = 'search-suggestions';
        suggestionList.setAttribute('role', 'listbox');
        suggestionList.hidden = true;
        searchInput.parentNode.appendChild(suggestionList);

        function closeSuggestions() {
            suggestionList.hidden = true;
            suggestionList.innerHTML = '';
            suggestions = [];
            activeIndex = -1;
            searchInput.setAttribute('aria-expanded', 'false');
        }

        function chooseSuggestion(index) {
            if (index < 0 || index >= suggestions.length) {
                return;
            }

            searchInput.value = suggestions[index];
            closeSuggestions();

            if (searchForm) {
                searchForm.submit();
            }
        }

        function highlightSuggestions(items) {
            for (var v = 0; v < items.length; v++) {
                items[v].setAttribute('aria-selected', v === activeIndex ? 'true' : 'false');
            }
        }

        function renderSuggestions() {
            suggestionList.innerHTML = '';

            if (!suggestions.length) {
                closeSuggestions();
                return;
            }

            suggestions.forEach(function (value, index) {
                var item = document.createElement('li');
                item.className = 'search-suggestion';
                item.setAttribute('role', 'option');
                item.textContent = value;
                item.addEventListener('mousedown', function (event) {
                    event.preventDefault();
                    chooseSuggestion(index);
                });
                suggestionList.appendChild(item);
            });

            suggestionList.hidden = false;
            searchInput.setAttribute('aria-expanded', 'true');
            activeIndex = -1;
        }

        function loadSuggestions(value) {
            if (!suggestUrl || value.length < 2) {
                closeSuggestions();
                return;
            }

            fetch(suggestUrl + '?q=' + encodeURIComponent(value))
                .then(function (response) {
                    return response.json();
                })
                .then(function (data) {
                    suggestions = Array.isArray(data) ? data : [];
                    renderSuggestions();
                })
                .catch(function () {
                    closeSuggestions();
                });
        }

        searchInput.addEventListener('input', function () {
            clearTimeout(suggestTimer);
            var value = searchInput.value.trim();
            suggestTimer = setTimeout(function () {
                loadSuggestions(value);
            }, 180);
        });

        searchInput.addEventListener('keydown', function (event) {
            if (suggestionList.hidden) {
                return;
            }

            var items = suggestionList.querySelectorAll('.search-suggestion');

            if (event.key === 'ArrowDown') {
                event.preventDefault();
                activeIndex = Math.min(activeIndex + 1, items.length - 1);
                highlightSuggestions(items);
            } else if (event.key === 'ArrowUp') {
                event.preventDefault();
                activeIndex = Math.max(activeIndex - 1, 0);
                highlightSuggestions(items);
            } else if (event.key === 'Enter' && activeIndex >= 0) {
                event.preventDefault();
                chooseSuggestion(activeIndex);
            } else if (event.key === 'Escape') {
                closeSuggestions();
            }
        });

        searchInput.addEventListener('blur', function () {
            setTimeout(closeSuggestions, 120);
        });
    }
})();
