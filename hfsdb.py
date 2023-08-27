import requests
from binascii import crc32
from hashlib import md5, sha1
from os import path


LANGUAGES = ['en', 'fr', 'de', 'it', 'es', 'jp', 'pt']
REGIONS = ['PAL', 'JPN', 'US', 'WORLD']

# __version__ = "1.1.0"


class HFSDB(object):
    def __init__(self):
        self.s = requests.session()
        # self.dburl = "https://db.hfsplay.fr/"
        self.dburl = "http://localhost:8000/"
        self.appstate = {'token': None, 'username': None}
        if self.appstate['token']:
            self.s.headers.update({'Authorization': 'Token ' + self.appstate['token']})

        self.meta_cache = {}

    # ACCOUNT =========================

    def logout(self):
        self.appstate['token'] = None
        self.appstate['username'] = None
        self.s.headers.update({'Authorization': None})

    def login(self, user='', pwd=''):
        if self.appstate['token']:
            return self.appstate
        res = self.s.post(self.dburl + 'api/v1/auth/token', {'username': user, 'password': pwd})
        data = res.json()
        if 'token' not in data:
            return False
        self.appstate['token'] = data['token']
        self.appstate['username'] = user
        self.s.headers.update({'Authorization': 'Token ' + data['token']})
        return self.appstate

    def account(self):
        res = self.s.get(self.dburl + 'api/v1/account')
        return res.json()

    # MEDIAS =========================

    def upload_media(self, file, dbitem_id, meta):
        # {'media-type': ['artwork'], 'media-author': [''], 'media-license': [''], 'media-region': [''],
        # 'media-artworktype': [''], 'media-id_artworktype': ['']}
        # {'media-file': [<InMemoryUploadedFile: salt.png (image/png)>]}

        # handle subtype metadata
        if 'subtype' in meta:
            sub_name = '%stype' % meta['type']
            sub_value = meta['subtype']
            sub_id = self.get_metadata_id(sub_name, sub_value)
            if not sub_id:
                return False, 'SubtypeNotFound-%s-%s' % (sub_name, sub_value)
            meta['id_%s' % sub_name] = sub_id
            meta[sub_name] = sub_value
            del meta['subtype']

        data = {'media-' + k: v for k, v in meta.items()}

        try:
            with open(file, 'rb') as f:
                files = {'media-file': f}
                res = self.s.post(self.dburl + 'api/v1/dbitem/%s/addmedia' % dbitem_id, files=files, data=data)
        except FileNotFoundError:
            return False, 'FileNotFound'

        if 'detail' in res.json() and res.json()['detail'] == 'ok':
            return True, 'OK'
        return False, 'OtherError: %s' % str(res.content)

    def upload_hash(self, file, dbitem_id):
        try:
            with open(file, 'rb') as f:
                shasum = sha1()
                md5sum = md5()
                crcsum = 0

                chunk = f.read(4096)
                while chunk != b"":
                    shasum.update(chunk)
                    md5sum.update(chunk)
                    crcsum = crc32(chunk, crcsum)
                    chunk = f.read(4096)

                data = {
                    'media-type': 'hash',
                    'media-md5': md5sum.hexdigest(),
                    'media-sha1': shasum.hexdigest(),
                    'media-crc32': format(crcsum & 0xFFFFFFFF, '08x'),
                    'media-description': path.basename(file),
                    'media-size': path.getsize(file),
                }

                res = self.s.post(self.dburl + 'api/v1/dbitem/%s/addmedia' % dbitem_id, data=data)
                if 'detail' in res.json() and res.json()['detail'] == 'ok':
                    return True, 'OK'
                return False, 'OtherError: %s' % str(res.content)
        except FileNotFoundError:
            return False, 'FileNotFound'
        return False, 'UnknownError'

    # GAMES =========================

    def create_game(self, data):
        # name, description, genre, id_genre, editor, id_editor, developer, id_developer,
        # system, id_system, players, id_players, rating_eur, id_rating_eur, rating_usa,
        # id_rating_usa, rating_jpn, id_rating_jpn, released_at_PAL, released_at_US, released_at_JPN,
        # released_at_WORLD, resolution_ntsc, id_resolution_ntsc, resolution_pal, id_resolution_pal, lang,

        res = self.s.post(self.dburl + 'api/v1/games', data)
        if res.status_code == 200:
            return res.json()['redirect']
        print('[!!] FAILED CREATING GAME: ' + res.text)
        return False

    def edit_game(self, dbitem_id, data):
        editable_fields = ['name', 'description', 'lang']
        release_fields = ['released_at_' + R for R in REGIONS]

        assert 'lang' in data
        assert data['lang'] in LANGUAGES

        for item in data:
            assert item in editable_fields or item in release_fields

        game = self.get_game(dbitem_id)
        if not game:
            return False

        new_data = {
            'lang': data['lang'],
            'name': game['name_' + data['lang']],
            'description': game['description_' + data['lang']]
        }

        for r in REGIONS:
            if 'released_at_' + r in data:
                new_data['released_at_' + r] = data['released_at_' + r]
            else:
                new_data['released_at_' + r] = game['released_at_' + r]

        if 'name' in data:
            new_data['name'] = data['name']
        if 'description' in data:
            new_data['description'] = data['description']

        res = self.s.post(self.dburl + 'api/v1/dbitem/%s/revision' % dbitem_id, new_data)
        return res.json()

    def delete_game(self, dbitem_id):
        res = self.s.delete(self.dburl + 'api/v1/games/%s' % dbitem_id)
        return res.json()

    def search_game(self, name, system=None):
        if system:
            res = self.s.get(self.dburl + 'api/v1/games?search=%s&system=%s' % (name, system))
        else:
            res = self.s.get(self.dburl + 'api/v1/games?search=%s' % name)
        return res.json()

    def get_game(self, dbitem_id):
        game = self.s.get(self.dburl + 'api/v1/games/%s' % dbitem_id)
        if game.status_code == 404:
            return False
        return game.json()

    # SYSTEMS =========================

    def list_systems(self):
        res = self.s.get(self.dburl + 'api/v1/systems?id_and_name=1')
        print(res.text)
        return res.json()

    # METADATA =========================

    def list_metadata(self, name):
        res = self.s.get(self.dburl + 'api/v1/metadata?name=%s' % name)
        print(res.text)
        return res.json()

    def create_metadata(self, name, value):
        res = self.s.post(self.dburl + 'api/v1/metadata', {'name': name, 'value': value})
        if res.status_code == 201:
            json = res.json()
            print('CREATED %s %s %s' % (json['id'], name, value))
            self.meta_cache[name][value] = json['id']
            return json['id']
        print('[!!] FAILED CREATING METADATA: ' + res.text)
        return False

    def get_or_create_metadata(self, name, value, ask=True):
        m_id = self.get_metadata_id(name, value)
        if not m_id:
            if ask:
                r = input('"%s:%s" does not exist; Create ? (y)es / (n)o / (r)ename: ' % (name, value))
                if r == 'y':
                    pass
                elif r == 'r':
                    value = input("input new value for %s:" % name)
                    return self.get_or_create_metadata(name, value)
                elif r == 'n':
                    return False
            m_id = self.create_metadata(name, value)
        return m_id

    def get_metadata_id(self, name, value):
        if name in self.meta_cache:
            if value not in self.meta_cache[name]:
                return False
            return self.meta_cache[name][value]

        res = self.s.get(self.dburl + 'api/v1/metadata?name=%s' % name)
        while True:
            for v in res.json()['results']:
                if name not in self.meta_cache:
                    self.meta_cache[name] = {}
                self.meta_cache[name][v['value']] = v['id']
            if not res.json()['next']:
                break
            res = self.s.get(res.json()['next'])

        if name not in self.meta_cache:
            return False

        if value in self.meta_cache[name]:
            return self.meta_cache[name][value]
        return False
