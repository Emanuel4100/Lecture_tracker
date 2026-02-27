import flet as ft
from models.schedule import WeeklySchedule
from models.lecture import Lecture
from views.schedule_view import ScheduleView
from views.add_lecture_view import AddLectureView

def main(page: ft.Page):
    page.title = "מערכת שעות"
    page.rtl = True
    page.theme_mode = ft.ThemeMode.LIGHT
    
    my_schedule = WeeklySchedule()
    dummy_lec = Lecture("1", "פיתוח אפליקציות", "בוט חכם", "ראשון", "09:00", "11:00", "מעבדה 1")
    my_schedule.add_lecture(dummy_lec)

    def change_screen(screen_name):
        # SPA approach: manipulate controls instead of page.views 
        # to prevent Linux FlutterEngine GTK/OpenGL crashes.
        page.controls.clear() 
        
        if screen_name == "schedule":
            page.controls.append(ScheduleView(page, my_schedule, change_screen))
        elif screen_name == "add":
            page.controls.append(AddLectureView(page, my_schedule, change_screen))
            
        page.update()

    change_screen("schedule")

if __name__ == "__main__":
    ft.run(main)