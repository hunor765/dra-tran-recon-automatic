# PROJECT PLAN: UI Redesign ("The Red Line")

## 1. Goal & Vision
**Objective**: Redesign the application UI to feel "premium," "curated," and "human-centric," avoiding the generic "AI startup" look.
**Style Update**: Strict adherence to existing brand assets (Montserrat, #dd3333, Black/White/Grey) but elevating their usage through layout, spacing, and contrast.

**Aesthetic Concept: "Swiss Minimalist"**
- **Vibe**: High-fashion tech, brutalist-lite, extremely clean. Think "Modern Art Gallery Website" or "Premium architectural portfolio".
- **Keywords**: Sharp, spacious, decisive.

## 2. Design System
### 2.1 Typography (Strict: Montserrat)
Since we are single-font, we will use weight and size dramatically.
- **Headings**: **Montserrat (Black/900 or ExtraBold/800)** - Tight tracking (`-0.02em`) for impact.
- **Body**: **Montserrat (Regular/400 or Medium/500)** - Relaxed line-height (`1.6`) for readability.
- **Labels/UI**: **Montserrat (SemiBold/600)** - All-caps, wide tracking (`0.05em`) for premium feel.

### 2.2 Color Palette (Strict: B/W/Red)
A high-contrast, "magazine" aesthetic.
- **Backgrounds**: 
  - `Light`: `#ffffff` (Pure White) & `#f4f4f5` (Zinc-100/Light Grey).
  - `Dark`: `#0a0a0a` (Rich Black) & `#171717` (Neutral-900).
- **Accents**:
  - `Brand`: `#dd3333` (Revolt Red) - Used *sparingly* for primary actions and key data points. "The red line".
  - `Text`: `#171717` (Black) on White / `#ffffff` (White) on Black.

### 2.3 Visual Language
- **Borders**: Sharp, 1px lines. No rounded corners on major sections (`rounded-none` or `rounded-sm`).
- **Shadows**: Removed or very subtle. Rely on borders and layout.
- **Space**: Generous whitespace. 
- **Data Vis**: Thin lines, monochromatic with red highlights (no rainbow charts).

## 3. Implementation Steps

### Phase 1: Foundation
- [ ] Reset `globals.css` to remove any conflicting styles.
- [ ] Configure Tailwind v4 Theme:
    - Add `#dd3333` as `revolt-red`.
    - Set default font stack to `Montserrat`.
    - Define custom spacing/border utilities.

### Phase 2: Core Components ("The Red Kit")
- [ ] **Button**: Sharp edges, uppercase text. 
    - `Primary`: Red background, White text.
    - `Outline`: 1px Black border, hover Red.
- [ ] **Input**: Underlined only (Material/Swiss style) or sharp rectangle.
- [ ] **Card**: White background, 1px Grey border, no shadow.
- [ ] **Badge**: Outlined, square corners.

### Phase 3: Layout & Navigation
- [ ] **Sidebar**: White background, right-border. Selected state: Red text + Red left-border indicator.
- [ ] **Top Bar**: Minimal. Breadcrumbs in uppercase.
- [ ] **Main Layout**: Grid-based, distinct sections separated by visible borders.

### Phase 4: Screens
- [ ] **Dashboard**: "KPI Cards" with large typography.
- [ ] **Reconciliation View**: Clean data tables, alternating rows (zebra striping) for readability.
- [ ] **Settings**: Organized, form-focused.

## 4. Verification Plan
### Automated
- `npm run lint`: Ensure no style conflicts.
- `npm run build`: Verify production build.

### Manual Review (User)
- **Visual Check**:
    1. Is it consistent with the "Red Line" aesthetic?
    2. Is Montserrat used effectively (readability vs style)?
    3. does it feel "premium" without being flashy?

## Agent Roles
- **Frontend Specialist**: Implement Tailwind config, components, and layouts.
- **User**: Review aesthetic direction.
