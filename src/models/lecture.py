
class Course:
    def __init__(self,course_name,course_id,weekly_hours,info_link = None):
        self.course_name = course_name 
        self.course_id  = course_id 
        self.weekly_hours = weekly_hours
        self.info_link = info_link
        
        
        
class Lecture:
    def __init__(self, id, title, lecturer, day, start_time, end_time, room):
        self.id = id
        self.title = title
        self.lecturer = lecturer
        self.day = day
        self.start_time = start_time
        self.end_time = end_time
        self.room = room