# 🗡️ KaamKaaj: The Accountability Engine

> **To-do lists are broken. They rely on willpower. KaamKaaj relies on proof.**

**KaamKaaj is a hardcore, gamified productivity application that forces accountability. Users cannot simply check a box to complete a task; they must submit photographic evidence ("Saboot") which is critically evaluated by an AI Game Master before XP is awarded.**

---

🔗 **Enter the Arena (Live App):** [kaamkaaj-sooty.vercel.app](https://kaamkaaj-sooty.vercel.app)

---

## 📲 The PWA Experience: Your Life, Installable

KaamKaaj isn't just a website; it's a **Progressive Web App (PWA)** designed to feel like a native mobile application. Stop fumbling with browser tabs and bring the grind directly to your home screen.

### ⚡ Why Install KaamKaaj?
*   **Native-App Feel:** No URL bars, no browser chrome—just pure, immersive RPG-style productivity.
*   **Instant Access:** Launch KaamKaaj directly from your app drawer or home screen with a single tap.
*   **Optimized for Mobile:** Every button, card, and interaction is engineered for a tactile, mobile-first experience.
*   **Dopamine-Hit Pushes:** Receive real-time feedback from the Game Master as if it were a native system notification.

**How to Install:**
1.  Open [KaamKaaj](https://kaamkaaj-sooty.vercel.app) in your mobile browser (Chrome/Safari).
2.  Tap the **Menu** or **Share** button.
3.  Select **"Add to Home Screen"** or **"Install App"**.
4.  ⚔️ **Begin your journey.**

---

## ⚖️ Why KaamKaaj? (The Willpower Gap)

Most productivity apps are just digital lists. They trust you to be honest. But in the heat of procrastination, honesty is the first casualty. **KaamKaaj removes the option to lie.** 

By requiring visual proof, it creates a "Hardcore Mode" for your life. It turns mundane tasks into high-stakes quests where your progress is verified by an impartial AI judge. Stop managing lists and start conquering goals.

---

## 🎯 The Core Loop (How it works)

1.  **Forge a Lakshya (Quest):** Set a high-level goal (e.g., "Master DSA").
2.  **Assign a Kaam (Task):** Break it down into actionable steps (e.g., "Solve LC 3912").
3.  **Submit the Saboot (Proof):** Upload an image of your completed work.
4.  **Face the Game Master (AI Evaluation):** The backend background worker sends the image and task description to Google's Gemini AI. The AI acts as a strict judge.
5.  **Level Up or Fail:** If the proof is valid, the AI grants approval and you earn XP. If it's weak or irrelevant, the AI brutally rejects the submission.

---

## 🛠️ The FARP Stack Architecture

This project is built on the modern **FARP Stack**, prioritizing type-safety, rapid API development, and fluid UI interactions.

### Frontend (The Face)
*   **Framework:** Next.js 15 (App Router) & React 19
*   **Styling:** Tailwind CSS 4 & Shadcn/ui (Dark Mode RPG Aesthetic)
*   **State Management:** Zustand (Auth persistence) & TanStack React Query 5 (Smart polling & caching)
*   **PWA Core:** Next-PWA with specialized manifest and service worker configuration for high performance.

### Backend (The Brain)
*   **Framework:** FastAPI (Python)
*   **Database & ORM:** PostgreSQL (hosted on Neon.tech) via SQLModel (SQLAlchemy + Pydantic)
*   **Authentication:** OAuth2 with JWT (JSON Web Tokens) & OTP-based Email Verification
*   **Storage:** Cloudinary API (Multipart form-data image streaming)
*   **AI Engine:** Google Gemini API integrated via asynchronous background tasks.

---

## 🚀 Engineering Highlights & Problem Solving

### 1. The "Empty String" Payload Trap
**Challenge:** Next.js forms natively send empty strings (`""`) for untouched optional fields, which caused FastAPI's `exclude_unset=True` to wipe existing database columns during `PATCH` profile updates.
**Solution:** Engineered a frontend payload sanitizer utilizing `Object.entries` to filter out nulls and empty strings before transmission, ensuring non-destructive data hydration.

### 2. Automated Dopamine Loop (Smart Polling)
**Challenge:** AI image evaluation takes 2-4 seconds. Forcing the user to manually refresh the page to see if they leveled up breaks the psychological gamification loop.
**Solution:** Implemented dynamic React Query polling. The frontend acts as a **radar**—pinging the server every 2 seconds *only* when a task status is `in_review`. The millisecond the AI finishes, the UI captures the `completed` state, stops polling, and triggers cinematic status transitions.

### 3. The Hybrid Edge-Tunnel Deployment Bypass
**Challenge:** Standard free-tier cloud platforms institute strict credit card verification walls, blocking immediate backend deployment for developers without international cards.
**Solution:** Engineered a reverse-proxy tunnel using Cloudflare (`cloudflared`). The Next.js frontend lives globally on Vercel and routes authenticated HTTPS requests directly through the tunnel to the local FastAPI instance and Neon Cloud DB.

---

## 🧪 Try it Out (Demo Credentials)

To evaluate the system without registering, use the following credentials:
*   **Username:** `suleman.miles` (Or awaken your "Khiladi" and start the grind!)
*   **Password:** `recruiter123` 

**Built with ⚔️ by [Suleman Khan](https://github.com/Sulemankhannit)**
