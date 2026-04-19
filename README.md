# CareerBridge 🚀

**Course & Internship Recommendation Platform (Streamlit + Python)**

---

## 🔍 Overview

CareerBridge is a lightweight platform that helps students discover, apply to, and track courses and internships in one place.
It combines structured listing management with a **scoring-based recommendation system** to surface the most relevant opportunities.

---

## ✨ Key Features

### 👨‍🎓 Student

* Browse courses & internships
* Search and filter (domain, type)
* Apply/enroll with **duplicate prevention**
* Track applications (Applied / Pending / Selected / Enrolled)
* Personalized recommendations based on skills
* Profile management (skills + resume upload/download)

### 🏢 Provider

* Post new courses/internships
* Manage listings and applicants
* Update application status

---

## 🧠 Recommendation System

The platform uses a **weighted multi-signal scoring system** to rank listings:

* **Title Match (40%)** → Skill appears in listing title
* **Domain Match (30%)** → Skill aligns with listing domain
* **Description Match (20%)** → Skill found in description
* **Popularity (10%)** → Based on number of applications

Each listing is scored and ranked to show the most relevant opportunities first.

👉 This approach is:

* Simple and explainable
* Easily tunable
* Extendable to ML models (TF-IDF, embeddings, collaborative filtering)

---

## 🏗 System Architecture

* **Frontend:** Streamlit
* **Backend Logic:** Python modules

  * `recommender.py` → scoring engine
  * `storage.py` → data handling
* **Data Layer:** JSON files (easily replaceable with DB)

---

## 🗄 Database Design

* **Users** → authentication & roles
* **Listings** → courses/internships
* **Applications** → tracks user activity (duplicate-safe)

---

## ⚙️ How to Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open:

```id="l2r8sv"
http://localhost:8501
```

---

## 📸 Demo Highlights

* Smart recommendation ranking
* Real-time duplicate application prevention
* Clean dashboard for tracking applications
* Simple provider workflow for posting listings

---

## 📄 System Design Report

👉 See detailed explanation here:
**CareerBridge_System_Design.pdf**

---

## ⚠️ Edge Case Handling

* Duplicate applications prevented (UI + backend)
* Empty input handling
* Safe defaults for missing data
* Validation for provider inputs

---

## 🚀 Future Improvements

* TF-IDF / embedding-based recommendations
* Collaborative filtering (“users like you”)
* PostgreSQL integration
* Scalable backend (FastAPI + caching)

---

## 👤 Author

**Adan Tabish Azeem**
GitHub: https://github.com/Syed-Adan

---

## ⭐ Final Note

This project focuses on **clarity of logic, usability, and recommendation relevance**, rather than over-engineering — making it practical and extensible for real-world systems.
