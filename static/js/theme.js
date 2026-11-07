(function () {
    try {
        if (localStorage.getItem('theme') === 'dark') {
            document.documentElement.setAttribute('data-theme', 'dark');
        }

        if (localStorage.getItem('sidebar') === 'collapsed') {
            document.documentElement.classList.add('sidebar-collapsed');
        }
    } catch (error) {
        return;
    }
})();
