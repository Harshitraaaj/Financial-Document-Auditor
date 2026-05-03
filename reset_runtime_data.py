from __future__ import annotations

import argparse
import shutil
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from financial_auditor.core.config import Settings
from financial_auditor.core.storage import SQLiteStore


RUNTIME_SUBDIRECTORIES = ("storage", "reports", "audit_trail", "logs")
SQLITE_TABLES = ("documents", "invoice_index", "audit_events")


@dataclass(frozen=True)
class ResetSummary:
    data_dir: Path
    database_path: Path
    removed_directories: list[Path]
    reset_tables: list[str]


def reset_runtime_data(settings: Settings, dry_run: bool = False) -> ResetSummary:
    data_dir = settings.data_dir.resolve()
    database_path = settings.database_path.resolve()
    _assert_safe_runtime_path(data_dir)

    removed_directories = _clear_runtime_directories(data_dir, dry_run=dry_run)
    reset_tables = _reset_sqlite_tables(database_path, dry_run=dry_run)

    if not dry_run:
        settings.ensure_local_dirs()
        (data_dir / "audit_trail").mkdir(parents=True, exist_ok=True)
        SQLiteStore(settings).initialize()

    return ResetSummary(
        data_dir=data_dir,
        database_path=database_path,
        removed_directories=removed_directories,
        reset_tables=reset_tables,
    )


def _clear_runtime_directories(data_dir: Path, dry_run: bool) -> list[Path]:
    removed: list[Path] = []
    for name in RUNTIME_SUBDIRECTORIES:
        path = data_dir / name
        if path.exists():
            removed.append(path)
            if not dry_run:
                shutil.rmtree(path)
        elif not dry_run:
            path.mkdir(parents=True, exist_ok=True)
    return removed


def _reset_sqlite_tables(database_path: Path, dry_run: bool) -> list[str]:
    if not database_path.exists():
        return []

    reset_tables: list[str] = []
    with sqlite3.connect(database_path) as connection:
        existing_tables = _existing_tables(connection)
        for table_name in SQLITE_TABLES:
            if table_name in existing_tables:
                reset_tables.append(table_name)
                if not dry_run:
                    connection.execute(f"DELETE FROM {table_name}")
        if not dry_run:
            _reset_sqlite_sequences(connection, reset_tables)
            connection.commit()
            connection.execute("VACUUM")
    return reset_tables


def _existing_tables(connection: sqlite3.Connection) -> set[str]:
    rows = connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
    return {row[0] for row in rows}


def _reset_sqlite_sequences(connection: sqlite3.Connection, table_names: list[str]) -> None:
    if "sqlite_sequence" not in _existing_tables(connection):
        return
    for table_name in table_names:
        connection.execute("DELETE FROM sqlite_sequence WHERE name = ?", (table_name,))


def _assert_safe_runtime_path(data_dir: Path) -> None:
    if data_dir.anchor == str(data_dir):
        raise ValueError(f"Refusing to reset filesystem root: {data_dir}")
    if data_dir.name in {"", ".", ".."}:
        raise ValueError(f"Refusing to reset ambiguous runtime path: {data_dir}")
    if len(data_dir.parts) < 2:
        raise ValueError(f"Refusing to reset unsafe runtime path: {data_dir}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clear local runtime data for repeatable testing.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be cleared without deleting runtime data.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    settings = Settings()
    summary = reset_runtime_data(settings, dry_run=args.dry_run)
    action = "Would reset" if args.dry_run else "Reset"
    print(f"{action} runtime data directory: {summary.data_dir}")
    print(f"{action} SQLite database: {summary.database_path}")
    print("Runtime directories:")
    for path in summary.removed_directories:
        print(f"  - {path}")
    if not summary.removed_directories:
        print("  - none existed")
    print("SQLite tables:")
    for table_name in summary.reset_tables:
        print(f"  - {table_name}")
    if not summary.reset_tables:
        print("  - none existed")


if __name__ == "__main__":
    main()

