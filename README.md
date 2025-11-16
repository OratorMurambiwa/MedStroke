# MedStroke 🧠⚕️

## 📘 Overview
MedStroke is a web application that enables doctors to send patient prompts to OpenAI's ChatGPT API. The model generates suggested treatment plans and clinical insights based on provided patient information. The application also includes ICD diagnosis code search functionality using fuzzy matching.

This project consists of:
- A **backend** (Python + FastAPI) that handles API requests and connects to OpenAI
- A **frontend** (HTML, Tailwind CSS, JavaScript) for doctors to input prompts and view AI-generated responses
 

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|-----------|
| **Backend** | Python, FastAPI |
| **Frontend** | HTML, Tailwind CSS, JavaScript |
| **Database** | SQLite / PostgreSQL |
| **AI/ML** | OpenAI API (ChatGPT) |
| **Search** | RapidFuzz (ICD code matching) |
| **Development** | Visual Studio Code, Google Colab |
| **Deployment** | Render, Replit |

---

## 📁 Project Structure
```
MedStroke/
├── README.md
├── requirements.txt
├── backend/
│   ├── main.py                 # FastAPI entry point
│   ├── requirements.txt         # Backend dependencies
│   ├── .env                     # Environment variables (not committed)
│   ├── models.py               # Database models
│   ├── utils.py                # Utility functions
│   └── ...other backend files
├── frontend/
│   ├── index.html              # Main page
│   ├── css/
│   │   └── styles.css          # Tailwind CSS styles
│   ├── js/
│   │   └── app.js              # JavaScript logic
│   └── ...other frontend files
└── database/
    └── init.sql                # Database initialization
```

---

## ✅ Prerequisites
Ensure you have the following installed:
- **Python 3.9+**
- **pip** (Python package manager)
- **Git**
- **An OpenAI API key** (get one at [platform.openai.com](https://platform.openai.com))

---

## 🚀 Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone <your-repo-url>
cd MedStroke
```

### 2️⃣ Create and Activate a Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate on macOS / Linux
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

### 3️⃣ Install Dependencies
```bash
# Install all dependencies at once
pip install -r requirements.txt -r backend/requirements.txt
```

### 4️⃣ Configure Environment Variables
Create a `.env` file in the `backend/` folder:

```ini
OPENAI_API_KEY=your_api_key_here
DATABASE_URL=sqlite:///./medstroke.db
# For PostgreSQL: DATABASE_URL=postgresql://user:password@localhost/medstroke
```

⚠️ **Important:** Never commit `.env` to GitHub. It's already in `.gitignore`.

### 5️⃣ Run the Backend Server
```bash
cd backend
uvicorn main:app --reload
```

The API will be available at:
- **Main API:** [http://localhost:8000](http://localhost:8000)
- **Interactive Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative Docs:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 📝 Key Features
- 🤖 AI-powered treatment plan generation using OpenAI GPT
- 🔍 ICD diagnosis code search with fuzzy matching
- 👨‍⚕️ User-friendly interface for healthcare professionals
- 📊 Patient data management
- 🔐 Secure API endpoints

---

## 🤝 Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

---

## 📧 Support
For questions or issues, please open an issue on GitHub or contact the development team.

