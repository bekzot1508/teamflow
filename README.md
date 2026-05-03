# 🧠 PROJECT DESCRIPTION (READY

TeamFlow — Project Management System (Jira/Trello-like)

- Designed and built a scalable backend using Django and Django REST Framework
- Implemented multi-tenant architecture with Workspaces, Projects, and Tasks
- Developed Kanban-style task management with column-based status transitions
- Applied RBAC system (Owner, Admin, Member, Viewer) with strict permission checks
- Built service layer architecture for clean separation of business logic
- Implemented notification system with mentions and deadline reminders
- Integrated Celery + Redis for async tasks (email notifications, reminders)
- Ensured data consistency using transaction.atomic and row-level locking
- Wrote 80+ automated tests (services, API, permissions, concurrency scenarios)
- Optimized database queries using select_related and prefetch_related
- Deployed production-ready app on Render with Docker setup


## Live Demo

🌐 https://teamflow-05uo.onrender.com

Admin panel:
https://teamflow-05uo.onrender.com/admin/

API Docs:
https://teamflow-05uo.onrender.com/api/v1/docs/


## Celery (Async Tasks)

Celery and Redis are configured for:
- email notifications
- deadline reminders

⚠️ Note:
Background workers require a paid instance on Render.
Locally, Celery runs via Docker.



---

# 🧠 GITHUB DESCRIPTION (READY)

Repo description:

```text
Production-ready Django backend with RBAC, Kanban task management, 
DRF API, Celery (local), and 80+ automated tests.
```

## Testing

Run tests:

```bash
docker compose exec web pytest
```


## Screenshots

### Dashboard
![Dashboard](docs/screenshots/dashboard.png)

### Workspaces
![Workspaces](docs/screenshots/workspace.png)

### Projects
![Projects](docs/screenshots/project.png)

### Kanban Board
![Kanban](docs/screenshots/kanban.png)

### Task Detail
![Task](docs/screenshots/task_detail.png)

### Notifications
![Notifications](docs/screenshots/notifications.png)

### API Docs
![Swagger](docs/screenshots/swagger.png)

### Admin
![Admin](docs/screenshots/admin.png)