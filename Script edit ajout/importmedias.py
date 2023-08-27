import csv
from datetime import datetime
from hfsdb import HFSDB
from settings import LOGIN, PASSWORD


def main():
    db = HFSDB()
    db.dburl = "https://db.hfsplay.fr/"
    db.login(LOGIN, PASSWORD)
    print(db.account())

    # example:
    # id,media_type,author,license,region,path
    # 87528,cover3d,Phenix14000,CC-BY-NC-SA,PAL,files/Covers3d/Ace Combat 2.png

    now = datetime.now().strftime('%Y%m%d-%H%M%S')
    log = open('LOG-%s.txt' % now, 'w')

    with open('psx_covers_covers3d.csv', 'r') as f:
        reader = csv.DictReader(f, delimiter=';', quotechar='"')

        for r in reader:

            game_id = int(r['ID'])

            upload_data = {
                'type': 'cover2d',
                'subtype': 'front',
                'author': 'Phenix14000',
                'region': r['region'],
                'licence': r['license'],
            }

            success, msg = db.upload_media(r['path'], game_id, upload_data)

            if success:
                info = 'OK added media [%s] %s' % (game_id, r['path'])
            else:
                info = 'FAILED adding media [%s] %s : %s' % (game_id, r['path'], msg)

            print(info)
            log.write(info + '\n')


if __name__ == '__main__':
    main()
