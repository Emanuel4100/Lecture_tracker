import flet as ft
from models.schedule import SemesterSchedule
from views.schedule_view import ScheduleView
from views.add_course_view import AddCourseView
from views.onboarding_view import OnboardingView
from views.settings_view import SettingsView

def main(page: ft.Page):
    page.title = "מעקב הרצאות לסטודנט"
    page.rtl = True
    page.theme_mode = ft.ThemeMode.LIGHT
    
    my_schedule = SemesterSchedule()
    my_schedule.load_from_file()

    def change_screen(screen_name):
        page.controls.clear() 
        
        if not my_schedule.is_semester_set():
            page.controls.append(OnboardingView(page, my_schedule, change_screen))
        else:
            if screen_name == "schedule":
                page.controls.append(ScheduleView(page, my_schedule, change_screen))
            elif screen_name == "add":
                page.controls.append(AddCourseView(page, my_schedule, change_screen))
            elif screen_name == "settings":
                page.controls.append(SettingsView(page, my_schedule, change_screen))
            
        page.update()

    change_screen("schedule")

if __name__ == "__main__":
    ft.run(main, port=8550, host="0.0.0.0")