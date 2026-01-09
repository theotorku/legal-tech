# 🚀 Quick Start Guide - Contract Analyzer

Get your Contract Analyzer platform up and running in 10 minutes!

---

## Prerequisites

Before you begin, ensure you have:

- ✅ Python 3.11 or higher
- ✅ Node.js 20 or higher
- ✅ PostgreSQL 15 or higher
- ✅ OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- ✅ Stripe account ([Sign up here](https://dashboard.stripe.com/register))

---

## Step 1: Clone or Navigate to Project

```bash
cd "OneDrive/Desktop/DevOps/Legal Tech"
```

---

## Step 2: Set Up Backend (5 minutes)

### 2.1 Create Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\Activate.ps1

# Mac/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 2.2 Install Dependencies

```bash
pip install -r requirements.txt
```

### 2.3 Configure Environment Variables

Create `.env` file in the project root:

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/contract_analyzer

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key-here

# Stripe
STRIPE_SECRET_KEY=sk_test_your-stripe-secret-key
STRIPE_PUBLISHABLE_KEY=pk_test_your-stripe-publishable-key
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret

# App
ENVIRONMENT=development
```

### 2.4 Initialize Database

```bash
# Create database
createdb contract_analyzer

# Or using psql
psql -U postgres -c "CREATE DATABASE contract_analyzer;"

# Initialize tables
python -c "from app.database import init_db; init_db()"
```

### 2.5 Start Backend Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

✅ **Backend is now running at:** http://localhost:8000

---

## Step 3: Set Up Frontend (3 minutes)

### 3.1 Navigate to Frontend Directory

```bash
cd frontend
```

### 3.2 Install Dependencies

```bash
npm install
```

### 3.3 Configure Environment Variables

Create `.env.local` file in the `frontend` directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your-stripe-publishable-key
```

### 3.4 Start Frontend Server

```bash
npm run dev
```

✅ **Frontend is now running at:** http://localhost:3000

---

## Step 4: Test the Application (2 minutes)

### 4.1 Visit the Landing Page

Open your browser and go to: **http://localhost:3000**

You should see the beautiful landing page with:
- Hero section
- Feature highlights
- Pricing information
- Call-to-action buttons

### 4.2 Register a New Account

1. Click **"Get Started"** or **"Sign Up"**
2. Fill in the registration form:
   - Email: `test@example.com`
   - Password: `password123`
   - Full Name: `Test User`
3. Click **"Create Account"**

✅ You'll be redirected to the pricing page

### 4.3 Select a Subscription Plan

1. Choose a plan (use **Starter** for testing)
2. Click **"Subscribe"**
3. Enter Stripe test card details:
   - Card Number: `4242 4242 4242 4242`
   - Expiry: Any future date (e.g., `12/25`)
   - CVC: Any 3 digits (e.g., `123`)
   - ZIP: Any 5 digits (e.g., `12345`)
4. Click **"Subscribe"**

✅ You'll be redirected to the dashboard

### 4.4 Analyze a Contract

1. Click **"Analyze Contract"** in the sidebar
2. Drag and drop a PDF file or click to upload
3. Click **"Analyze Contract"**
4. Wait for the AI analysis (5-10 seconds)
5. View the comprehensive results:
   - Summary
   - Parties
   - Key terms
   - Identified risks

✅ Your first contract is analyzed!

### 4.5 Check Your Subscription

1. Click **"Subscription"** in the sidebar
2. View your current plan details
3. See usage statistics
4. Try upgrading to a different plan

### 4.6 Get Your API Key

1. Click **"API Keys"** in the sidebar
2. View your API key
3. Click **"Show"** to reveal the full key
4. Click **"Copy"** to copy to clipboard
5. Test the API with cURL:

```bash
curl -X POST http://localhost:8000/v1/contracts/analyze \
  -H "X-API-Key: your_api_key_here" \
  -F "file=@path/to/contract.pdf"
```

---

## Step 5: Explore the API Documentation

Visit: **http://localhost:8000/docs**

You'll see the interactive Swagger UI with all API endpoints:
- Authentication
- Contract Analysis
- Subscriptions
- API Keys
- Webhooks
- Health Checks

Try out the endpoints directly from the browser!

---

## 🎉 You're All Set!

Your Contract Analyzer platform is now fully operational!

### What You Can Do Now:

1. **Analyze Contracts** - Upload and analyze legal documents
2. **Manage Subscriptions** - Upgrade, downgrade, or cancel plans
3. **Use the API** - Integrate with your own applications
4. **Monitor Usage** - Track your contract analysis usage
5. **Manage API Keys** - Generate and revoke API keys

---

## 🔧 Troubleshooting

### Backend Won't Start

**Issue:** Database connection error

**Solution:**
```bash
# Check if PostgreSQL is running
pg_isready

# Create database if it doesn't exist
createdb contract_analyzer

# Check DATABASE_URL in .env
```

**Issue:** OpenAI API error

**Solution:**
- Verify your OpenAI API key in `.env`
- Check your OpenAI account has credits
- Ensure the key starts with `sk-`

### Frontend Won't Start

**Issue:** Module not found errors

**Solution:**
```bash
# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Issue:** Can't connect to backend

**Solution:**
- Ensure backend is running on port 8000
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Verify CORS is enabled in backend

### Stripe Payment Issues

**Issue:** Payment fails

**Solution:**
- Use test card: `4242 4242 4242 4242`
- Ensure Stripe keys are in test mode (`sk_test_` and `pk_test_`)
- Check Stripe dashboard for errors

---

## 📚 Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [FRONTEND_IMPLEMENTATION.md](FRONTEND_IMPLEMENTATION.md) for frontend details
- Review [PROJECT_COMPLETE.md](PROJECT_COMPLETE.md) for the complete feature list
- Explore the API at http://localhost:8000/docs

---

## 🆘 Need Help?

- Check the documentation files in the project root
- Review the code comments
- Test with the Swagger UI at `/docs`
- Verify environment variables are set correctly

---

**Happy Analyzing! 🎉**

