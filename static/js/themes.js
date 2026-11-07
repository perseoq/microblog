(function () {
    var filter = document.querySelector('[data-theme-filter]');
    var cards = document.querySelectorAll('.theme-card');
    var empty = document.querySelector('[data-theme-empty]');

    if (!filter) {
        return;
    }

    filter.addEventListener('input', function () {
        var term = filter.value.trim().toLowerCase();
        var visible = 0;

        cards.forEach(function (card) {
            var name = card.getAttribute('data-name') || '';
            var match = !term || name.indexOf(term) !== -1;
            card.hidden = !match;

            if (match) {
                visible++;
            }
        });

        if (empty) {
            empty.hidden = visible !== 0;
        }
    });
})();
