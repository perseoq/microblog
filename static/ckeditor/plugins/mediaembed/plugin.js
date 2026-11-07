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

        var spotify = url.match(/open\.spotify\.com\/(?:embed\/)?(track|album|playlist|episode|show|artist)\/([A-Za-z0-9]+)/);
        if (spotify) {
            return { src: 'https://open.spotify.com/embed/' + spotify[1] + '/' + spotify[2], width: '100%', height: '352' };
        }

        var instagram = url.match(/instagram\.com\/(p|reel|tv)\/([A-Za-z0-9_-]+)/);
        if (instagram) {
            return { src: 'https://www.instagram.com/' + instagram[1] + '/' + instagram[2] + '/embed', width: '400', height: '480' };
        }

        var vimeo = url.match(/vimeo\.com\/(\d+)/);
        if (vimeo) {
            return { src: 'https://player.vimeo.com/video/' + vimeo[1], width: '560', height: '315' };
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
            title: 'Insertar YouTube, Spotify o Instagram',
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
                            label: 'URL del video, pista o publicación',
                            width: '100%',
                            validate: CKEDITOR.dialog.validate.notEmpty('Introduce una URL.')
                        }
                    ]
                }
            ],
            onOk: function () {
                var embed = buildEmbed(this.getValueOf('info', 'url'));
                if (!embed) {
                    alert('URL no compatible. Usa YouTube, Spotify, Instagram o Vimeo.');
                    return false;
                }
                editor.insertHtml(
                    '<iframe src="' + escapeAttribute(embed.src) + '" width="' + escapeAttribute(embed.width) +
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
                label: 'Insertar YouTube, Spotify o Instagram',
                command: 'mediaembed'
            });
        }
    });
})();
