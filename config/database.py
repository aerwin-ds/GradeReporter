"""
Database connection management.
"""
import sqlite3
from sqlalchemy import create_engine
from contextlib import contextmanager
from typing import Generator
from config.settings import DB_PATH, AFTER_HOURS_DB_PATH


class DatabaseManager:
    """Manages database connections for the application."""

    def __init__(self):
        self._main_engine = None
        self._after_hours_engine = None

    @property
    def main_engine(self):
        """Get or create the main database engine."""
        if self._main_engine is None:
            self._main_engine = create_engine(f'sqlite:///{DB_PATH}')
        return self._main_engine

    @property
    def after_hours_engine(self):
        """Get or create the after-hours database engine."""
        if self._after_hours_engine is None:
            self._after_hours_engine = create_engine(f'sqlite:///{AFTER_HOURS_DB_PATH}')
        return self._after_hours_engine

    @contextmanager
    def get_connection(self, db_type: str = 'main') -> Generator[sqlite3.Connection, None, None]:
        """
        Context manager for database connections.

        Args:
            db_type: Either 'main' or 'after_hours'

        Yields:
            sqlite3.Connection: Database connection
        """
        if db_type == 'main':
            db_path = DB_PATH
        elif db_type == 'after_hours':
            db_path = AFTER_HOURS_DB_PATH
        else:
            raise ValueError(f"Unknown database type: {db_type}")

        conn = sqlite3.connect(db_path)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def execute_query(self, query: str, params: tuple = (), db_type: str = 'main'):
        """
        Execute a query and return results.

        Args:
            query: SQL query to execute
            params: Query parameters
            db_type: Either 'main' or 'after_hours'

        Returns:
            List of result rows as dictionaries
        """
        with self.get_connection(db_type) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def execute_update(self, query: str, params: tuple = (), db_type: str = 'main') -> int:
        """
        Execute an INSERT/UPDATE/DELETE query.

        Args:
            query: SQL query to execute
            params: Query parameters
            db_type: Either 'main' or 'after_hours'

        Returns:
            Number of affected rows
        """
        with self.get_connection(db_type) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.rowcount


# Global database manager instance
db_manager = DatabaseManager()
