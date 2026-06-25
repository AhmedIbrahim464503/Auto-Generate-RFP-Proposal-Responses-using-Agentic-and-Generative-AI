# 05. Database Design

## Schema Design

### Users
- `id` (UUID, Primary Key)
- `email` (String, Unique)
- `name` (String)
- `role` (Enum: Admin, Writer, Reviewer)

### Projects (RFPs)
- `id` (UUID, Primary Key)
- `title` (String)
- `description` (Text)
- `status` (Enum: In_Progress, Under_Review, Completed)
- `created_at` (Timestamp)

### Questions
- `id` (UUID, Primary Key)
- `project_id` (UUID, Foreign Key)
- `question_text` (Text)
- `suggested_answer` (Text)
- `status` (Enum: Draft, Reviewed, Approved)
