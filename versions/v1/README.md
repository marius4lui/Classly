# Classly v1.0.0

🎉 **Classly v1.0.0 is here!** 

Classly is the ultimate SaaS platform for managing school classes, timetables, and events. This release marks the first major version, including a complete Admin Dashboard, robust REST API, and powerful integration tools.

## 🚀 Features

### for Students & Teachers
- **Events & Homework**: Track homework (`HA`), exams (`KA`, `TEST`), and info (`INFO`).
- **Timetable**: Digital timetable with customizable slots and breaks.
- **Push Notifications**: Stay updated with mobile app integration (iOS/Android).

### for Class Admins
- **Admin Dashboard**: Manage users, roles, and class settings.
- **User Management**: Invite links, role promotion/demotion, and kick users.
- **Backup**: Download full database backups of your class data.
- **Login Tokens**: Generate one-time login tokens for easy onboarding.

### 🔌 Developer & Integration
- **API v1**: Robust, secure REST API with granular scopes (`events:read`, `events:write`, etc.).
- **Legacy Support**: Full backward compatibility with OAuth 2.0 flow.
- **API Keys**: Manage secure access keys via the Admin Dashboard (`/api-keys`).
- **AI Integration**: Dedicated Python Client and AI Skill for Agent integration.

## 📦 Getting Started

### Installation
```bash
git clone https://github.com/marius4lui/Classly.git
cd Classly
pip install -r requirements.txt
```

### Run Server
```bash
uvicorn app.main:app --reload
```

## 🤖 AI & Automation Assets

This release includes specialized tools for automating Classly:

- **`classly_client.py`**: A complete Python CLI and client library for the Classly API.
  - Usage: `python classly_client.py events list`
- **`SKILL.md`**: A definition file for AI Agents (Claude, GPT) to understand and control Classly.

## 📚 Documentation

Full documentation is available at **[docs.classly.site](https://docs.classly.site)**.
- [API Overview](https://docs.classly.site/development/api)
- [API v1 Reference](https://docs.classly.site/development/api-v1)
- [AI Integration Guide](https://docs.classly.site/development/api-integration)

---
*Built with ❤️ by the Classly Team.*
