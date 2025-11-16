# NoteBuddy — Frontend  
*A fast, intuitive note-taking interface built for real-time learning.*

---

## 📘 Overview

The NoteBuddy frontend is a React single-page application designed to help students capture clearer in-class notes, generate study questions using AI, and access their saved content through an organized notebook.

The focus of this client is:
- Speed  
- Clean UI  
- Practical learning features  
- Smooth interaction with the backend API  

This repository contains the **frontend only**. It connects to the NoteBuddy API for authentication, note storage, and AI question generation.

---

## 🚀 Features

### ✏️ In-Class Notes Interface
- Large, distraction-free note-taking editor  
- Real-time writing statistics (word count, character count, sentences, etc.)  
- “Generate Questions” powered by the backend AI route  
- Save notes directly to the Notebook  
- Title input + “Note Saved!” confirmation  
- Automatic clearing of the editor after save  
- Lightweight overlays for questions and stats  

### 📒 Notebook
- Loads all saved notes for the authenticated user  
- Clean card layout  
- Scrollable sidebar list  
- Layout prepared for future editing support  

### 🤖 AI Question Generator
- Sends notes to `/api/ai/generate-questions`  
- Receives structured study questions  
- Handles errors (401, 429, request failures) gracefully  

### 🔐 Authentication
- Login & register flows  
- JWT stored securely in localStorage  
- 30-minute inactivity auto-logout  
- Protected routes for all internal pages  
- React Context (`useAuth`) for central auth management  

### 🎨 UI / Styling
- Textured charcoal backgrounds  
- Ivory typewriter-inspired theme  
- Bootstrap grid + custom CSS  
- Responsive, mobile-friendly  
- Consistent component spacing and colour accents  

---

## 🧩 Tech Stack

**Framework:** React (Vite)  
**Routing:** React Router  
**UI:** Bootstrap Grid + Custom CSS  
**Auth:** React Context + LocalStorage  
**State:** Local component state + Context  
**HTTP:** Fetch API  

---

## 📁 Folder Structure




---

## ⚙️ Installation & Development

### 1. Install dependencies
```bash
npm install

2. Start the development server

npm run dev

3. API base

The frontend expects the backend to run at:

http://localhost:5000

Optionally specify:

VITE_API_BASE=http://localhost:5000

🔐 Authentication Flow

User logs in → backend returns accessToken.

Frontend stores the token in localStorage.

All protected API calls include:

