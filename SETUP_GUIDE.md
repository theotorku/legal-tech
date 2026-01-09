# Complete Setup Guide - Contract Analyzer API with Monetization

This guide will walk you through setting up the complete monetization system from scratch.

---

## Prerequisites

- Python 3.11+
- OpenAI API key
- Supabase account (free tier available)
- Stripe account (optional for payments)

---

## Step 1: Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Step 2: Set Up Supabase

### 2.1 Create Supabase Project

1. Go to https://supabase.com
2. Click "Start your project"
3. Create a new organization (if needed)
4. Create a new project
5. Wait for project to be ready (~2 minutes)

### 2.2 Run Database Schema

1. In Supabase Dashboard, go to "SQL Editor"
2. Click "New query"
3. Copy the entire contents of `supabase_monetization_schema.sql`
4. Paste into the SQL editor
5. Click "Run" or press Ctrl+Enter
6. Verify tables were created in "Table Editor"

### 2.3 Get API Credentials

1. Go to Project Settings → API
2. Copy your Project URL
3. Copy your `anon` `public` key
4. Save these for the next step

---

## Step 3: Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env
```

Edit `.env` and add your credentials:

```bash
# Required
OPENAI_API_KEY=sk-your-openai-key-here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# Generate a secure JWT secret
JWT_SECRET_KEY=your-super-secret-jwt-key-min-32-chars

# Optional (for payments)
STRIPE_API_KEY=sk_test_your_stripe_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key
```

### Generate Secure JWT Secret

```bash
# Using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Or using OpenSSL
openssl rand -hex 32
```

---

## Step 4: Set Up Stripe (Optional but Recommended)

### 4.1 Create Stripe Account

1. Go to https://stripe.com
2. Sign up for an account
3. Complete verification (can use test mode immediately)

### 4.2 Create Products

1. Go to Stripe Dashboard → Products
2. Create 4 products matching your plans:

**Starter Plan:**
- Name: "Starter Plan"
- Price: $99/month (create monthly price)
- Price: $990/year (create annual price)

**Professional Plan:**
- Name: "Professional Plan"
- Price: $299/month
- Price: $2,990/year

**Business Plan:**
- Name: "Business Plan"
- Price: $799/month
- Price: $7,990/year

**Enterprise Plan:**
- Name: "Enterprise Plan"
- Price: Custom (contact sales)

### 4.3 Get API Keys

1. Go to Developers → API keys
2. Copy "Publishable key" (starts with `pk_test_`)
3. Copy "Secret key" (starts with `sk_test_`)
4. Add to `.env` file

### 4.4 Set Up Webhooks (for production)

1. Go to Developers → Webhooks
2. Click "Add endpoint"
3. Endpoint URL: `https://your-domain.com/api/v1/webhooks/stripe`
4. Select events:
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Copy webhook signing secret
6. Add to `.env` as `STRIPE_WEBHOOK_SECRET`

---

## Step 5: Run the Application

```bash
# Development mode with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or using the Makefile
make run
```

The API will be available at: http://localhost:8000

---

## Step 6: Test the Setup

### 6.1 Check Health

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-08T...",
  "version": "1.0.0",
  "checks": {
    "database": "healthy"
  }
}
```

### 6.2 View API Documentation

Open in browser: http://localhost:8000/docs

You should see:
- Authentication endpoints
- Subscription endpoints
- Contract analysis endpoints

### 6.3 Register a Test User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123!",
    "full_name": "Test User",
    "company_name": "Test Company"
  }'
```

Expected response:
```json
{
  "user": {
    "id": "...",
    "email": "test@example.com",
    "full_name": "Test User",
    ...
  },
  "access_token": "eyJ...",
  "token_type": "bearer",
  "api_key": "ca_..."
}
```

**Save the `access_token` and `api_key` for next steps!**

### 6.4 Get Subscription Plans

```bash
curl http://localhost:8000/api/v1/subscriptions/plans
```

Expected response: Array of 4 plans with pricing details

### 6.5 Create a Subscription

```bash
curl -X POST http://localhost:8000/api/v1/subscriptions/subscribe \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plan_name": "professional",
    "billing_cycle": "monthly"
  }'
```

Expected response:
```json
{
  "subscription": {
    "id": "...",
    "status": "trial",
    "trial_end": "2026-01-22T...",
    ...
  },
  "message": "Subscription created successfully. Your 14-day free trial has started!"
}
```

### 6.6 Check Usage

```bash
curl http://localhost:8000/api/v1/subscriptions/usage \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 6.7 Analyze a Contract (with API Key)

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "X-API-Key: YOUR_API_KEY" \
  -F "file=@sample_contract.pdf"
```

---

## Step 7: Verify Database

### Check Users Table

1. Go to Supabase Dashboard → Table Editor
2. Select `users` table
3. You should see your test user

### Check Subscriptions Table

1. Select `subscriptions` table
2. You should see the subscription you created
3. Status should be "trial"

### Check Usage Tracking

1. After analyzing a contract, check `usage_tracking` table
2. You should see a record for the analysis

---

## Troubleshooting

### Issue: "AuthService not initialized"

**Solution**: Make sure Supabase URL and key are set in `.env`

```bash
# Check if variables are set
echo $SUPABASE_URL
echo $SUPABASE_KEY
```

### Issue: "Failed to initialize Supabase client"

**Solution**: Verify your Supabase credentials are correct

1. Check Project URL in Supabase Dashboard
2. Check API key (use `anon` `public` key, not service role)
3. Restart the application

### Issue: "Invalid token"

**Solution**: Token may have expired (24 hours)

```bash
# Login again to get a new token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePassword123!"}'
```

### Issue: Database connection errors

**Solution**: Check Supabase project status

1. Go to Supabase Dashboard
2. Check if project is paused (free tier pauses after inactivity)
3. Click "Restore" if paused

### Issue: Stripe errors

**Solution**: Verify Stripe is in test mode

1. Check that keys start with `sk_test_` and `pk_test_`
2. Verify webhook secret if using webhooks
3. Check Stripe Dashboard for error logs

---

## Next Steps

1. **Test all endpoints** using the interactive docs at `/docs`
2. **Create additional test users** with different plans
3. **Test subscription upgrades** and cancellations
4. **Monitor usage tracking** in the database
5. **Set up Stripe webhooks** for production
6. **Build frontend dashboard** (see `uZrG9ChHmAikvjvcXB7uUx` task)
7. **Deploy to production** (see `DEPLOYMENT.md`)

---

## Production Checklist

Before going to production:

- [ ] Change `JWT_SECRET_KEY` to a strong random value
- [ ] Use Stripe live keys (not test keys)
- [ ] Set up SSL/TLS certificates
- [ ] Configure production CORS origins
- [ ] Set `ENVIRONMENT=production` in `.env`
- [ ] Enable Supabase Row Level Security policies
- [ ] Set up monitoring and alerts
- [ ] Configure backup strategy
- [ ] Test all payment flows
- [ ] Review security headers
- [ ] Enable rate limiting
- [ ] Set up error tracking (Sentry, etc.)

---

## Support

For issues or questions:
1. Check the logs: `docker-compose logs -f` or console output
2. Review the documentation in `/docs`
3. Check Supabase logs in Dashboard → Logs
4. Check Stripe logs in Dashboard → Developers → Logs

---

**Congratulations!** Your monetization system is now set up and ready to use! 🎉

