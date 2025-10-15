
import os
import sys

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


def do_init():
    # import app details lazily so tests that don't configure DB won't fail on import
    from app import DB_ENABLED
    if not DB_ENABLED:
        print("DB not enabled, skipping init")
        return
    from app import app, init_db
    init_db(app)
    print("✅ Auth service DB initialized")


def do_seed():
    # The init_db function already seeds from USERS_JSON when DB enabled
    from app import DB_ENABLED
    if not DB_ENABLED:
        print("DB not enabled, skipping seed")
        return
    print("Seeding handled in init step if DB enabled")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Initialize auth-service database')
    parser.add_argument('--init', action='store_true', help='Create tables')
    parser.add_argument('--seed', action='store_true', help='Seed data')
    args = parser.parse_args()

    if args.init:
        do_init()

    if args.seed:
        do_seed()

    if not args.init and not args.seed:
        print('Usage: python init_db.py [--init] [--seed]')