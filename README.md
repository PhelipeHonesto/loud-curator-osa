# 🦅 Loud Curator OSA

> AI-powered aviation news curation built by Orange Sunshine Aviation.

---

## ✈️ About the Project

**Loud Hawk** is the official media engine of **Orange Sunshine Aviation**. It pulls aviation news from multiple sources, runs it through a Gen-Z-flavored vibe filter, and delivers bold, remixable headlines via an AI-powered workflow.

---

## 📸 Preview

![Dashboard Preview](./docs/dashboard-preview.png)

---

## 🚀 Key Features

- ✅ Multi-source article ingestion (NewsData.io, Ground News, custom scrapers)
- 🧠 *Vibe Check Engine* – detects sarcasm, rebellion, or dry tone
- 🎛️ *Headline Remix Generator* – generates 3 Gen Z-style versions
- 📲 One-click export to WhatsApp, Figma, and Slack
- 🌐 Web app with swipeable news carousel

---

## 🛠️ Local Development Setup

### 1. Clone the repo

```bash
git clone https://github.com/PhelipeHonesto/loud-curator-osa.git
cd loud-curator-osa
```

### 2. Backend Setup

```bash
cd backend
cp .env.example .env

# Install dependencies
pip install -r requirements.txt

# Run the backend
uvicorn main:app --reload
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Then open: [http://localhost:5173](http://localhost:5173)

---

## 📁 Project Structure

```
loud-curator-osa/
├── backend/
│   ├── agents/
│   ├── main.py
│   ├── database.py
│   └── ...
├── frontend/
│   ├── src/
│   └── ...
├── .env.example
├── README.md
└── docs/
    └── dashboard-preview.png
```

---

## 📜 License

MIT License — remix, improve, or deploy your own version. Just don't forget to fly loud. 🦅
