import flet as ft
from models.lecture import LectureStatus
from utils.i18n import t
from utils.theme import AppTheme

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
        
        self.shadow = ft.BoxShadow(spread_radius=0, blur_radius=2, color=ft.Colors.SHADOW, offset=ft.Offset(0, 1))

        status_colors = {
            LectureStatus.ATTENDED: AppTheme.STATUS_ATTENDED,
            LectureStatus.WATCHED_RECORDING: AppTheme.STATUS_WATCHED,
            LectureStatus.NEEDS_WATCHING: AppTheme.STATUS_PENDING,
            LectureStatus.SKIPPED: AppTheme.STATUS_SKIPPED,
            LectureStatus.CANCELLED: AppTheme.STATUS_CANCELLED
        }
        b_color = status_colors.get(self.lecture.status, ft.Colors.TRANSPARENT)
        self.border = ft.border.all(1.5, b_color) if b_color != ft.Colors.TRANSPARENT else None

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
                color=ft.Colors.ON_SURFACE, 
                text_align="center", 
                max_lines=3, 
                overflow=ft.TextOverflow.ELLIPSIS
            )
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)

    def build_detailed_view(self):
        title = ft.Text(self.lecture.title, weight="w600", size=13, color=ft.Colors.ON_SURFACE, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS)
        
        time_elements = []
        if self.show_date:
            time_elements.extend([
                ft.Image(src="icons/calendar_month.svg", width=14, height=14, color=ft.Colors.PRIMARY),
                ft.Text(self.lecture.date_str, color=ft.Colors.PRIMARY, size=12, weight="bold"),
                ft.Container(width=10)
            ])
            
        time_elements.extend([
            ft.Image(src="icons/access_time.svg", width=12, height=12, color=ft.Colors.ON_SURFACE_VARIANT),
            ft.Text(f"{self.lecture.start_time}-{self.lecture.end_time}", color=ft.Colors.ON_SURFACE_VARIANT, size=11),
            ft.Container(width=4),
            ft.Image(src="icons/location_on.svg", width=12, height=12, color=ft.Colors.ON_SURFACE_VARIANT),
            ft.Text(self.lecture.room, color=ft.Colors.ON_SURFACE_VARIANT, size=11, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS)
        ])

        time_room = ft.Row(time_elements, spacing=2, alignment=ft.MainAxisAlignment.START)

        return ft.Column([
            title, time_room, ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT), self.build_status_icons()
        ], spacing=6)

    def build_status_icons(self):
        def create_icon(icon_name, status_value, tooltip_text, active_color):
            is_active = (self.lecture.status == status_value)
            def on_status_click(e):
                self.lecture.status = status_value
                if self.update_callback: self.update_callback()

            return ft.Container(
                content=ft.Image(src=f"icons/{icon_name}.svg", width=18, height=18, color=active_color if is_active else ft.Colors.OUTLINE),
                tooltip=tooltip_text,
                bgcolor=ft.Colors.SURFACE if is_active else ft.Colors.TRANSPARENT,
                border_radius=20,
                padding=6,
                on_click=on_status_click
            )

        return ft.Row([
            create_icon("check_circle", LectureStatus.ATTENDED, t("status.attended_short"), AppTheme.STATUS_ATTENDED),
            create_icon("smart_display", LectureStatus.WATCHED_RECORDING, t("status.watched_short"), AppTheme.STATUS_WATCHED),
            create_icon("pending", LectureStatus.NEEDS_WATCHING, t("status.needs_watching_short"), AppTheme.STATUS_PENDING),
            create_icon("cancel", LectureStatus.SKIPPED, t("status.skipped_short"), AppTheme.STATUS_SKIPPED),
            create_icon("block", LectureStatus.CANCELLED, t("status.cancelled_short"), AppTheme.STATUS_CANCELLED),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    def build_popup_content(self):
        title = ft.Text(self.lecture.title, weight="bold", size=18, color=ft.Colors.ON_SURFACE, text_align="center")
        
        loc_text = f" | {self.lecture.room}" if self.lecture.room else ""
        date_text = f"{self.lecture.date_str} | " if self.show_date else ""
        
        time_room = ft.Row([
            ft.Image(src="icons/schedule.svg", width=16, height=16, color=ft.Colors.ON_SURFACE_VARIANT),
            ft.Text(f"{date_text}{self.lecture.start_time} - {self.lecture.end_time}{loc_text}", color=ft.Colors.ON_SURFACE_VARIANT, size=14)
        ], alignment=ft.MainAxisAlignment.CENTER)

        options = [
            ("check_circle", LectureStatus.ATTENDED, t("status.attended"), AppTheme.STATUS_ATTENDED),
            ("smart_display", LectureStatus.WATCHED_RECORDING, t("status.watched"), AppTheme.STATUS_WATCHED),
            ("pending", LectureStatus.NEEDS_WATCHING, t("status.needs_watching"), AppTheme.STATUS_PENDING),
            ("cancel", LectureStatus.SKIPPED, t("status.skipped"), AppTheme.STATUS_SKIPPED),
            ("block", LectureStatus.CANCELLED, t("status.cancelled"), AppTheme.STATUS_CANCELLED),
        ]

        buttons = []
        for icon_name, status_value, text_label, active_color in options:
            is_active = (self.lecture.status == status_value)
            def make_click_handler(stat_val):
                def on_click(e):
                    self.lecture.status = stat_val
                    if self.update_callback: self.update_callback()
                    if self.current_dialog: self.current_dialog.open = False; e.page.update()
                return on_click

            btn = ft.Container(
                content=ft.Row([
                    ft.Image(src=f"icons/{icon_name}.svg", width=22, height=22, color=active_color if is_active else ft.Colors.ON_SURFACE_VARIANT),
                    ft.Text(text_label, size=15, weight="bold" if is_active else "normal", color=active_color if is_active else ft.Colors.ON_SURFACE)
                ], alignment=ft.MainAxisAlignment.START),
                padding=10, border_radius=8,
                bgcolor=ft.Colors.SURFACE if is_active else ft.Colors.TRANSPARENT,
                border=ft.border.all(2, active_color) if is_active else ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                on_click=make_click_handler(status_value), ink=True
            )
            buttons.append(btn)

        return ft.Column([
            title, time_room, ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT), ft.Column(buttons, spacing=8)
        ], spacing=10, tight=True)

    def open_popup(self, e):
        def close_dlg(args):
            self.current_dialog.open = False; e.page.update()

        self.current_dialog = ft.AlertDialog(
            content=ft.Container(content=self.build_popup_content(), width=320, padding=10),
            shape=ft.RoundedRectangleBorder(radius=15),
            bgcolor=self.lecture.course_color,
            actions=[ft.TextButton(t("common.back", default="חזור"), on_click=close_dlg)],
            actions_alignment=ft.MainAxisAlignment.END
        )
        e.page.overlay.append(self.current_dialog); self.current_dialog.open = True; e.page.update()