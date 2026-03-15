import flet as ft

class AppTheme:
    SEED_COLOR = "#005CBB"

    @staticmethod
    def get_theme():
        return ft.Theme(
            color_scheme_seed=AppTheme.SEED_COLOR
            # הסרנו את visual_density כדי למנוע את השגיאה
        )

    STATUS_ATTENDED = ft.Colors.GREEN_600
    STATUS_WATCHED = ft.Colors.BLUE_600
    STATUS_PENDING = ft.Colors.ORANGE_600
    STATUS_SKIPPED = ft.Colors.ERROR
    STATUS_CANCELLED = ft.Colors.OUTLINE