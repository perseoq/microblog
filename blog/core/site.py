from blog.arch.models import SiteConfig
from blog.core.extensions import db

DEFAULT_TITLE = 'microblog'
DEFAULT_DESCRIPTION = 'Ideas, notas y tutoriales sobre desarrollo, diseño y tecnología.'
DEFAULT_FOOTER = '© microblog'


def get_site_config():
    config = SiteConfig.query.first()
    if config is None:
        config = SiteConfig(
            site_title=DEFAULT_TITLE,
            site_description=DEFAULT_DESCRIPTION,
            footer_text=DEFAULT_FOOTER,
        )
        db.session.add(config)
        db.session.commit()
    return config
