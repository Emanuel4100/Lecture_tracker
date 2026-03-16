import json
import os
from datetime import datetime, timedelta
from models.course import Course
from utils.i18n import translator

class SemesterSchedule:
    def __init__(self):
        self.courses = []
        self.semester_start = None
        self.semester_end = None
        self.language = "he"
        self.show_weekend = False
        self.data_file = "my_schedule_data.json"
        self.enable_meeting_numbers = True

    def is_semester_set(self):
        return self.semester_start is not None and self.semester_end is not None

    def _safe_parse_date(self, d):
        """פונקציה חכמה שממירה תאריכים מכל פורמט אפשרי ומונעת קריסות"""
        if not d:
            return None
        if hasattr(d, 'date'):
            return d.date()
        if isinstance(d, str):
            # מנקה רווחים אם יש
            d = d.strip()
            # מנסה כמה תבניות שונות של תאריכים
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S"):
                try:
                    # מנסה לחלץ רק את 10 התווים הראשונים אם הפורמט קצר
                    test_str = d[:10] if len(fmt) <= 10 else d
                    return datetime.strptime(test_str, fmt).date()
                except ValueError:
                    continue
        return d

    def set_semester(self, start_date, end_date):
        self.semester_start = self._safe_parse_date(start_date)
        self.semester_end = self._safe_parse_date(end_date)

    def add_course(self, course):
        self.courses.append(course)

    def get_all_lectures(self):
        all_lecs = []
        for c in self.courses:
            all_lecs.extend(c.lectures)
        all_lecs.sort(key=lambda l: (l.date_obj, l.start_time if l.start_time else "00:00"))
        return all_lecs

    def get_weekly_lectures(self, target_date):
        idx = (target_date.weekday() + 1) % 7
        sun = target_date - timedelta(days=idx)
        end_day = sun + timedelta(days=6)
        
        weekly = []
        for lec in self.get_all_lectures():
            if sun <= lec.date_obj <= end_day:
                weekly.append(lec)
        return weekly

    def get_pending_lectures(self):
        today = datetime.now().date()
        return [l for l in self.get_all_lectures() if l.status == "status.needs_watching" and l.date_obj <= today]

    def get_past_lectures(self):
        today = datetime.now().date()
        return [l for l in self.get_all_lectures() if l.date_obj < today and l.status != "status.needs_watching"]

    def get_future_lectures(self):
        today = datetime.now().date()
        return [l for l in self.get_all_lectures() if l.date_obj > today]

    def to_dict(self):
        return {
            "semester_start": self.semester_start.strftime("%Y-%m-%d") if self.semester_start else None,
            "semester_end": self.semester_end.strftime("%Y-%m-%d") if self.semester_end else None,
            "language": self.language,
            "show_weekend": self.show_weekend,
            "enable_meeting_numbers": self.enable_meeting_numbers,
            "courses": [c.to_dict() for c in self.courses]
        }

    def load_from_file(self):
        if not os.path.exists(self.data_file):
            return False
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # שימוש בפונקציה החכמה לחילוץ התאריכים (מונע קריסה גם אם הקובץ הישן נשמר בפורמט שונה)
                self.semester_start = self._safe_parse_date(data.get("semester_start"))
                self.semester_end = self._safe_parse_date(data.get("semester_end"))
                
                self.language = data.get("language", "he")
                self.show_weekend = data.get("show_weekend", False)
                self.enable_meeting_numbers = data.get("enable_meeting_numbers", True)
                translator.set_language(self.language)
                
                self.courses = []
                for c_data in data.get("courses", []):
                    self.courses.append(Course.from_dict(c_data))
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False

    def save_to_file(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.update(self.to_dict(), f, ensure_ascii=False, indent=4)
        except:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                f.write(json.dumps(self.to_dict(), ensure_ascii=False, indent=4))