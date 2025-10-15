"""Simple init script to create DB tables and optionally seed data for managers-service
Usage:
  python init_db.py --init --seed
"""
import argparse
from app import create_app
from app.config.database import db
from app.modules.managers.models import AccountManager, Client, AssignmentHistory


def init_db(seed=False):
    app = create_app()
    with app.app_context():
        print('Creating tables...')
        db.create_all()
        print('Tables created')
        if seed:
            print('Seeding sample data...')
            # Add minimal seed if no managers exist
            if db.session.query(AccountManager).count() == 0:
                m = AccountManager(full_name='Seed Manager', email='seed@local', phone='000', identification='SEED1')
                m.created_by = 'init'
                db.session.add(m)
                db.session.commit()
                print('Seed manager added')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--init', action='store_true', help='Create tables')
    parser.add_argument('--seed', action='store_true', help='Seed sample data')
    args = parser.parse_args()

    if args.init:
        init_db(seed=args.seed)
    else:
        print('Nothing to do. Use --init to create tables')


if __name__ == '__main__':
    main()
