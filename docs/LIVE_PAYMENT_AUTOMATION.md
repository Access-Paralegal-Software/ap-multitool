---
category: software
plane_id: 
profit_likelihood: high
project: None
status: inbox
tags:
  - idea
title: LIVE_PAYMENT_AUTOMATION
type: idea
updated_at: "2026-05-17T09:08:47Z"
---

# 💳 Access Paralegal Live Production Gateway
## Stripe & Keygen.sh Automated Integration Blueprint

This document serves as the central technical authority and deployment guide for your live payment processing system. It records your official product credentials and provides a zero-friction roadmap to automatically delivering production license keys to paying customers.

---

## 📋 Production Asset Inventory

These are the validated, live production credentials for your legal ecosystem:

| Service Provider | Asset Description | Production Value / ID |
| :--- | :--- | :--- |
| **Stripe** | Elite Founder Tier Product ID | `prod_UWPdKwW0N2K7Nj` |
| **Keygen.sh** | Product Account ID | `c885ab2c-9f4d-44a1-adfd-ec1839a0ed93` |
| **Keygen.sh** | Product Token | `prod-1ba5ec8a951c...[REDACTED_IN_PUBLIC]` |

---

## 🚀 Step 1: Generate Your Live Purchase Link (Stripe)

Now that your Stripe Product is live (`prod_UWPdKwW0N2K7Nj`), you need to generate the public checkout URL. This token will replace the `YOUR_STRIPE_LINK_HERE` placeholders in your website's HTML code.

### 🛒 How to Generate the Link in Stripe:
1.  Log into your **Stripe Dashboard** ([dashboard.stripe.com](https://dashboard.stripe.com)).
2.  In the top search bar, type your Product ID `prod_UWPdKwW0N2K7Nj` or navigate to **Product Catalog** and select the **Access Paralegal Suite**.
3.  Scroll down to the pricing section and click the **Create payment link** button.
4.  **Configure Checkout**:
    *   Turn ON **Collect customers' addresses** (Highly recommended for legal software tax calculations).
    *   Under **Advanced options**, ensure "Allow promotion codes" is turned on if you plan to run discounts!
5.  Click **Create link** in the top-right corner.
6.  Stripe will generate an obfuscated URL like: `https://buy.stripe.com/6oEcPt9u9...`
7.  **Action Item**: Copy this link and replace the placeholder in:
    *   📂 `docs/index.html` (Line 118)
    *   📂 `web_portal/index.html` (Line 118)

---

## 🤖 Step 2: Connect Payments to Licenses (Zero-Code Automation)

When a user purchases through the link above, we want **Keygen.sh** to automatically generate a license and email it to the customer. 

We recommend using **Zapier** for this, as it requires no server code and integrates natively with both Stripe and Keygen.

### 🛠️ Step-by-Step Zapier Setup:

#### **A. The Trigger (Stripe)**
1.  Log into Zapier and click **Create Zap**.
2.  Select **Stripe** as the App and **New Payment** (or **New Subscription**) as the Trigger Event.
3.  Connect your Stripe account.
4.  In the test step, verify that Zapier pulls in a sample sale of your Product ID `prod_UWPdKwW0N2K7Nj`.

#### **B. The Action (Keygen)**
1.  Add an action step and select **Keygen** as the App.
2.  Select **Create License** as the Action Event.
3.  When prompted for API keys, use your **Keygen Product Token** and **Account ID** listed in our inventory.
4.  **Map the Data**:
    *   **Product**: Select `Access Paralegal Compiler` from the dropdown.
    *   **Policy**: Select `Lifetime Unlimited License` from the dropdown.
    *   **Name**: Map the customer's Name from Stripe.
    *   **Metadata**: Add a field mapping `stripe_product_id` to `prod_UWPdKwW0N2K7Nj` (Excellent for bookkeeping!).
5.  Click Test. Keygen will instantly generate a sample key!

#### **C. The Delivery (Email)**
1.  Add a final action step using **Gmail** or **Zapier Email**.
2.  Map the recipient to the **Customer Email** pulled from the Stripe transaction.
3.  **Subject**: ⚖️ Your Access Paralegal Suite License Key is Inside!
4.  **Body**: Write an elegant welcome email and map the **License Key** generated in Step B directly into the body copy!

---

## 🔒 Security Controls

*   **Over-Activation Shield**: By mapping the Keygen policy properly, every license automatically delivered by this Zap will be capped at **1 Machine Activation**. If the user attempts to run the app on a second PC, Keygen's validation server will reject the handshake, protecting your revenue!
*   **Revocation Flow**: If a customer initiates a chargeback or refund in Stripe, you can simply find their license in Keygen.sh and toggle their Status to **Suspended**. The desktop app will automatically lock them out upon its next validation cycle.

***
*For technical engineering support during live API routing, please contact the Core Engineering Team.* 🛡️💻🔑💳
