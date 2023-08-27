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
    # ID;NAME;URL
    # 87528,Ace Combat 2;psx up\Covers3d\Ace Combat 2.bin

    now = datetime.now().strftime('%Y%m%d-%H%M%S')
    log = open('LOG-%s.txt' % now, 'w')

    with open('csvtest.csv', 'r') as f:
        reader = csv.DictReader(f, delimiter=';', quotechar='"')

        for r in reader:

            game_id = int(r['ID'])

            # add hash
            success, msg = db.upload_hash(r['URL'], game_id)
            result = 'OK' if success else 'FAILED'
            info = '%s adding hash [%s] (%s) %s' % (result, game_id, msg, r['URL'])

            print(info)
            log.write(info + '\n')


if __name__ == '__main__':
    main()
