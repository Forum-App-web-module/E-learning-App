ALTER TABLE IF EXISTS v1.enrollments
    ADD CONSTRAINT unique_student_course UNIQUE (student_id, course_id);