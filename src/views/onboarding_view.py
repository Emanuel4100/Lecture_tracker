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
        
        self.build_ui()

    def build_ui(self):
        self.controls.clear()
        
        header = ft.Container(
            content=ft.Text("הגדרת סמסטר חדש", size=24, weight="bold", color="white"),
            bgcolor="#1976D2",
            padding=15,
            alignment=ft.Alignment(0, 0),
            border_radius=10
        )
        
        self.update_step_content()
        
        self.controls = [
            header,
            self.content_area
        ]

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
            ft.Text("בוא נגדיר יחד את הסמסטר החדש שלך בכמה צעדים פשוטים.", size=16, text_align="center"),
            ft.Container(height=30),
            ft.ElevatedButton("צור סמסטר חדש", on_click=self.next_step, bgcolor="#1976D2", color="white", width=200)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, expand=True)

    def build_semester_dates_screen(self):
        self.start_input = ft.TextField(label="תאריך התחלה (DD/MM/YYYY)", value="01/03/2026", text_align="center")
        self.end_input = ft.TextField(label="תאריך סיום (DD/MM/YYYY)", value="30/06/2026", text_align="center")
        
        return ft.Column([
            ft.Text("שלב 1: תאריכי הסמסטר", size=20, weight="bold", color="#1976D2"),
            ft.Text("מתי הסמסטר מתחיל ומתי הוא נגמר?"),
            ft.Container(height=20),
            self.start_input,
            self.end_input,
            ft.Container(height=20),
            ft.ElevatedButton("המשך לשלב הבא", on_click=self.save_dates_and_continue, bgcolor="#43A047", color="white")
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    def save_dates_and_continue(self, e):
        try:
            datetime.strptime(self.start_input.value, "%d/%m/%Y")
            datetime.strptime(self.end_input.value, "%d/%m/%Y")
            self.schedule.set_semester(self.start_input.value, self.end_input.value)
            self.next_step()
        except ValueError:
            snack = ft.SnackBar(ft.Text("שגיאה! אנא השתמש בפורמט DD/MM/YYYY"))
            self.app_page.snack_bar = snack
            snack.open = True
            self.app_page.update()

    def build_initial_courses_screen(self):
        self.c_title = ft.TextField(label="שם הקורס", width=180)
        self.c_lecturer = ft.TextField(label="מרצה", width=180)
        
        self.c_day = ft.Dropdown(
            label="יום", 
            options=[ft.dropdown.Option(d) for d in ["ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי"]], 
            width=100
        )
        self.c_start = ft.TextField(label="התחלה", value="10:00", width=80)
        self.c_end = ft.TextField(label="סיום", value="12:00", width=80)
        self.c_room = ft.TextField(label="חדר", width=80)
        
        self.temp_meetings_view = ft.ListView(height=80, spacing=5)
        self.added_courses_list = ft.ListView(height=120, spacing=5)

        return ft.Column([
            ft.Text("שלב 2: הוספת קורסים (אופציונלי)", size=20, weight="bold", color="#1976D2"),
            ft.Text("הוסף קורס, הגדר את המפגשים שלו (הרצאות/תרגולים), ושמור."),
            
            ft.Row([self.c_title, self.c_lecturer], alignment=ft.MainAxisAlignment.CENTER, wrap=True),
            ft.Row([self.c_day, self.c_start, self.c_end, self.c_room], alignment=ft.MainAxisAlignment.CENTER, wrap=True),
            
            ft.Row([
                ft.ElevatedButton("➕ הוסף מפגש", on_click=self.add_meeting_to_temp, bgcolor="#F57C00", color="white")
            ], alignment=ft.MainAxisAlignment.CENTER),
            
            self.temp_meetings_view,
            
            ft.Row([
                ft.ElevatedButton("✅ שמור קורס זה לסמסטר", on_click=self.save_temp_course, bgcolor="#1976D2", color="white")
            ], alignment=ft.MainAxisAlignment.CENTER),
            
            ft.Divider(),
            ft.Text("קורסים שנוספו בהצלחה:", weight="bold"),
            self.added_courses_list,
            
            ft.Row([
                ft.ElevatedButton("המשך לשלב הבא", on_click=self.next_step, bgcolor="#43A047", color="white")
            ], alignment=ft.MainAxisAlignment.CENTER)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO)

    def add_meeting_to_temp(self, e):
        if not self.c_day.value:
            return
        
        meeting = {
            "day": self.c_day.value,
            "start": self.c_start.value,
            "end": self.c_end.value,
            "room": self.c_room.value
        }
        self.current_course_meetings.append(meeting)
        
        self.temp_meetings_view.controls.append(
            ft.Text(f"📌 יום {meeting['day']}, {meeting['start']}-{meeting['end']} (חדר: {meeting['room']})", color="#F57C00", size=13)
        )
        self.app_page.update()

    def save_temp_course(self, e):
        if not self.c_title.value or len(self.current_course_meetings) == 0:
            snack = ft.SnackBar(ft.Text("שגיאה! חובה להזין שם קורס ולפחות מועד אחד."))
            self.app_page.snack_bar = snack
            snack.open = True
            self.app_page.update()
            return
            
        new_course = Course(
            course_id=str(time.time()),
            title=self.c_title.value,
            lecturer=self.c_lecturer.value if self.c_lecturer.value else "לא הוגדר"
        )
        
        for m in self.current_course_meetings:
            new_course.add_weekly_meeting(
                semester_start=self.schedule.semester_start,
                semester_end=self.schedule.semester_end,
                day_name=m["day"],
                start_time=m["start"],
                end_time=m["end"],
                room=m["room"]
            )
            
        self.schedule.add_course(new_course)
        
        self.added_courses_list.controls.append(
            ft.Text(f"✅ קורס '{self.c_title.value}' נוסף עם {len(self.current_course_meetings)} מפגשים", color="green")
        )
        
        self.c_title.value = ""
        self.c_lecturer.value = ""
        self.current_course_meetings = []
        self.temp_meetings_view.controls.clear()
        self.app_page.update()

    def build_notifications_setup_screen(self):
        options = [ft.dropdown.Option(str(m)) for m in [0, 5, 10, 15, 30, 60]]
        
        self.notif_before = ft.Dropdown(label="דקות התראה לפני שיעור", options=options, value="15", width=200)
        self.notif_after = ft.Dropdown(label="דקות לשאלה האם הלכת", options=options, value="15", width=200)

        return ft.Column([
            ft.Text("שלב 3: הגדרות התראות", size=20, weight="bold", color="#1976D2"),
            ft.Text("מתי נזכיר לך על הרצאות?"),
            ft.Container(height=20),
            self.notif_before,
            self.notif_after,
            ft.Container(height=20),
            ft.ElevatedButton("המשך להדרכה", on_click=self.save_notifications_and_continue, bgcolor="#43A047", color="white")
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    def save_notifications_and_continue(self, e):
        self.schedule.set_notifications(self.notif_before.value, self.notif_after.value)
        self.next_step()

    def build_tutorial_screen(self):
        return ft.Column([
            ft.Text("שלב 4: איך זה עובד?", size=20, weight="bold", color="#1976D2"),
            ft.Container(height=10),
            
            ft.Container(
                content=ft.Row([ft.Text("➕", size=24), ft.Text("לחיצה על ה- + כדי להוסיף קורסים בהמשך", size=16)]),
                bgcolor="#FFF3E0", padding=10, border_radius=8
            ),
            ft.Text("⬇️", size=24, color="grey"),
            ft.Container(
                content=ft.Row([ft.Text("👆", size=24), ft.Text("לחץ על הסטטוס בכרטיסיה כדי לשנות אותו", size=16)]),
                bgcolor="#E3F2FD", padding=10, border_radius=8
            ),
            ft.Text("⬇️", size=24, color="grey"),
            ft.Container(
                content=ft.Row([ft.Text("✅", size=24), ft.Text("צבע ירוק = הלכתי/ראיתי\nצבע אדום = דילגתי", size=16)]),
                bgcolor="#E8F5E9", padding=10, border_radius=8
            ),
            
            ft.Container(height=20),
            ft.ElevatedButton("סיום - התחל להשתמש באפליקציה!", on_click=lambda _: self.change_screen("schedule"), bgcolor="#1976D2", color="white", width=280)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)