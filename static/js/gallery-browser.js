(function () {
    var params = new URLSearchParams(window.location.search);
    var funcNum = params.get('CKEditorFuncNum');
    var filter = document.querySelector('[data-browser-filter]');
    var items = document.querySelectorAll('.browser-item');
    var albums = document.querySelectorAll('.browser-album');
    var empty = document.querySelector('[data-browser-empty]');

    document.querySelectorAll('.browser-image').forEach(function (button) {
        button.addEventListener('click', function () {
            if (!funcNum || !window.opener || window.opener.closed) {
                return;
            }

            window.opener.CKEDITOR.tools.callFunction(funcNum, button.getAttribute('data-url'));
            window.close();
        });
    });

    if (filter) {
        filter.addEventListener('input', function () {
            var term = filter.value.trim().toLowerCase();
            var visible = 0;

            items.forEach(function (item) {
                var album = item.getAttribute('data-album') || '';
                var match = !term || album.indexOf(term) !== -1;
                item.hidden = !match;

                if (match) {
                    visible++;
                }
            });

            albums.forEach(function (album) {
                album.hidden = !album.querySelector('.browser-item:not([hidden])');
            });

            if (empty) {
                empty.hidden = visible !== 0;
            }
        });
    }
})();
