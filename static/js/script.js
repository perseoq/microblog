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
})();
