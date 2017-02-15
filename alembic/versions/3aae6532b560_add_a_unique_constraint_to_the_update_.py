"""Add a unique constraint to the Update.title

Revision ID: 3aae6532b560
Revises: 83c7716b12cf
Create Date: 2016-03-01 19:03:30.088491

"""
import logging

from alembic import op
from sqlalchemy.orm import scoped_session, sessionmaker, aliased
from zope.sqlalchemy import ZopeTransactionExtension
import transaction

from bodhi.server.models import Update, Base


# revision identifiers, used by Alembic.
revision = '3aae6532b560'
down_revision = '83c7716b12cf'

log = logging.getLogger('alembic.migration')


def upgrade():
    engine = op.get_bind()
    Session = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
    Session.configure(bind=engine)
    db = Session()
    Base.metadata.bind = engine

    # Remove updates with duplicate titles and empty builds
    # This bug has been resolved with https://github.com/fedora-infra/bodhi/pull/809
    with transaction.manager:
        update_alias = aliased(Update)
        dupes = db.query(Update, update_alias).\
            join((update_alias, Update.id > update_alias.id)).\
            filter(Update.title == update_alias.title).all()
        for pair in dupes:
            for up in pair:
                if len(up.builds) == 0:
                    log.info('Deleting %s (%s)' % (up.title, up.alias))
                    for c in up.comments:
                        db.delete(c)
                    db.delete(up)

    op.drop_index('ix_updates_title', table_name='updates')
    op.create_index(op.f('ix_updates_title'), 'updates', ['title'], unique=True)


def downgrade():
    op.drop_index(op.f('ix_updates_title'), table_name='updates')
    op.create_index('ix_updates_title', 'updates', ['title'], unique=False)
