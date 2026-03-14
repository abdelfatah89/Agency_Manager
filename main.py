import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont

from src.main_window.main_window import MainWindowDashboard
from services.db_services.backup_service import run_backup_now

def main() -> None:
    app = QApplication(sys.argv)
    app.setFont(QFont("Tajawal", 10))
    
    # Set application metadata
    app.setApplicationName("KONACH - Daily Balance")
    app.setOrganizationName("KONACH")

    # Start directly with dashboard (login screen disabled).
    window = MainWindowDashboard()
    window.show()

    # Execute application
    exit_code = app.exec_()

    # Safety backup on app shutdown.
    ok, path, message = run_backup_now(reason="app-close")
    if ok:
        print(f"[Backup] Backup created on close: {path}")
    else:
        print(f"[Backup] {message}")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
