import sqlite3
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QFrame
)

from PySide6.QtCore import Qt

from database.connection import DATABASE_PATH


class SettingsPage(QWidget):

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)

        # PAGE TITLE

        title = QLabel("Settings & Backup")
        title.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: white;
        """)

        subtitle = QLabel(
            "Manage your TradeWise database and backups."
        )

        subtitle.setStyleSheet("""
            color: #94A3B8;
            font-size: 13px;
        """)

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        # DATABASE INFORMATION

        database_card = QFrame()
        database_card.setStyleSheet("""
            QFrame {
                background-color: #0F172A;
                border-radius: 12px;
                padding: 15px;
            }
        """)

        database_layout = QVBoxLayout(database_card)

        database_title = QLabel("Database Information")
        database_title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: white;
        """)

        database_status = QLabel(
            f"Database Location: {DATABASE_PATH}"
        )

        database_status.setWordWrap(True)
        database_status.setStyleSheet("""
            color: #94A3B8;
            font-size: 12px;
        """)

        database_layout.addWidget(database_title)
        database_layout.addWidget(database_status)

        main_layout.addWidget(database_card)

        # BACKUP SECTION

        backup_card = QFrame()
        backup_card.setStyleSheet("""
            QFrame {
                background-color: #0F172A;
                border-radius: 12px;
                padding: 15px;
            }
        """)

        backup_layout = QVBoxLayout(backup_card)

        backup_title = QLabel("Database Backup")
        backup_title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: white;
        """)

        backup_description = QLabel(
            "Create a safe copy of your TradeWise database."
        )

        backup_description.setStyleSheet(
            "color: #94A3B8;"
        )

        backup_button = QPushButton("Create Backup")
        backup_button.setCursor(Qt.PointingHandCursor)

        backup_button.setStyleSheet("""
            QPushButton {
                background-color: #16A34A;
                color: white;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #15803D;
            }
        """)

        backup_button.clicked.connect(self.create_backup)

        backup_layout.addWidget(backup_title)
        backup_layout.addWidget(backup_description)
        backup_layout.addWidget(backup_button)

        main_layout.addWidget(backup_card)

        # RESTORE SECTION

        restore_card = QFrame()
        restore_card.setStyleSheet("""
            QFrame {
                background-color: #0F172A;
                border-radius: 12px;
                padding: 15px;
            }
        """)

        restore_layout = QVBoxLayout(restore_card)

        restore_title = QLabel("Restore Database")
        restore_title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: white;
        """)

        restore_description = QLabel(
            "Restore your database using a previous backup."
        )

        restore_description.setStyleSheet(
            "color: #94A3B8;"
        )

        restore_button = QPushButton("Restore Backup")
        restore_button.setCursor(Qt.PointingHandCursor)

        restore_button.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: white;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #1D4ED8;
            }
        """)

        restore_button.clicked.connect(self.restore_backup)

        restore_layout.addWidget(restore_title)
        restore_layout.addWidget(restore_description)
        restore_layout.addWidget(restore_button)

        main_layout.addWidget(restore_card)

        main_layout.addStretch()

    # CREATE DATABASE BACKUP

    def create_backup(self):

        if not DATABASE_PATH.exists():

            QMessageBox.warning(
                self,
                "Database Not Found",
                "TradeWise database file was not found."
            )
            return

        backup_directory = QFileDialog.getExistingDirectory(
            self,
            "Select Backup Folder"
        )

        if not backup_directory:
            return

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        backup_path = (
            f"{backup_directory}/TradeWise_Backup_{timestamp}.db"
        )

        try:

            with sqlite3.connect(str(DATABASE_PATH)) as source:

                with sqlite3.connect(backup_path) as destination:

                    source.backup(destination)

            QMessageBox.information(
                self,
                "Backup Successful",
                f"Backup created successfully!\n\n{backup_path}"
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Backup Error",
                str(error)
            )

    # RESTORE DATABASE BACKUP

    def restore_backup(self):

        backup_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Database Backup",
            "",
            "Database Files (*.db)"
        )

        if not backup_path:
            return

        if str(DATABASE_PATH).lower() == backup_path.lower():

            QMessageBox.warning(
                self,
                "Invalid Backup",
                "You cannot restore the database from itself."
            )
            return

        try:

            # Validate selected backup

            with sqlite3.connect(backup_path) as source:

                result = source.execute(
                    "PRAGMA integrity_check"
                ).fetchone()

                if not result or result[0] != "ok":

                    QMessageBox.warning(
                        self,
                        "Invalid Backup",
                        "Selected backup file is corrupted."
                    )
                    return

                # Create safety backup before restoring

                timestamp = datetime.now().strftime(
                    "%Y%m%d_%H%M%S"
                )

                safety_backup = DATABASE_PATH.parent / (
                    f"TradeWise_Before_Restore_{timestamp}.db"
                )

                if DATABASE_PATH.exists():

                    with sqlite3.connect(
                        str(DATABASE_PATH)
                    ) as current_database:

                        with sqlite3.connect(
                            str(safety_backup)
                        ) as safety_database:

                            current_database.backup(
                                safety_database
                            )

                # Restore selected backup

                with sqlite3.connect(
                    str(DATABASE_PATH)
                ) as destination:

                    source.backup(destination)

            QMessageBox.information(
                self,
                "Restore Successful",
                "Database restored successfully!\n\n"
                "Please restart TradeWise to refresh the data."
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Restore Error",
                f"Could not restore database:\n{error}"
            )