import flet as ft
from models.lecture import LectureStatus
from utils.i18n import t

class LectureCard(ft.Container):
    def __init__(self, lecture, update_callback, is_mobile=False, show_date=False):
        super().__init__()
        self.lecture = lecture
        self.update_callback = update_callback 
        self.is_mobile = is_mobile
        self.show_date = show_date
        self.current_dialog = None
        
        self.border_radius = 8 if self.is_mobile else 12
        self.padding = 4 if self.is_mobile else 8
        self.margin = ft.margin.only(bottom=5 if self.is_mobile else 8)
        self.bgcolor = self.lecture.course_color
        
        self.shadow = ft.BoxShadow(spread_radius=1, blur_radius=3, color="black12", offset=ft.Offset(0, 1))

        status_colors = {
            LectureStatus.ATTENDED: "green",
            LectureStatus.WATCHED_RECORDING: "blue",
            LectureStatus.NEEDS_WATCHING: "orange",
            LectureStatus.SKIPPED: "red400",
            LectureStatus.CANCELLED: "grey700"
        }
        b_color = status_colors.get(self.lecture.status, "transparent")
        self.border = ft.border.all(1.5, b_color) if b_color != "transparent" else None

        if self.is_mobile:
            self.content = self.build_compact_view()
            self.on_click = self.open_popup
            self.ink = True 
        else:
            self.content = self.build_detailed_view()

    def build_compact_view(self):
        short_title = self.lecture.title.split('-')[0].strip()
        return ft.Column([
            ft.Text(
                short_title, 
                weight="bold", 
                size=11, 
                color="black87", 
                text_align="center", 
                max_lines=3, 
                overflow=ft.TextOverflow.ELLIPSIS
            )
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)

    def build_detailed_view(self):
        title = ft.Text(self.lecture.title, weight="w600", size=13, color="black87", no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS)
        
        time_elements = []
        if self.show_date:
            time_elements.extend([
                ft.Image(src="icons/calendar_month.svg", width=14, height=14, color="#1976D2"),
                ft.Text(self.lecture.date_str, color="#1976D2", size=12, weight="bold"),
                ft.Container(width=10)
            ])
            
        time_elements.extend([
            ft.Image(src="icons/access_time.svg", width=12, height=12, color="black54"),
            ft.Text(f"{self.lecture.start_time}-{self.lecture.end_time}", color="black54", size=11),
            ft.Container(width=4),
            ft.Image(src="icons/location_on.svg", width=12, height=12, color="black54"),
            ft.Text(self.lecture.room, color="black54", size=11, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS)
        ])

        time_room = ft.Row(time_elements, spacing=2, alignment=ft.MainAxisAlignment.START)

        return ft.Column([
            title, time_room, ft.Divider(height=1, color="black12"), self.build_status_icons()
        ], spacing=6)

    def build_status_icons(self):
        def create_icon(icon_name, status_value, tooltip_text, active_color):
            is_active = (self.lecture.status == status_value)
            
            def on_status_click(e):
                self.lecture.status = status_value
                if self.update_callback:
                    self.update_callback()

            return ft.Container(
                content=ft.Image(src=f"icons/{icon_name}.svg", width=18, height=18, color=active_color if is_active else "black38"),
                tooltip=tooltip_text,
                bgcolor="white" if is_active else "transparent",
                border_radius=20,
                padding=6,
                on_click=on_status_click
            )

        # תצוגת אייקונים אופקית עבור מחשב/טאבלט
        return ft.Row([
            create_icon("check_circle", LectureStatus.ATTENDED, t("status.attended_short"), "green"),
            create_icon("smart_display", LectureStatus.WATCHED_RECORDING, t("status.watched_short"), "blue"),
            create_icon("pending", LectureStatus.NEEDS_WATCHING, t("status.needs_watching_short"), "orange"),
            create_icon("cancel", LectureStatus.SKIPPED, t("status.skipped_short"), "red400"),
            create_icon("block", LectureStatus.CANCELLED, t("status.cancelled_short"), "grey700"),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    def build_popup_content(self):
        title = ft.Text(self.lecture.title, weight="bold", size=18, color="black87", text_align="center")
        
        loc_text = f" | {self.lecture.room}" if self.lecture.room else ""
        date_text = f"{self.lecture.date_str} | " if self.show_date else ""
        
        time_room = ft.Row([
            ft.Image(src="icons/schedule.svg", width=16, height=16, color="black54"),
            ft.Text(f"{date_text}{self.lecture.start_time} - {self.lecture.end_time}{loc_text}", color="black54", size=14)
        ], alignment=ft.MainAxisAlignment.CENTER)

        options = [
            ("check_circle", LectureStatus.ATTENDED, t("status.attended"), "green"),
            ("smart_display", LectureStatus.WATCHED_RECORDING, t("status.watched"), "blue"),
            ("pending", LectureStatus.NEEDS_WATCHING, t("status.needs_watching"), "orange"),
            ("cancel", LectureStatus.SKIPPED, t("status.skipped"), "red400"),
            ("block", LectureStatus.CANCELLED, t("status.cancelled"), "grey700"),
        ]

        buttons = []
        for icon_name, status_value, text_label, active_color in options:
            is_active = (self.lecture.status == status_value)
            
            def make_click_handler(stat_val):
                def on_click(e):
                    self.lecture.status = stat_val
                    if self.update_callback:
                        self.update_callback()
                    if self.current_dialog:
                        self.current_dialog.open = False
                        e.page.update()
                return on_click

            btn = ft.Container(
                content=ft.Row([
                    ft.Image(src=f"icons/{icon_name}.svg", width=22, height=22, color=active_color if is_active else "black54"),
                    ft.Text(text_label, size=15, weight="bold" if is_active else "normal", color=active_color if is_active else "black87")
                ], alignment=ft.MainAxisAlignment.START),
                padding=10,
                border_radius=8,
                bgcolor="white" if is_active else "transparent",
                border=ft.border.all(2, active_color) if is_active else ft.border.all(1, "black12"),
                on_click=make_click_handler(status_value),
                ink=True
            )
            buttons.append(btn)

        return ft.Column([
            title,
            time_room,
            ft.Divider(height=1, color="black12"),
            ft.Column(buttons, spacing=8)
        ], spacing=10, tight=True)

    def open_popup(self, e):
        def close_dlg(args):
            self.current_dialog.open = False
            e.page.update()

        self.current_dialog = ft.AlertDialog(
            content=ft.Container(content=self.build_popup_content(), width=320, padding=10),
            shape=ft.RoundedRectangleBorder(radius=15),
            bgcolor=self.lecture.course_color,
            actions=[ft.TextButton(t("common.back", default="חזור"), on_click=close_dlg)],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        e.page.overlay.append(self.current_dialog)
        self.current_dialog.open = True
        e.page.update()