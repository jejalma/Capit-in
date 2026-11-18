"""Export business data from SQLite (without users) to data_backup/sia-data.sql."""
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
db = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'sia' / 'data' / 'sia.db'
out = ROOT / 'data_backup' / 'sia-data.sql'
out.parent.mkdir(exist_ok=True)

c = sqlite3.connect(db)
lines = [l for l in c.iterdump()
         if l.startswith('INSERT INTO') and not l.startswith('INSERT INTO "users"')
         and not l.startswith('INSERT INTO "sqlite_sequence"')]
for name, seq in c.execute("SELECT name, MAX(seq) FROM sqlite_sequence WHERE name != 'users' GROUP BY name"):
    lines.append(f"INSERT INTO \"sqlite_sequence\" VALUES('{name}',{seq});")
out.write_text('\n'.join(lines) + '\n')
print(f'{len(lines)} rows -> {out}')
