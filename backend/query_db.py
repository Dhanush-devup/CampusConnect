"""
CampusConnect Interactive SQL Query Tool
Execute any SQL query on campus_connect.db directly from your terminal.

Usage:
  1. Interactive mode:
       python query_db.py

  2. One-liner query:
       python query_db.py "SELECT name, email, role FROM users LIMIT 5;"
"""
import sys
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "campus_connect.db"


def print_table(cursor, headers=True):
    rows = cursor.fetchall()
    if not rows:
        print("  (0 rows returned)")
        return

    col_names = [desc[0] for desc in cursor.description]
    str_rows = [[str(val) if val is not None else "NULL" for val in row] for row in rows]

    # Calculate column widths
    col_widths = [len(name) for name in col_names]
    for row in str_rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(val))

    # Print header
    header_line = " | ".join(name.ljust(col_widths[i]) for i, name in enumerate(col_names))
    separator = "-+-".join("-" * col_widths[i] for i in range(len(col_names)))

    print(f"\n{header_line}")
    print(separator)
    for row in str_rows:
        print(" | ".join(val.ljust(col_widths[i]) for i, val in enumerate(row)))
    print(f"({len(rows)} row{'s' if len(rows) != 1 else ''})\n")


def run_query(conn, query):
    query = query.strip()
    if not query:
        return

    # Special dot-commands
    if query in (".tables", "tables"):
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [t[0] for t in cur.fetchall()]
        print("\nTables in database:")
        for t in tables:
            print(f"  - {t}")
        print()
        return

    if query.startswith(".schema"):
        parts = query.split(maxsplit=1)
        cur = conn.cursor()
        if len(parts) > 1:
            table_name = parts[1].strip()
            cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        else:
            cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        rows = cur.fetchall()
        print()
        for r in rows:
            if r[0]:
                print(r[0] + ";\n")
        return

    try:
        cur = conn.cursor()
        cur.execute(query)
        if cur.description:
            print_table(cur)
        else:
            conn.commit()
            print(f"Query executed successfully. ({cur.rowcount} rows affected)\n")
    except sqlite3.Error as e:
        print(f"SQL Error: {e}\n")


def interactive_shell(conn):
    print("=" * 70)
    print(" CampusConnect Interactive SQL Terminal")
    print(f" Connected to: {DB_PATH.name}")
    print(" Type your SQL query (e.g., SELECT * FROM students LIMIT 5;)")
    print(" Helpful commands:  .tables    .schema <table_name>    exit")
    print("=" * 70)

    while True:
        try:
            query = input("sql> ").strip()
            if not query:
                continue
            if query.lower() in ("exit", "quit", "q"):
                print("Bye!")
                break
            run_query(conn, query)
        except (KeyboardInterrupt, EOFError):
            print("\nBye!")
            break


def main():
    if not DB_PATH.exists():
        print(f"Database file not found at: {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)

    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        run_query(conn, query)
    else:
        interactive_shell(conn)

    conn.close()


if __name__ == "__main__":
    main()
