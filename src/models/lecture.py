import datetime

class LectureStatus:
    ATTENDED = "הלכתי לראות"
    WATCHED_RECORDING = "ראיתי את ההקלטה"
    NEEDS_WATCHING = "צריך לראות את ההקלטה"
    SKIPPED = "לדלג / אין צורך"

class LectureSession:
    def __init__(self, session_id, title, lecturer, date_obj, start_time, end_time, room, status=LectureStatus.NEEDS_WATCHING):
        self.session_id = session_id
        self.title = title
        self.lecturer = lecturer
        self.date_obj = date_obj 
        self.start_time = start_time
        self.end_time = end_time
        self.room = room
        self.status = status

    @property
    def date_str(self):
        return self.date_obj.strftime("%d/%m/%Y")