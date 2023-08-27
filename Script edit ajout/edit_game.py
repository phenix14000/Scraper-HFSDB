from hfsdb import HFSDB
from settings import LOGIN, PASSWORD


def main():
    db = HFSDB()
    db.dburl = "https://db.hfsplay.fr/"
    db.login(LOGIN, PASSWORD)
    print(db.account())

    data = {'lang': 'fr', 'description': 'test'}
    res = db.edit_game(164394, data)

    print(res)


if __name__ == '__main__':
    main()
