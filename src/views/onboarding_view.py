import flet as ft
import time
from datetime import datetime
from models.course import Course

class OnboardingView(ft.Column):
    def __init__(self, page: ft.Page, schedule, change_screen_func):
        super().__init__(expand=True)
        self.app_page = page
        self.schedule = schedule
        self.change_screen = change_screen_func
        
        self.current_step = 0
        self.current_course_meetings = [] 
        self.content_area = ft.Container(expand=True, padding=20)
        
        self.start_picker = ft.DatePicker(on_change=self.start_date_changed)
        self.end_picker = ft.DatePicker(on_change=self.end_date_changed)
        if self.start_picker not in self.app_page.overlay:
            self.app_page.overlay.extend([self.start_picker, self.end_picker])
            
        self.start_text = ft.Text("לא נבחר", size=16, weight="bold", color="#1976D2")
        self.end_text = ft.Text("לא נבחר", size=16, weight="bold", color="#1976D2")
        
        self.build_ui()

    def build_ui(self):
        self.controls.clear()
        header = ft.Container(content=ft.Text("הגדרת סמסטר חדש", size=24, weight="bold", color="white"), bgcolor="#1976D2", padding=15, alignment=ft.Alignment(0, 0), border_radius=10)
        self.update_step_content()
        self.controls = [header, self.content_area]

    def next_step(self, e=None):
        self.current_step += 1
        self.update_step_content()
        self.update()

    def update_step_content(self):
        if self.current_step == 0:
            self.content_area.content = self.build_welcome_screen()
        elif self.current_step == 1:
            self.content_area.content = self.build_semester_dates_screen()
        elif self.current_step == 2:
            self.content_area.content = self.build_initial_courses_screen()
        elif self.current_step == 3:
            self.content_area.content = self.build_notifications_setup_screen()
        elif self.current_step == 4:
            self.content_area.content = self.build_tutorial_screen()

    def build_welcome_screen(self):
        return ft.Column([
            ft.Text("🎓", size=80), 
            ft.Text("ברוך הבא למעקב ההרצאות!", size=22, weight="bold", text_align="center"),
            ft.Container(height=30),
            ft.ElevatedButton("צור סמסטר חדש", on_click=self.next_step, bgcolor="#1976D2", color="white", width=200)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, expand=True)

    def open_picker(self, picker):
        picker.open = True
        self.app_page.update()

    def start_date_changed(self, e):
        if self.start_picker.value:
            self.start_text.value = self.start_picker.value.strftime("%d/%m/%Y")
            self.update()

    def end_date_changed(self, e):
        if self.end_picker.value:
            self.end_text.value = self.end_picker.value.strftime("%d/%m/%Y")
            self.update()

    def build_semester_dates_screen(self):
        return ft.Column([
            ft.Text("שלב 1: תאריכי הסמסטר", size=20, weight="bold", color="#1976D2"),
            ft.Container(height=20),
            ft.Row([ft.ElevatedButton(content=ft.Row([ft.Text("📅"), ft.Text("בחר התחלה")]), on_click=lambda _: self.open_picker(self.start_picker)), self.start_text], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=10),
            ft.Row([ft.ElevatedButton(content=ft.Row([ft.Text("📅"), ft.Text("בחר סיום")]), on_click=lambda _: self.open_picker(self.end_picker)), self.end_text], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=30),
            ft.ElevatedButton("המשך לשלב הבא", on_click=self.save_dates_and_continue, bgcolor="#43A047", color="white")
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    def save_dates_and_continue(self, e):
        if self.start_text.value == "לא נבחר" or self.end_text.value == "לא נבחר":
            self.app_page.snack_bar = ft.SnackBar(ft.Text("חובה לבחור תאריכים!"))
            self.app_page.snack_bar.open = True
            self.app_page.update()
            return
        self.schedule.set_semester(self.start_text.value, self.end_text.value)
        self.next_step()

    def build_initial_courses_screen(self):
        self.c_title = ft.TextField(label="שם הקורס", width=180)
        self.c_room = ft.TextField(label="חדר", width=80)
        self.c_day = ft.Dropdown(label="יום", options=[ft.dropdown.Option(d) for d in ["ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי"]], width=100)
        
        times = [f"{h:02d}:{m:02d}" for h in range(8, 22) for m in (0, 30)]
        self.c_start = ft.Dropdown(label="התחלה", options=[ft.dropdown.Option(t) for t in times], width=100, value="10:00")
        self.c_dur = ft.Dropdown(label="אורך", options=[ft.dropdown.Option(key="1", text="שעה"), ft.dropdown.Option(key="2", text="שעתיים"), ft.dropdown.Option(key="3", text="3 שעות")], width=100, value="2")
        
        self.temp_meetings_view = ft.ListView(height=80, spacing=5)
        self.added_courses_list = ft.ListView(height=120, spacing=5)

        return ft.Column([
            ft.Text("שלב 2: הוספת קורסים (אופציונלי)", size=20, weight="bold", color="#1976D2"),
            ft.Row([self.c_title, self.c_room], alignment=ft.MainAxisAlignment.CENTER, wrap=True),
            ft.Row([self.c_day, self.c_start, self.c_dur], alignment=ft.MainAxisAlignment.CENTER, wrap=True),
            ft.ElevatedButton("➕ הוסף מפגש", on_click=self.add_meeting_to_temp, bgcolor="#F57C00", color="white"),
            self.temp_meetings_view,
            ft.ElevatedButton("✅ שמור קורס זה לסמסטר", on_click=self.save_temp_course, bgcolor="#1976D2", color="white"),
            ft.Divider(),
            self.added_courses_list,
            ft.ElevatedButton("המשך לשלב הבא", on_click=self.next_step, bgcolor="#43A047", color="white")
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO)

    def add_meeting_to_temp(self, e):
        if not self.c_day.value or not self.c_start.value: return
        dur = float(self.c_dur.value)
        h, m = map(int, self.c_start.value.split(':'))
        end_str = f"{h + int(dur) + (m + int((dur - int(dur))*60))//60:02d}:{(m + int((dur - int(dur))*60))%60:02d}"
        
        meeting = {"day": self.c_day.value, "start": self.c_start.value, "end": end_str, "room": self.c_room.value}
        self.current_course_meetings.append(meeting)
        self.temp_meetings_view.controls.append(ft.Text(f"📌 {meeting['day']}, {meeting['start']}-{meeting['end']}", color="#F57C00"))
        self.app_page.update()

    def save_temp_course(self, e):
        if not self.c_title.value or len(self.current_course_meetings) == 0: return
        new_course = Course(course_id=str(time.time()), title=self.c_title.value, lecturer="לא הוגדר")
        for m in self.current_course_meetings:
            new_course.add_weekly_meeting(self.schedule.semester_start, self.schedule.semester_end, m["day"], m["start"], m["end"], m["room"])
        self.schedule.add_course(new_course)
        self.added_courses_list.controls.append(ft.Text(f"✅ '{self.c_title.value}' נוסף", color="green"))
        self.current_course_meetings.clear()
        self.temp_meetings_view.controls.clear()
        self.c_title.value = ""
        self.app_page.update()

    def build_notifications_setup_screen(self):
        options = [ft.dropdown.Option(str(m)) for m in [0, 5, 10, 15, 30, 60]]
        self.notif_before = ft.Dropdown(label="התראה לפני (דקות)", options=options, value="15", width=150)
        return ft.Column([
            ft.Text("שלב 3: התראות", size=20, weight="bold", color="#1976D2"),
            self.notif_before,
            ft.Container(height=20),
            ft.ElevatedButton("המשך", on_click=lambda _: self.next_step(), bgcolor="#43A047", color="white")
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    def build_tutorial_screen(self):
        return ft.Column([
            ft.Text("שלב 4: בוא נתחיל!", size=20, weight="bold", color="#1976D2"),
            ft.Container(height=20),
            ft.ElevatedButton("סיום - למערכת השעות!", on_click=lambda _: self.change_screen("schedule"), bgcolor="#1976D2", color="white", width=280)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)