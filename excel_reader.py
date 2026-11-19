
from openpyxl import load_workbook
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

EXCEL_FILE = Path(__file__).resolve().parent / "menu.xlsx"


def get_day_menu(day):
    workbook = None

    try:
        workbook = load_workbook(
            EXCEL_FILE,
            read_only=True,
            data_only=True
        )

        sheet = workbook.active

        for row in sheet.iter_rows(min_row=3, values_only=True):

            if not row[0]:
                continue

            if str(row[0]).strip().lower() == day.strip().lower():

                return {
                    "Breakfast": row[1],
                    "Lunch": row[2],
                    "Snacks": row[3],
                    "Dinner": row[4]
                }

        logger.warning("Menu not found for %s", day)
        return {}

    except Exception:
        logger.exception("Error reading menu.xlsx")
        return {}

    finally:
        if workbook:
            workbook.close()
