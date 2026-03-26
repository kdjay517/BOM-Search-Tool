import sys
import ctypes

# Prevent multiple instances
mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "BOM_SEARCH_TOOL_MUTEX")
if ctypes.windll.kernel32.GetLastError() == 183:
    sys.exit(0)

from ui.main_window import MainWindow


def main():
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()
