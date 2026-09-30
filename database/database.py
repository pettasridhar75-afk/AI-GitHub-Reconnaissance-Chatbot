import sqlite3
import os


# ============================================================
# DATABASE LOCATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATABASE_DIR = os.path.join(
    BASE_DIR,
    "data"
)

DATABASE_PATH = os.path.join(
    DATABASE_DIR,
    "reconnaissance.db"
)


# ============================================================
# CREATE DATABASE DIRECTORY
# ============================================================

os.makedirs(
    DATABASE_DIR,
    exist_ok=True
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# CREATE TABLES
# ============================================================

def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()


    # --------------------------------------------------------
    # REPOSITORIES TABLE
    # --------------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS repositories (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            full_name TEXT UNIQUE,

            name TEXT,

            owner TEXT,

            description TEXT,

            url TEXT,

            stars INTEGER,

            forks INTEGER,

            language TEXT,

            default_branch TEXT,

            created_at TEXT,

            updated_at TEXT,

            open_issues INTEGER,

            license TEXT,

            analyzed_at TEXT
        )
        """
    )


    # --------------------------------------------------------
    # SECURITY FINDINGS TABLE
    # --------------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS security_findings (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            repository_id INTEGER,

            file_path TEXT,

            category TEXT,

            severity TEXT,

            url TEXT,

            FOREIGN KEY (
                repository_id
            )
            REFERENCES repositories(id)
        )
        """
    )


    connection.commit()

    connection.close()


# ============================================================
# SAVE REPOSITORY
# ============================================================

def save_repository(repository):

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        INSERT OR REPLACE INTO repositories (

            full_name,
            name,
            owner,
            description,
            url,
            stars,
            forks,
            language,
            default_branch,
            created_at,
            updated_at,
            open_issues,
            license,
            analyzed_at

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """,

        (
            repository.get("full_name"),
            repository.get("name"),
            repository.get("owner"),
            repository.get("description"),
            repository.get("url"),
            repository.get("stars"),
            repository.get("forks"),
            repository.get("language"),
            repository.get("default_branch"),
            repository.get("created_at"),
            repository.get("updated_at"),
            repository.get("open_issues"),
            repository.get("license")
        )
    )


    connection.commit()


    cursor.execute(
        """
        SELECT id
        FROM repositories
        WHERE full_name = ?
        """,
        (
            repository.get("full_name"),
        )
    )


    result = cursor.fetchone()

    repository_id = result["id"]


    connection.close()


    return repository_id


# ============================================================
# SAVE SECURITY FINDING
# ============================================================

def save_security_finding(
    repository_id,
    finding
):

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        INSERT INTO security_findings (

            repository_id,
            file_path,
            category,
            severity,
            url

        )

        VALUES (?, ?, ?, ?, ?)
        """,

        (
            repository_id,

            finding.get("file"),

            finding.get("category"),

            finding.get(
                "severity",
                "Medium"
            ),

            finding.get("url")
        )
    )


    connection.commit()

    connection.close()


# ============================================================
# GET SAVED REPOSITORIES
# ============================================================

def get_saved_repositories():

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT *
        FROM repositories
        ORDER BY analyzed_at DESC
        """
    )


    repositories = cursor.fetchall()

    connection.close()


    return repositories


# ============================================================
# GET SECURITY FINDINGS
# ============================================================

def get_security_findings(
    repository_id
):

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT *
        FROM security_findings
        WHERE repository_id = ?
        ORDER BY id DESC
        """,
        (
            repository_id,
        )
    )


    findings = cursor.fetchall()

    connection.close()


    return findings 