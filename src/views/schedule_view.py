import flet as ft
from datetime import datetime, timedelta
from components.lecture_card import LectureCard

class ScheduleView(ft.Column):
    def __init__(self, page: ft.Page, schedule, change_screen_func):
        super().__init__(expand=True)
        self.app_page = page 
        self.schedule = schedule
        self.change_screen = change_screen_func

        self.tabs = ["לוח שבועי", "השלמות", "כל ההרצאות", "היסטוריה"]
        self.selected_tab = self.tabs[0]

        self.tabs_row = ft.Row(scroll=ft.ScrollMode.AUTO, alignment="center")
        self.content_area = ft.Container(expand=True)

        self.build_tabs()
        self.update_content()

        header = ft.Container(
            content=ft.Row([
                ft.TextButton(
                    content=ft.Text("⚙️ הגדרות", color="white", weight="bold"), 
                    on_click=lambda _: self.change_screen("settings")
                ),
                ft.Text("מעקב הרצאות", size=24, weight="bold", color="white"),
                ft.Container(width=80) 
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor="#1976D2",
            padding=15,
            border_radius=10
        )

        add_btn = ft.FloatingActionButton(
            content=ft.Text("+", size=30, color="white"),
            bgcolor="#F57C00", 
            shape=ft.RoundedRectangleBorder(radius=100),
            on_click=lambda _: self.change_screen("add")
        )

        self.controls = [
            header,
            self.tabs_row,
            self.content_area,
            ft.Row([add_btn], alignment="start")
        ]

    def build_tabs(self):
        self.tabs_row.controls.clear()
        for tab in self.tabs:
            is_selected = (tab == self.selected_tab)
            btn = ft.TextButton(
                content=ft.Text(
                    tab, 
                    color="#1976D2" if is_selected else "grey",
                    weight="bold" if is_selected else "normal"
                ),
                style=ft.ButtonStyle(
                    bgcolor="#E3F2FD" if is_selected else "transparent",
                    shape=ft.RoundedRectangleBorder(radius=8),
                ),
                on_click=self.create_tab_click_handler(tab)
            )
            self.tabs_row.controls.append(btn)

    def create_tab_click_handler(self, tab):
        def on_click(e):
            self.selected_tab = tab
            self.build_tabs()
            self.update_content()
            self.update()
        return on_click

    def refresh_ui(self):
        self.update_content()
        self.update()

    def build_weekly_grid(self):
        lectures = self.schedule.get_weekly_lectures()
        day_names = ["ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת"]
        day_columns = []
        
        today = datetime.now().date()
        idx = (today.weekday() + 1) % 7
        sun = today - timedelta(days=idx)

        for i in range(7):
            current_day_date = sun + timedelta(days=i)
            date_str = current_day_date.strftime("%d/%m")
            
            col_header = ft.Container(
                content=ft.Text(f"{day_names[i]}\n{date_str}", weight="bold", size=14, color="#1976D2", text_align="center"),
                alignment=ft.Alignment(0, 0),
                padding=5,
                bgcolor="#E3F2FD",
                border_radius=8
            )
            
            # עמודה לכל יום עם יכולת גלילה פנימית במקרה של הרבה הרצאות באותו יום
            day_columns.append(ft.Column([col_header], spacing=10, scroll=ft.ScrollMode.AUTO))

        for lec in lectures:
            lec_idx = (lec.date_obj.weekday() + 1) % 7
            day_columns[lec_idx].controls.append(LectureCard(lec, self.refresh_ui))

        grid_row = ft.Row(
            # expand=True מבטיח שכל עמודה תקבל בדיוק 1/7 מהמסך
            controls=[ft.Container(content=col, padding=2, expand=True) for col in day_columns],
            vertical_alignment="start",
            expand=True # הלוח תופס את כל הגובה הנותר
        )
        return grid_row

    def update_content(self):
        if self.selected_tab == "לוח שבועי":
            self.content_area.content = self.build_weekly_grid()
            return

        list_view = ft.ListView(expand=True, padding=20)
        
        if self.selected_tab == "השלמות":
            lectures = self.schedule.get_pending_lectures()
        elif self.selected_tab == "היסטוריה":
            lectures = self.schedule.get_history_lectures()
        else:
            lectures = self.schedule.get_all_lectures()
        
        if not lectures:
            list_view.controls.append(
                ft.Container(
                    content=ft.Text("אין הרצאות להציג כאן 🎉", size=16, color="grey"), 
                    alignment=ft.Alignment(0, 0), 
                    padding=50
                )
            )
        else:
            for lec in lectures:
                list_view.controls.append(LectureCard(lec, self.refresh_ui))
        
        self.content_area.content = list_view