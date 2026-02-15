# PLAN-client-ui-upgrade.md - Client UI/UX Upgrade

> **Goal:** Redesign the Client Landing Page and Dashboard with "Pro Max" aesthetics, hiding Admin access.

## Phase 1: Analysis & Design
**Objective:** Generate a premium design system tailored for "Financial Reconciliation SaaS".

- [ ] **1.1. Generate Design System**
    - [ ] Run `ui-ux-pro-max` script for `fintech saas reconciliation`.
    - [ ] Defines: Color Palette (Deep Blues/Reds?), Typography (Inter/Montserrat), Spacing, Glassmorphism rules.
- [ ] **1.2. Define Assets**
    - [ ] Illustrations/Gradients for Landing.
    - [ ] Chart styles for Dashboard.

## Phase 2: Landing Page Redesign (`src/app/page.tsx`)
**Objective:** Create a high-converting, trust-building entry point for Clients.

- [ ] **2.1. Hero Section**
    - [ ] Value Prop: "Recover Lost Revenue Automatically".
    - [ ] CTA: "Client Login" (Direct to `/login`).
    - [ ] **Constraint:** NO "Admin Login" button.
- [ ] **2.2. Visuals**
    - [ ] "Pro Max" Gradient Backgrounds.
    - [ ] Feature Highlights (Grid).
    - [ ] Trust Badges (Stripe, Shopify icons).

## Phase 3: Dashboard Redesign (`src/app/dashboard/page.tsx`)
**Objective:** A professional financial dashboard.

- [ ] **3.1. Layout Update**
    - [ ] Sidebar vs Topbar (Stick to Topbar but upgrade visuals).
- [ ] **3.2. Components Upgrade**
    - [ ] `HeroStat`: Glassmorphic cards, sparklines.
    - [ ] `TrendChart`: Better tooltips, gradients.
    - [ ] `DiscrepancyTable`: Status badges, sortable headers.

## Phase 4: Implementation & Polish
**Objective:** Code the changes.

- [ ] **4.1. Apply Design System** (Update `globals.css`).
- [ ] **4.2. Code Landing Page**.
- [ ] **4.3. Code Dashboard**.
- [ ] **4.4. Verify Flows**.

---

## Agent Assignments
- `frontend-specialist`: Implementation (Phases 2-4).
- `ui-ux-pro-max`: Design System Generation (Phase 1).
