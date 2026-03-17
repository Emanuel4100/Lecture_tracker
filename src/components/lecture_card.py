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
        self.padding = 4 if self.is_mobile else 12  # קצת יותר ריווח לרשימה כדי שתנשום
        self.margin = ft.margin.only(bottom=5 if self.is_mobile else 8)
        self.shadow = ft.BoxShadow(spread_radius=0, blur_radius=2, color="shadow", offset=ft.Offset(0, 1))

        status_colors = {
            LectureStatus.ATTENDED: AppTheme.STATUS_ATTENDED,
            LectureStatus.WATCHED_RECORDING: AppTheme.STATUS_WATCHED,
            LectureStatus.NEEDS_WATCHING: AppTheme.STATUS_PENDING,
            LectureStatus.SKIPPED: AppTheme.STATUS_SKIPPED,
            LectureStatus.CANCELLED: AppTheme.STATUS_CANCELLED
        }
        b_color = status_colors.get(self.lecture.status, "transparent")
        
        # --- ההפרדה החכמה בין היומן לרשימה ---
        if self.is_mobile:
            # בלוח השבועי: שומרים על בלוק צבע מלא כדי שיראה כמו יומן
            self.bgcolor = self.lecture.course_color
            self.border = ft.border.all(1.5, b_color) if b_color != "transparent" else None
            self.content = self.build_compact_view()
            self.on_click = self.open_popup
            self.ink = True 
        else:
            # בלשונית ההרצאות: רקע נקי עם מסגרת עדינה
            self.bgcolor = "surface"
            self.border = ft.border.all(1.5, b_color) if b_color != "transparent" else ft.border.all(1, "outlineVariant")
            self.content = self.build_detailed_view()

    def build_compact_view(self):
        short_title = self.lecture.display_title.split('-')[0].strip()
        return ft.Column([
            ft.Text(short_title, weight="bold", size=11, color="onSurface", text_align="center", max_lines=3, overflow=ft.TextOverflow.ELLIPSIS)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)

    def build_detailed_view(self):
        # נגיעת הצבע: עיגול קטן ליד הכותרת במקום לצבוע את כל הכרטיסייה
        course_dot = ft.Container(width=12, height=12, border_radius=6, bgcolor=self.lecture.course_color)
        title = ft.Text(self.lecture.display_title, weight="bold", size=14, color="onSurface", no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS, expand=True)
        title_row = ft.Row([course_dot, title], spacing=8, alignment=ft.MainAxisAlignment.START)
        
        time_elements = []
        if self.show_date:
            time_elements.extend([
                ft.Image(src="icons/calendar_month.svg", width=14, height=14, color="primary"),
                ft.Text(self.lecture.date_str, color="primary", size=12, weight="bold"),
                ft.Container(width=10)
            ])
            
        if self.lecture.start_time and self.lecture.end_time:
            time_text = f"{self.lecture.start_time}-{self.lecture.end_time}"
        elif self.lecture.duration_mins:
            time_text = f"{self.lecture.duration_mins} min"
        else:
            time_text = t("lecture.custom_task", default="משימה")
            
        time_elements.extend([
            ft.Image(src="icons/access_time.svg", width=12, height=12, color="onSurfaceVariant"),
            ft.Text(time_text, color="onSurfaceVariant", size=11),
            ft.Container(width=4),
            ft.Image(src="icons/place.svg", width=12, height=12, color="onSurfaceVariant"),
            ft.Text(self.lecture.room if self.lecture.room else t("lecture.no_room", default="ללא מיקום"), color="onSurfaceVariant", size=11, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS)
        ])

        time_room = ft.Row(time_elements, spacing=4, alignment=ft.MainAxisAlignment.START)
        
        link_container = ft.Container()
        if self.lecture.external_link:
            link_container = ft.Row([
                ft.Image(src="icons/link.svg", width=12, height=12, color="primary"),
                ft.Text(t("lecture.attachment_included", default="מצורף קישור"), color="primary", size=11, italic=True)
            ])

        actions_row = ft.Row([
            self.build_single_status_button(),
            ft.Container(
                content=ft.Image(src="icons/edit.svg", width=18, height=18, color="primary"), 
                tooltip=t("lecture.edit_meeting", default="ערוך"), 
                on_click=self.open_edit_dialog,
                padding=8,
                border_radius=20,
                ink=True
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        return ft.Column([title_row, time_room, link_container, ft.Divider(height=1, color="outlineVariant"), actions_row], spacing=8)

    def build_single_status_button(self):
        options = [
            ("check_circle", LectureStatus.ATTENDED, t("status.attended"), AppTheme.STATUS_ATTENDED),
            ("smart_display", LectureStatus.WATCHED_RECORDING, t("status.watched"), AppTheme.STATUS_WATCHED),
            ("pending", LectureStatus.NEEDS_WATCHING, t("status.needs_watching"), AppTheme.STATUS_PENDING),
            ("cancel", LectureStatus.SKIPPED, t("status.skipped"), AppTheme.STATUS_SKIPPED),
            ("block", LectureStatus.CANCELLED, t("status.cancelled"), AppTheme.STATUS_CANCELLED),
        ]
        
        current_icon, current_color = "pending", AppTheme.STATUS_PENDING
        for icon_name, stat_val, label, color in options:
            if stat_val == self.lecture.status:
                current_icon, current_color = icon_name, color
                break

        def on_status_selected(e):
            self.lecture.status = e.control.data
            if self.update_callback: self.update_callback()

        items = []
        for icon_name, status_value, text_label, active_color in options:
            items.append(
                ft.PopupMenuItem(
                    data=status_value,
                    content=ft.Row([
                        ft.Image(src=f"icons/{icon_name}.svg", width=20, height=20, color=active_color),
                        ft.Text(text_label, color="onSurface", weight="bold" if status_value == self.lecture.status else "normal")
                    ]),
                    on_click=on_status_selected
                )
            )

        return ft.PopupMenuButton(
            content=ft.Container(
                content=ft.Row([
                    ft.Image(src=f"icons/{current_icon}.svg", width=18, height=18, color=current_color),
                    ft.Text(t(self.lecture.status), color=current_color, size=12, weight="bold")
                ], spacing=4),
                padding=ft.padding.symmetric(horizontal=10, vertical=5),
                bgcolor="surface", border_radius=20, border=ft.border.all(1, current_color)
            ),
            items=items, tooltip=t("lecture.change_status", default="שנה סטטוס")
        )

    def open_edit_dialog(self, e):
        link_input = ft.TextField(label=t("lecture.link_label", default="קישור"), value=self.lecture.external_link, width=280)
        dur_input = ft.TextField(label=t("lecture.duration_label", default="אורך"), value=str(self.lecture.duration_mins) if self.lecture.duration_mins else "", width=100, keyboard_type=ft.KeyboardType.NUMBER)
        
        def save_changes(args):
            self.lecture.external_link = link_input.value
            if dur_input.value.isdigit():
                self.lecture.duration_mins = int(dur_input.value)
            self.current_dialog.open = False
            e.page.update()
            if self.update_callback: self.update_callback()
            
        def close_dialog(args):
            self.current_dialog.open = False
            e.page.update()

        self.current_dialog = ft.AlertDialog(
            title=ft.Text(t("lecture.edit_meeting", default="ערוך")),
            content=ft.Column([
                ft.Text(t("lecture.update_details", default="פרטים:"), size=14), link_input, dur_input
            ], tight=True),
            actions=[
                ft.TextButton(t("common.cancel", default="ביטול"), on_click=close_dialog),
                ft.ElevatedButton(t("common.save", default="שמור"), on_click=save_changes, bgcolor="primary", color="onPrimary")
            ]
        )
        e.page.overlay.append(self.current_dialog); self.current_dialog.open = True; e.page.update()

    def build_popup_content(self):
        # גם בפופ-אפ במובייל: עברנו לעיצוב נקי עם עיגול צבע
        course_dot = ft.Container(width=14, height=14, border_radius=7, bgcolor=self.lecture.course_color)
        title_text = ft.Text(self.lecture.display_title, weight="bold", size=18, color="onSurface", text_align="center", expand=True)
        title_row = ft.Row([course_dot, title_text], alignment=ft.MainAxisAlignment.CENTER, spacing=8)
        
        link_container = ft.Text(f"Link: {self.lecture.external_link}", color="primary", size=12, italic=True) if self.lecture.external_link else ft.Container()

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
                    ft.Image(src=f"icons/{icon_name}.svg", width=22, height=22, color=active_color if is_active else "onSurfaceVariant"),
                    ft.Text(text_label, size=15, weight="bold" if is_active else "normal", color=active_color if is_active else "onSurface")
                ], alignment=ft.MainAxisAlignment.START),
                padding=10, border_radius=8, 
                bgcolor="surfaceVariant" if is_active else "transparent",
                border=ft.border.all(2, active_color) if is_active else ft.border.all(1, "outlineVariant"),
                on_click=make_click_handler(status_value), ink=True
            )
            buttons.append(btn)

        edit_btn = ft.TextButton(content=ft.Row([ft.Image(src="icons/edit.svg", width=18, height=18, color="primary"), ft.Text(t("lecture.edit_meeting", default="ערוך"), color="primary")], alignment=ft.MainAxisAlignment.CENTER), on_click=self.open_edit_dialog)

        return ft.Column([title_row, link_container, ft.Divider(height=1, color="outlineVariant"), ft.Column(buttons, spacing=8), edit_btn], spacing=10, tight=True)

    def open_popup(self, e):
        def close_dlg(args):
            self.current_dialog.open = False; e.page.update()

        self.current_dialog = ft.AlertDialog(
            content=ft.Container(content=self.build_popup_content(), width=320, padding=10),
            shape=ft.RoundedRectangleBorder(radius=15), 
            bgcolor="surface", # הרקע של הפופ-אפ הפך לנקי (לבן/אפור בהיר) במקום צבעוני
            actions=[ft.TextButton(t("common.back", default="חזור"), on_click=close_dlg)],
            actions_alignment=ft.MainAxisAlignment.END
        )
        e.page.overlay.append(self.current_dialog); self.current_dialog.open = True; e.page.update()