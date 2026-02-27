import flet as ft
from models.schedule import WeeklySchedule
from models.lecture import Lecture
from views.schedule_view import ScheduleView
from views.add_lecture_view import AddLectureView

def main(page: ft.Page):
    page.title = "מערכת שעות"
    page.rtl = True # הגדרה קריטית לעברית (מימין לשמאל)
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # אתחול הלוח השבועי והכנסת הרצאה אחת לדוגמה
    my_schedule = WeeklySchedule()
    dummy_lec = Lecture("1", "פיתוח אפליקציות", "בוט חכם", "ראשון", "09:00", "11:00", "מעבדה 1")
    my_schedule.add_lecture(dummy_lec)

    def route_change(route):
        page.views.clear()
        
        # ניתוב לעמודים השונים
        if page.route == "/":
            page.views.append(ScheduleView(page, my_schedule))
        elif page.route == "/add":
            page.views.append(AddLectureView(page, my_schedule))
            
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    page.go("/")

if __name__ == "__main__":
    ft.app(target=main)