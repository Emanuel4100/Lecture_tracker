import flet as ft
from models.schedule import SemesterSchedule
from views.schedule_view import ScheduleView
from views.add_course_view import AddCourseView
from views.add_meeting_view import AddMeetingView # <-- הוספנו את הייבוא החדש
from views.onboarding_view import OnboardingView
from views.settings_view import SettingsView
from utils.i18n import translator, t

def main(page: ft.Page):
    my_schedule = SemesterSchedule()
    my_schedule.load_from_file()
    
    translator.set_language(my_schedule.language)
    page.title = t("schedule.app_title", default="Lecture Tracker")
    page.rtl = (my_schedule.language == "he")
    page.theme_mode = ft.ThemeMode.LIGHT

    def change_screen(screen_name):
        page.controls.clear() 
        
        if not my_schedule.is_semester_set():
            page.controls.append(OnboardingView(page, my_schedule, change_screen))
        else:
            if screen_name == "schedule":
                page.controls.append(ScheduleView(page, my_schedule, change_screen))
            elif screen_name == "add":
                page.controls.append(AddCourseView(page, my_schedule, change_screen))
            elif screen_name == "add_meeting": # <-- הוספנו את הניתוב החדש
                page.controls.append(AddMeetingView(page, my_schedule, change_screen))
            elif screen_name == "settings":
                page.controls.append(SettingsView(page, my_schedule, change_screen))
            
        page.update()

    change_screen("schedule")

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")