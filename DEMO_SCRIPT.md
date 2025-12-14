# DocWiz Demo Script
## AI-Powered Surgical Visualization Platform

**Duration:** 3-4 minutes
**Live URL:** https://doc-wiz-32041.web.app

---

## 🏆 SPONSOR INTEGRATION SUMMARY

| Sponsor | Where It's Used | Demo Moment |
|---------|-----------------|-------------|
| **🤖 Google Gemini / Nano-Banana** | AI visualization, similarity analysis, insurance docs | Parts 4, 5, 6 |
| **🧠 Qdrant** | Similar cases vector search | Part 4 (after generation) |
| **🎨 Freepik** | Cost breakdown infographics | Part 6 (insurance section) |

---

## Opening (15 seconds)

> "Hi, I'm presenting **DocWiz** - an AI-powered platform that helps plastic surgeons show patients realistic previews of surgical outcomes before they commit to a procedure. This solves a real problem: patients often can't visualize what they'll look like after surgery, leading to anxiety and unrealistic expectations."

---

## Part 1: Login & Setup (30 seconds)

**Action:** Open https://doc-wiz-32041.web.app

> "Let me walk you through the platform. I'll log in as a doctor..."

**Action:** Login with credentials

> "The system uses secure JWT authentication hosted on **🤖 Google Cloud Run** with data stored in **Firebase/Firestore**."

### 🤖 GOOGLE CLOUD CALLOUT #1:
> "Our entire backend runs on **Google Cloud Run** - serverless, scalable, and cost-effective."

---

## Part 2: Upload Patient Photo (30 seconds)

**Action:** Click "Upload Image" and select a before photo

> "First, I upload the patient's current photo. This is the 'before' image that our AI will transform."

**Action:** Wait for upload to complete

### 🤖 GOOGLE CLOUD CALLOUT #2:
> "The image is securely stored in **Google Cloud Storage** via Firebase - ensuring HIPAA-ready data handling."

---

## Part 3: Select Procedure - Cleft Repair (30 seconds)

**Action:** Click on "Cleft Lip Repair" procedure card

> "Now I select the procedure. Let's choose **Cleft Lip Repair** - a reconstructive surgery that repairs the upper lip."

**Action:** Show procedure details

> "The system shows average costs, recovery time, and procedure details."

---

## Part 4: AI Visualization Generation (60 seconds) ⭐ KEY DEMO MOMENT

**Action:** Click "Generate Visualization" button

### 🤖 GOOGLE GEMINI CALLOUT #1 (MAIN FEATURE):
> "Here's where **Google Gemini 2.0 Flash** powers our core feature. I click generate, and **Nano-Banana** - our Gemini-powered AI engine - creates a photorealistic 'after' image showing what the patient could look like post-surgery."

**Action:** Wait for AI to generate (show loading animation)

> "The AI analyzes the facial structure, understands the cleft defect, and generates a medically-informed prediction of the surgical outcome using **Gemini's image generation capabilities**."

**Action:** Show the generated result

> "And here's our AI-generated preview! You can see the cupid's bow restoration, the philtral columns, and natural lip symmetry."

### 🧠 QDRANT CALLOUT (Similar Cases):
**Action:** Point to "Similar Cases" section if visible

> "And notice this - we use **Qdrant vector database** to find similar past surgical cases. The system converts this visualization into a 768-dimensional embedding and searches our database for matching outcomes. This helps patients see real results from similar procedures!"

---

## Part 5: Compare AI vs Real Result (60 seconds) ⭐ KEY DEMO MOMENT

**Action:** Scroll to "Step 2: Compare with Real Result"

> "Now here's something unique - we can validate our AI's accuracy by comparing it to actual surgical outcomes."

**Action:** Upload a real post-surgery photo

> "I'll upload a real post-procedure photo from a previous case..."

### 🤖 GOOGLE GEMINI CALLOUT #2 (MULTIMODAL):
**Action:** Wait for AI Similarity Analysis to auto-generate

