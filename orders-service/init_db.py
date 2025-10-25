"""Simple init script to create DB tables and optionally seed sample orders.

Usage: python init_db.py --init --seed
"""
import argparse
import os
from app.db import engine, Base, SessionLocal
from app.services.orders_service import OrdersService


def init_db(seed=False):
    print('Creating tables...')
    Base.metadata.create_all(bind=engine)
    if seed:
        print('Seeding sample orders...')
        svc = OrdersService()
        try:
            svc.seed()
            print('Seed complete')
        except Exception as e:
            print('Seed failed:', e)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--init', action='store_true', help='Create tables')
    parser.add_argument('--seed', action='store_true', help='Seed sample data')
    args = parser.parse_args()
    if args.init:
        init_db(seed=args.seed)
    else:
        print('Nothing to do. Use --init [--seed]')


if __name__ == '__main__':
    main()
