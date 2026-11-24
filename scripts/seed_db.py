#!/usr/bin/env python3
"""
Database Seeder Script: Generates 1,000+ realistic synthetic subscription records,
users, roles, categories, expenses, and renewal histories.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.seeds.generate_synthetic_data import generate_seed_data


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 1050
    print(f"Seeding database with {count} synthetic subscription records...")
    generate_seed_data(count)
    print("Seeding complete!")
