from couchpotato import get_session
from couchpotato.api import addApiView
from couchpotato.core.event import fireEvent, fireEventAsync, addEvent
from couchpotato.core.helpers.variable import splitString
from couchpotato.core.logger import CPLog
from couchpotato.core.media import MediaBase

log = CPLog(__name__)


class Media(MediaBase):

    def __init__(self):

        addApiView('media.refresh', self.refresh, docs = {
            'desc': 'Refresh a any media type by ID',
            'params': {
                'id': {'desc': 'Movie, Show, Season or Episode ID(s) you want to refresh.', 'type': 'int (comma separated)'},
            }
        })

        addEvent('app.load', self.addSingleRefresh)

    def refresh(self, id = '', **kwargs):
        db = get_session()

        for x in splitString(id):
            media = db.query(Media).filter_by(id = x).first()

            if media:
                # Get current selected title
                default_title = ''
                for title in media.library.titles:
                    if title.default: default_title = title.title

                fireEvent('notify.frontend', type = '%s.busy.%s' % (media.type, x), data = True)
                fireEventAsync('library.update.%s' % media.type, identifier = media.library.identifier, default_title = default_title, force = True, on_complete = self.createOnComplete(x))

        db.expire_all()

        return {
            'success': True,
        }

    def addSingleRefresh(self):

        for media_type in fireEvent('media.types', merge = True):
            addApiView('%s.refresh' % media_type, self.refresh)
