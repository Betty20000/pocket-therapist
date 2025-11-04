# 🧠 PocketTherapist — AI-Powered Emotional Support Agent

PocketTherapist is a Django + Gemini AI-based agent that detects negative sentiments, provides empathetic reframes, and helps users reflect on their emotional well-being.  
It integrates seamlessly with **Telex.im** using the **A2A protocol** for conversational workflows.

---

## 🚀 Features

- 🤖 **AI-Powered Cognitive Reframing** via Gemini 2.5
- 🧭 **Automatic Sentiment Detection**
- 💬 **Conversational Logging (A2A Message Model)**
- ❤️ **Crisis Risk Detection**
- 📈 **Weekly Summary Generation**
- 🌐 **Telex Integration (A2A Workflow)**
- 🗃️ **PostgreSQL-ready for production, SQLite for local development**

---

## 🧩 Tech Stack

- **Backend:** Django 5 + Django REST Framework
- **Database:** SQLite (local) / PostgreSQL (production)
- **AI API:** Google Gemini (via `google-generativeai`)
- **Deployment:** Leapcell
- **Integration:** Telex.im A2A Protocol

---

## ⚙️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/Betty20000/pocket-therapist.git
cd pocket-therapist
```

### 2. Create and Activate Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # on Windows
# or
source venv/bin/activate  # on Mac/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a `.env` file in the project root and add:

```
DEBUG=True
SECRET_KEY=your-secret-key
GEMINI_API_KEY=your-gemini-api-key

# Local DB (SQLite)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# Production (Leapcell / PostgreSQL)
DB_ENGINE_PROD=django.db.backends.postgresql
DB_NAME_PROD=yourdbname
DB_USER_PROD=youruser
DB_PASSWORD_PROD=yourpassword
DB_HOST_PROD=yourdbhost
DB_PORT_PROD=5432
```

### 5. Apply Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Run the Server
```bash
python manage.py runserver
```

Visit: [http://127.0.0.1:8000/a2a/pockettherapist/](http://127.0.0.1:8000/a2a/pockettherapist/)

---

## 🧠 Telex Integration (A2A Workflow)

To connect PocketTherapist with Telex:

1. Go to your Telex dashboard and create a **new A2A Workflow**.  
2. Use this URL as the agent endpoint:  
   ```
   https://<your-leapcell-deployment-url>/a2a/pockettherapist/
   ```

3. Example JSON workflow node:
   ```json
   {
     "id": "pockettherapist_agent",
     "name": "PocketTherapist Agent",
     "parameters": {},
     "position": [816, -112],
     "type": "a2a/mastra-a2a-node",
     "typeVersion": 1,
     "url": "https://<your-leapcell-deployment-url>/a2a/pockettherapist/"
   }
   ```

To view your logs:
```
https://api.telex.im/agent-logs/{channel-id}.txt
```

---

## 🧾 Example API Usage

**POST** `/a2a/pockettherapist/`  
Request body:
```json
{
  "user_id": "01989dec-0d08-71ee-9017-00e4556e1942",
  "message": "I feel so tired and sad lately."
}
```

Response:
```json
{
  "response": "I’m sorry you’re feeling that way. It sounds like you’re struggling. This might be a bit of emotional exhaustion. Try to take a break and do something soothing."
}
```

---

## 📦 Deployment on Leapcell

1. Push your code to GitHub.
2. Connect your GitHub repo on [Leapcell.io](https://leapcell.io).
3. Add environment variables under **Settings → Environment Variables**.
4. Set `DEBUG=False` and configure PostgreSQL variables.
5. Deploy your app and copy the public URL.
6. Use that URL in your Telex A2A node configuration.

---

## 🧰 Folder Structure

```
pockettherapist/
│
├── agent/
│   ├── models.py
│   ├── utils.py
│   ├── views.py
│   ├── urls.py
│
├── pockettherapist/
│   ├── settings.py
│   ├── urls.py
│
├── manage.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

---

## 🧡 Author

**Beatrice Gachigi**  
Backend Developer (HNG Backend Wizards)  
Stack: Django | REST Framework | PostgreSQL | ReactJS  
🔗 [LinkedIn](https://linkedin.com) | 🌐 [GitHub](https://github.com/Betty20000)

---

© 2025 PocketTherapist. All rights reserved.
