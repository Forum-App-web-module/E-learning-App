ALTER TABLE v1.students_course_sections
ADD CONSTRAINT unique_student_section UNIQUE (students_id, course_sections_id);