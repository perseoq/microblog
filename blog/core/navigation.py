from blog.arch.models import Category, Page, Tag


def sidebar_nav():
    return {
        'categories': Category.query.order_by(Category.name).all(),
        'tags': Tag.query.order_by(Tag.name).all(),
        'pages': Page.query.filter_by(status='published').order_by(Page.title).all(),
    }
