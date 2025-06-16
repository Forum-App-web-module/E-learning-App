ALTER TABLE v1.course_sections
ADD CONSTRAINT fk_course_id
FOREIGN KEY (course_id) REFERENCES v1.courses(id)
ON DELETE CASCADE;
