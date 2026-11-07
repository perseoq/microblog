(function () {
    'use strict';

    function buildEmbed(rawUrl) {
        var url = (rawUrl || '').trim();
        if (!url) {
            return null;
        }

        var youtube = url.match(/(?:youtube\.com\/(?:watch\?v=|embed\/|shorts\/)|youtu\.be\/)([A-Za-z0-9_-]{11})/);
        if (youtube) {
            return { src: 'https://www.youtube.com/embed/' + youtube[1], width: '560', height: '315' };
        }

        return null;
    }

    function escapeAttribute(value) {
        return String(value)
            .replace(/&/g, '&amp;')
            .replace(/"/g, '&quot;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
    }

    CKEDITOR.dialog.add('mediaembedDialog', function (editor) {
        return {
            title: 'Insertar video de YouTube',
            minWidth: 460,
            minHeight: 120,
            contents: [
                {
                    id: 'info',
                    label: 'URL',
                    elements: [
                        {
                            type: 'text',
                            id: 'url',
                            label: 'URL del video de YouTube',
                            width: '100%',
                            validate: CKEDITOR.dialog.validate.notEmpty('Introduce una URL.')
                        }
                    ]
                }
            ],
            onOk: function () {
                var embed = buildEmbed(this.getValueOf('info', 'url'));
                if (!embed) {
                    alert('URL de YouTube no válida.');
                    return false;
                }
                editor.insertHtml(
                    '<iframe class="media-embed" src="' + escapeAttribute(embed.src) + '" width="' + escapeAttribute(embed.width) +
                    '" height="' + escapeAttribute(embed.height) + '" loading="lazy" allowfullscreen></iframe>'
                );
            }
        };
    });

    CKEDITOR.plugins.add('mediaembed', {
        init: function (editor) {
            CKEDITOR.document.appendStyleText(
                '.cke_button__mediaembed_icon{' +
                'background-image:url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 16 16\'%3E%3Crect x=\'1.5\' y=\'2.5\' width=\'13\' height=\'11\' rx=\'2\' fill=\'none\' stroke=\'%23333\' stroke-width=\'1.4\'/%3E%3Cpath d=\'M6.8 5.8v4.4L10.6 8z\' fill=\'%23333\'/%3E%3C/svg%3E");' +
                'background-size:16px 16px;background-position:center;background-repeat:no-repeat;}'
            );

            editor.addCommand('mediaembed', {
                exec: function (editor) {
                    editor.openDialog('mediaembedDialog');
                }
            });

            editor.ui.addButton('MediaEmbed', {
                label: 'Insertar video de YouTube',
                command: 'mediaembed'
            });
        }
    });
})();
