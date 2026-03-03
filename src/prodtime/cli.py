#!/usr/bin/env python

import sqlite3
import time
import argparse
import datetime
import csv

DB_FILE = "timers.db"


# ======================
# Database Setup
# ======================


def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS timers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            tags TEXT,
            duration REAL NOT NULL,
            created_at TEXT NOT NULL
        )
    """
    )
    conn.commit()
    conn.close()


# ======================
# Timer Logic (Pause/Resume)
# ======================


def start_timer():
    name = input("Enter timer name: ").strip()
    tags = input("Enter tags (comma separated, optional): ").strip()

    if not name:
        print("Timer name cannot be empty.")
        return

    print("\nTimer started. Press Ctrl+C to pause.\n")

    elapsed = 0
    start_time = time.perf_counter()

    try:
        while True:
            current = time.perf_counter()
            total = elapsed + (current - start_time)

            print(f"\rElapsed: {format_duration(total)}", end="")
            time.sleep(1)

    except KeyboardInterrupt:
        # Pause timer
        elapsed += time.perf_counter() - start_time
        print("\n\nPaused at:", format_duration(elapsed))

        while True:
            print("\nOptions:")
            print("1 → Resume")
            print("2 → Stop and Save")
            print("3 → Stop and Delete")

            choice = input("Select option (1/2/3): ").strip()

            if choice == "1":
                print("\nResuming...\nPress Ctrl+C to pause again.\n")
                start_time = time.perf_counter()
                try:
                    while True:
                        current = time.perf_counter()
                        total = elapsed + (current - start_time)
                        print(f"\rElapsed: {format_duration(total)}", end="")
                        time.sleep(1)
                except KeyboardInterrupt:
                    elapsed += time.perf_counter() - start_time
                    print("\n\nPaused at:", format_duration(elapsed))
                    continue

            elif choice == "2":
                save_timer(name, tags, elapsed)
                print("Timer saved.")
                return

            elif choice == "3":
                print("Timer deleted.")
                return

            else:
                print("Invalid option.")


# ======================
# Database Actions
# ======================


def save_timer(name, tags, duration):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO timers (name, tags, duration, created_at)
        VALUES (?, ?, ?, ?)
    """,
        (
            name,
            tags,
            round(duration, 2),
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )
    conn.commit()
    conn.close()


def format_duration(seconds: float) -> str:
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hours:02}:{minutes:02}:{secs:02}"


def list_timers():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM timers ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()

    if not rows:
        print("No timers found.")
        return

    for row in rows:
        formatted = format_duration(row[3])
        print(f"ID: {row[0]} | {row[1]} | {row[2]} | {formatted} | {row[4]}")


def delete_timer(timer_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM timers WHERE id=?", (timer_id,))
    conn.commit()
    conn.close()
    print("Deleted.")


def edit_timer(timer_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    new_name = input("New name: ")
    new_tags = input("New tags: ")

    c.execute(
        """
        UPDATE timers
        SET name=?, tags=?
        WHERE id=?
    """,
        (new_name, new_tags, timer_id),
    )

    conn.commit()
    conn.close()
    print("Updated.")


def export_csv():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM timers")
    rows = c.fetchall()
    conn.close()

    with open("timers_export.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Name", "Tags", "Duration", "Created At"])
        writer.writerows(rows)

    print("Exported to timers_export.csv")


def show_stats():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    print("\nTotal Time Per Task:")
    c.execute(
        """
        SELECT name, SUM(duration)
        FROM timers
        GROUP BY name
    """
    )
    for row in c.fetchall():
        print(f"{row[0]} → {round(row[1],2)} sec")

    print("\nDaily Totals:")
    c.execute(
        """
        SELECT DATE(created_at), SUM(duration)
        FROM timers
        GROUP BY DATE(created_at)
    """
    )
    for row in c.fetchall():
        print(f"{row[0]} → {round(row[1],2)} sec")

    conn.close()


# ======================
# CLI Interface
# ======================


def main():
    init_db()

    parser = argparse.ArgumentParser(
        prog="prodtime",
        description="""
prodtime — A developer-focused productivity timer.

Track named work sessions from the command line.
Supports pause/resume, tagging, statistics, editing,
CSV export, and persistent SQLite storage.
        """,
        epilog="""
Examples:
  prodtime start
      Start a new interactive timer session.

  prodtime list
      List all saved sessions.

  prodtime delete 3
      Delete session with ID 3.

  prodtime edit 5
      Edit name and tags of session 5.

  prodtime stats
      Show total time per task and daily totals.

  prodtime export
      Export all sessions to timers_export.csv
        """,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    subparsers = parser.add_subparsers(title="Commands", dest="command", metavar="")

    # -----------------------
    # start
    # -----------------------
    subparsers.add_parser(
        "start",
        help="Start a new productivity timer session.",
        description="""
Start an interactive stopwatch session.

During the session:
  p  → pause/resume
  s  → stop and save
  d  → stop and discard

You will be prompted for:
  - Timer name
  - Optional comma-separated tags
        """,
    )

    # -----------------------
    # list
    # -----------------------
    subparsers.add_parser(
        "list",
        help="List all saved timer sessions.",
        description="""
Display all recorded sessions in reverse
chronological order.

Shows:
  - ID
  - Task name
  - Tags
  - Duration (seconds)
  - Timestamp
        """,
    )

    # -----------------------
    # delete
    # -----------------------
    delete_parser = subparsers.add_parser(
        "delete",
        help="Delete a saved timer by ID.",
        description="""
Permanently remove a saved session from the database.
This action cannot be undone.
        """,
    )
    delete_parser.add_argument(
        "id", type=int, help="ID of the timer session to delete."
    )

    # -----------------------
    # edit
    # -----------------------
    edit_parser = subparsers.add_parser(
        "edit",
        help="Edit name and tags of a saved timer.",
        description="""
Update the task name and/or tags
of an existing session.
        """,
    )
    edit_parser.add_argument("id", type=int, help="ID of the timer session to edit.")

    # -----------------------
    # stats
    # -----------------------
    subparsers.add_parser(
        "stats",
        help="Show aggregated productivity statistics.",
        description="""
Displays:

1. Total time spent per task name.
2. Daily total time across all tasks.

Useful for identifying:
  - Repeated tasks
  - Daily productivity levels
        """,
    )

    # -----------------------
    # export
    # -----------------------
    subparsers.add_parser(
        "export",
        help="Export all sessions to CSV.",
        description="""
Export all saved sessions to:

  timers_export.csv

Columns:
  ID, Name, Tags, Duration (seconds), Timestamp
        """,
    )

    args = parser.parse_args()

    if args.command == "start":
        start_timer()

    elif args.command == "list":
        list_timers()

    elif args.command == "delete":
        delete_timer(args.id)

    elif args.command == "edit":
        edit_timer(args.id)

    elif args.command == "stats":
        show_stats()

    elif args.command == "export":
        export_csv()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