> "Watch this - **Gemini's multimodal AI** automatically analyzes BOTH images together - the AI prediction and the real result - and generates a detailed similarity report."

**Action:** Show the analysis results

> "The AI gives us an **87% accuracy score** and breaks down exactly where the prediction matched: lip contour, nostril symmetry, muscle continuity. This is **Gemini's vision + text capabilities** working together!"

---

## Part 6: Insurance & Cost Visualization (45 seconds)

**Action:** Scroll to "Step 3: Insurance Claim Assistance"

### 🤖 GOOGLE GEMINI CALLOUT #3 (TEXT GENERATION):
> "For reconstructive procedures like cleft repair, insurance is crucial. **Gemini** auto-generates pre-authorization letters with ICD-10 codes and medical necessity justification - saving hours of paperwork."

**Action:** Show the insurance documentation

### 🎨 FREEPIK CALLOUT:
**Action:** Point to cost breakdown section/infographic

> "And for cost transparency, we use the **Freepik API** to generate professional cost breakdown infographics. Freepik's AI creates visual representations of surgeon fees, facility costs, anesthesia - all styled with a clean medical aesthetic that patients can easily understand."

---

## Part 7: Technology Stack Summary (30 seconds)

> "Let me quickly recap our sponsor integrations:"

### 🤖 GOOGLE / GEMINI / NANO-BANANA:
> "**Google Gemini 2.0 Flash** powers THREE core features:
> 1. **Image generation** for surgical previews
> 2. **Multimodal analysis** comparing AI vs real results  
> 3. **Text generation** for insurance documentation
> 
> Plus **Firebase/Firestore** for database, **Cloud Storage** for images, and **Cloud Run** for hosting."

### 🧠 QDRANT:
> "**Qdrant** provides vector similarity search - we store 768-dimensional embeddings of every visualization and find matching cases based on visual similarity, procedure type, and patient demographics."

### 🎨 FREEPIK:
> "**Freepik's AI API** generates professional cost infographics - turning raw pricing data into patient-friendly visual breakdowns."

---

## Closing (15 seconds)

> "DocWiz demonstrates how **Gemini, Qdrant, and Freepik** can work together to solve real healthcare problems. We bridge the gap between patient expectations and surgical reality with AI-powered visualization and validation."

> "Thank you! Any questions?"

---

## 📍 QUICK REFERENCE: Where Each Sponsor Appears

### 🤖 Google Gemini / Nano-Banana (3 uses)
| Feature | Code Location | Demo Moment |
|---------|---------------|-------------|
| Image Generation | `nano_banana_client.py → generate_image()` | Part 4 - Generate button |
| Multimodal Analysis | `nano_banana_client.py → generate_multimodal_analysis()` | Part 5 - Auto-analysis |
| Text Generation | `nano_banana_client.py → generate_text()` | Part 6 - Insurance docs |

### 🤖 Google Cloud Products
| Product | Purpose |
|---------|---------|
| Cloud Run | Backend hosting |
| Firebase Hosting | Frontend hosting |
| Firestore | Database |
| Cloud Storage | Image storage |

### 🧠 Qdrant (1 use)
| Feature | Code Location | Demo Moment |
|---------|---------------|-------------|
| Similar Cases Search | `qdrant_client.py → search_similar()` | Part 4 - After generation |

### 🎨 Freepik (1 use)
| Feature | Code Location | Demo Moment |
|---------|---------------|-------------|
| Cost Infographics | `freepik_client.py → generate_cost_infographic()` | Part 6 - Cost section |

---

## Demo Backup Plan

If something doesn't work live:

1. **Backend down?** → Show code files: `nano_banana_client.py`, `qdrant_client.py`, `freepik_client.py`
2. **Generation slow?** → Explain Gemini is processing, show pre-recorded result
3. **Upload fails?** → Use hardcoded demo data

---

**Remember:** Call out EACH sponsor by name when you reach their feature in the demo!
