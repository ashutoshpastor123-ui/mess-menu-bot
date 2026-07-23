from openpyxl import load_workbook

DAY_COLUMNS = {
    "Monday": 3,
    "Tuesday": 4,
    "Wednesday": 5,
    "Thursday": 6,
    "Friday": 7,
    "Saturday": 8,
    "Sunday": 9
}

def get_day_menu(day):

    workbook = load_workbook("menu.xlsx")
    sheet = workbook.active

    col = DAY_COLUMNS[day]

    menu = {}

    for row in sheet.iter_rows(min_row=2):

        meal = row[0].value

        if meal is None:
            continue

        meal_name = meal.split()[0].capitalize()

        menu[meal_name] = row[col - 1].value

    return menu