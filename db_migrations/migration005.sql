ALTER TABLE v1.course_rating
ADD CONSTRAINT unique_student_course
UNIQUE (students_id, courses_id);
