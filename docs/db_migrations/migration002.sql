ALTER TABLE subscriptions
ADD CONSTRAINT unique_student_subscription UNIQUE (student_id);