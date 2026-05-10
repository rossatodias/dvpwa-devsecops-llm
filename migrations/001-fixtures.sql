INSERT INTO users (
  first_name,
  middle_name,
  last_name,
  username,
  pwd_hash,
  is_admin
)
VALUES
  ('Super', NULL, 'Admin', 'superadmin', '$2b$04$PgHLA6dMFRqDrMSBQ8tUbeb8k7Wc8tLX2gMvqOJpyK4/WoQtfwDYW', TRUE),
  ('John', 'William', 'Doe', 'j.doe', '$2b$04$Z5iNPI8DLWW8nrFbN2AQJOyx2BgWZnW0lVuUqW2RUqso7AbG85vNK', FALSE),
  ('Stephen', NULL, 'King', 's.king', '$2b$04$Z5iNPI8DLWW8nrFbN2AQJOyx2BgWZnW0lVuUqW2RUqso7AbG85vNK', FALSE),
  ('Peter', NULL, 'Parker', 'p.parker', '$2b$04$Itdgsk/W5DHiYrt0pjsFG.oVuxNoNB9CHdx1N.CXmk2v/Vg69m4/2', FALSE);

INSERT INTO students (name) VALUES
  ('Chuck'), ('James'), ('Thor'), ('Clint'),
  ('Richie'), ('Bill'), ('Ben'), ('Eddie');

INSERT INTO courses (title, description) VALUES
  ('Math', '2+2 = 5'),
  ('Grammar', 'Wi learn haw tu write korektli'),
  ('Physics', 'E=mc^2');

INSERT INTO marks(student_id, course_id, points) VALUES
  (1, 1, 4), (1, 1, 5), (1, 1, 3), (1, 1, 4),
  (1, 2, 2), (1, 2, 3), (1, 3, 5), (1, 3, 5);
