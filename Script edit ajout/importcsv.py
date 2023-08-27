import csv
from datetime import datetime
import pickle
from hfsdb import HFSDB
import glob
from settings import LOGIN, PASSWORD


now = datetime.now().strftime('%Y%m%d-%H%M%S')
logfile = open('LOG-%s.txt' % now, 'w')


def log(info):
    print(info)
    logfile.write(info + "\n")


def get_path(path):
    return path.replace('/Private/HFPrivate/Chantiers HFSBox Finis', '/Users/v/Downloads')


def process_revert(db, file):
    pkl_file = open(file, 'rb')
    to_delete = pickle.load(pkl_file)
    for dbitem in to_delete:
        db.delete_game(dbitem)


def main():
    db = HFSDB()
    db.dburl = "https://db.hfsplay.fr/"
    db.login(LOGIN, PASSWORD)
    print(db.account())

    # return process_revert(db, 'CREATED-stuff.pkl')

    # Champs texte
    # 'Rom': -
    # 'Description': name
    # 'Manufacturer': editor
    # 'Developer': developer
    # 'Year': released_at_WORLD
    # 'Genre': genre
    # 'Rating': rating_usa
    # 'Players': players
    # 'Synopsis': description

    ID_SYSTEM = 36022
    SYSTEM = 'Game Boy'
    # ID_SYSTEM = 2
    # SYSTEM = 'fdpsystem'

    created = []

    with open('NGB.csv', 'r') as f:
        reader = csv.DictReader(f, delimiter=',', quotechar='"')
        # print(reader.fieldnames)
        for r in reader:

            id_players = ''
            if r['Players']:
                id_players = db.get_or_create_metadata('players', r['Players'])

            id_genre = ''
            if r['Genre']:
                id_genre = db.get_or_create_metadata('genre', r['Genre'].title())

            id_editor = ''
            if r['Manufacturer']:
                id_editor = db.get_or_create_metadata('editor', r['Manufacturer'], ask=False)

            id_developer = ''
            if r['Developer']:
                id_developer = db.get_or_create_metadata('developer', r['Developer'], ask=False)

            if r['Rating']:
                id_rating = db.get_or_create_metadata('rating_usa', r['Rating'])

            date = str(r['Year']) + '-01-01'

            # print(db.meta_cache)
            game = {
                "name": r['Description'].title(),
                "description": r['Synopsis'],
                "genre": r['Genre'].title(),
                "id_genre": id_genre,
                "editor": r['Manufacturer'],
                "id_editor": id_editor,
                "developer": r['Developer'],
                "id_developer": id_developer,
                "system": SYSTEM,
                "id_system": ID_SYSTEM,
                "players": r['Players'],
                "id_players": id_players,
                "rating_eur": "",
                "id_rating_eur": "",
                "rating_usa": r['Rating'],
                "id_rating_usa": id_rating,
                "rating_jpn": "",
                "id_rating_jpn": "",
                "released_at_PAL": "",
                "released_at_US": "",
                "released_at_JPN": "",
                "released_at_WORLD": date,
                "resolution_ntsc": "",
                "id_resolution_ntsc": "",
                "resolution_pal": "",
                "id_resolution_pal": "",
                "lang": "fr"
            }

            res = db.create_game(game)
            if res:
                created.append(res)
                log('created [%s] %s' % (res, game['name']))
            else:
                log('failed creating %s' % game['name'])

            if not res:
                continue

            # Champs fichiers
            # 'Cover3d' : cover3d
            # 'Hardware/Cartridge' : hardware, cartridge
            # 'Document/cheatETAJV': document, cheat ETAJV
            # 'Document/cheatFAQ': document, cheat FAQ
            # 'Document/cheat': document, cheat
            # 'Logo': logo
            # 'Roms': rom
            # 'screenshot/in game' : screenshot, in game
            # 'Vidéos': video
            # 'Manual': manual

            # upload_data = {
            #     'type': 'cover2d',
            #     'subtype': 'front',
            #     'author': 'Phenix14000',
            #     'region': 'PAL',
            #     'licence': 'CC BY-NC-ND',
            # }
            game_id = res

            # add medias ============================================================
            medias_avail = [
                'cover3d',
                'hardware/cartridge',
                'document/cheat ETAJV',
                'document/cheat FAQ',
                'document/cheat',
                'logo',
                'screenshot/in game',
                'video'
            ]

            for m in medias_avail:
                if m.find('/') != -1:
                    typ, subtype = m.split('/')
                    success, msg = db.upload_media(get_path(r[m]), game_id, {'type': typ, 'subtype': subtype})
                else:
                    success, msg = db.upload_media(get_path(r[m]), game_id, {'type': m})

                result = 'OK' if success else 'FAILED'
                log('%s adding media [%s] (%s) %s' % (result, game_id, msg, get_path(r[m])))

            # add hash ==============================================================
            success, msg = db.upload_hash(get_path(r['rom']), game_id)
            result = 'OK' if success else 'FAILED'
            log('%s adding hash [%s] (%s) %s' % (result, game_id, msg, get_path(r['rom'])))

            # add manuals ===========================================================
            manuals = glob.glob(get_path(r['manual']))
            for m in manuals:
                success, msg = db.upload_media(m, game_id, {'type': 'manual'})
                result = 'OK' if success else 'FAILED'
                log('%s adding media [%s] %s' % (result, game_id, m))

    with open('CREATED-%s.pkl' % now, 'wb') as p:
        pickle.dump(created, p)


if __name__ == '__main__':
    main()
