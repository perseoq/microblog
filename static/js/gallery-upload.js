(function () {
    var input = document.querySelector('.file-input');
    var preview = document.querySelector('[data-upload-preview]');
    var counter = document.querySelector('[data-upload-count]');
    var drop = document.querySelector('[data-file-drop]');

    if (!input || !preview || typeof DataTransfer === 'undefined') {
        return;
    }

    var files = [];

    function formatSize(bytes) {
        if (bytes < 1024) {
            return bytes + ' B';
        }
        if (bytes < 1048576) {
            return Math.round(bytes / 1024) + ' KB';
        }
        return (bytes / 1048576).toFixed(1) + ' MB';
    }

    function sync() {
        var transfer = new DataTransfer();

        files.forEach(function (file) {
            transfer.items.add(file);
        });

        input.files = transfer.files;
        preview.innerHTML = '';

        files.forEach(function (file, index) {
            var item = document.createElement('li');
            item.className = 'upload-preview-item';

            var thumb = document.createElement('img');
            thumb.src = URL.createObjectURL(file);
            thumb.alt = '';
            thumb.addEventListener('load', function () {
                URL.revokeObjectURL(thumb.src);
            });

            var info = document.createElement('span');
            info.className = 'upload-preview-info';

            var name = document.createElement('span');
            name.className = 'upload-preview-name';
            name.textContent = file.name;

            var size = document.createElement('span');
            size.className = 'upload-preview-size';
            size.textContent = formatSize(file.size);

            info.appendChild(name);
            info.appendChild(size);

            var remove = document.createElement('button');
            remove.type = 'button';
            remove.className = 'upload-preview-remove';
            remove.setAttribute('aria-label', 'Quitar ' + file.name);
            remove.innerHTML = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12"></path></svg>';
            remove.addEventListener('click', function () {
                files.splice(index, 1);
                sync();
            });

            item.appendChild(thumb);
            item.appendChild(info);
            item.appendChild(remove);
            preview.appendChild(item);
        });

        counter.textContent = files.length
            ? files.length + ' imagen(es) seleccionada(s)'
            : '';
    }

    function setFiles(list) {
        files = [];

        Array.prototype.forEach.call(list, function (file) {
            if (file.type.indexOf('image/') === 0) {
                files.push(file);
            }
        });

        sync();
    }

    input.addEventListener('change', function () {
        setFiles(input.files);
    });

    if (drop) {
        ['dragenter', 'dragover'].forEach(function (name) {
            drop.addEventListener(name, function (event) {
                event.preventDefault();
                drop.classList.add('is-dragging');
            });
        });

        ['dragleave', 'drop'].forEach(function (name) {
            drop.addEventListener(name, function (event) {
                event.preventDefault();
                drop.classList.remove('is-dragging');
            });
        });

        drop.addEventListener('drop', function (event) {
            if (event.dataTransfer && event.dataTransfer.files.length) {
                setFiles(event.dataTransfer.files);
            }
        });
    }
})();
