# DRA - Onboarding Platform Brand Guidelines

**Version**: 1.0  
**Last Updated**: January 2026  
**Owner**: Data Revolt Agency  

---

## Brand Identity

### About Data Revolt Agency
Data Revolt Agency is a data marketing agency that empowers marketing with data. The brand identity reflects professionalism, data-driven decision making, and modern analytics capabilities.

---

## Color Palette

### Primary Colors

| Color Name | Hex Code | HSL | Usage |
|------------|----------|-----|-------|
| **Revolt Red** | `#dd3333` | `0 72% 53%` | Primary action buttons, active states, key highlights |
| **Revolt Black** | `#121212` | `0 0% 7%` | Dark backgrounds, text, headers |

### Extended Palette

#### Light Mode
| Role | Color | Usage |
|------|-------|-------|
| Background | `#ffffff` | Main page background |
| Card Background | `#ffffff` | Cards, panels |
| Foreground | `#121212` | Primary text |
| Muted | `#f5f5f5` | Secondary backgrounds |
| Muted Foreground | `#737373` | Secondary text |
| Border | `#e5e5e5` | Dividers, borders |

#### Dark Mode
| Role | Color | Usage |
|------|-------|-------|
| Background | `#0a0a0a` | Main page background |
| Card Background | `#141414` | Cards, panels |
| Foreground | `#fafafa` | Primary text |
| Muted | `#1a1a1a` | Secondary backgrounds |
| Muted Foreground | `#a3a3a3` | Secondary text |
| Border | `#262626` | Dividers, borders |

### Functional Colors

| Color | Hex | Usage |
|-------|-----|-------|
| Success | `#22c55e` | Positive states, completed |
| Warning | `#eab308` | Caution states, pending |
| Destructive | `#dd3333` | Error states (same as primary for brand consistency) |
| Info | `#3b82f6` | Informational states |

---

## Typography

### Primary Font
**Inter** - Modern, clean, highly legible sans-serif

```css
font-family: 'Inter', system-ui, sans-serif;
```

### Font Weights
- **Light**: 300 - Subtle text
- **Regular**: 400 - Body text
- **Medium**: 500 - UI labels
- **Semibold**: 600 - Subheadings
- **Bold**: 700 - Headings
- **Extrabold**: 800 - Hero text

### Heading Scale
- H1: 2.25rem (36px) - Bold
- H2: 1.875rem (30px) - Semibold
- H3: 1.5rem (24px) - Semibold
- H4: 1.25rem (20px) - Medium
- Body: 1rem (16px) - Regular
- Small: 0.875rem (14px) - Regular
- Caption: 0.75rem (12px) - Medium

---

## Visual Elements

### Logo Usage
- **Icon**: "DRA" in white on Revolt Red rounded square
- **Wordmark**: "Onboarding" in foreground color
- Minimum clear space: Equal to height of logo icon

### Border Radius
- Large: 0.75rem (12px) - Cards, modals
- Medium: 0.5rem (8px) - Buttons, inputs
- Small: 0.25rem (4px) - Small elements

### Shadows
```css
/* Card Shadow */
box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);

/* Elevated Shadow */
box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);

/* Red Glow */
box-shadow: 0 0 20px rgba(221, 51, 51, 0.3);
```

---

## UI Components

### Buttons

#### Primary Button
- Background: Revolt Red (#dd3333)
- Text: White
- Hover: Darker red (#c42d2d)
- Active glow effect

#### Secondary Button
- Background: Muted background
- Text: Foreground
- Border: 1px solid border color

#### Ghost Button
- Background: Transparent
- Text: Muted foreground
- Hover: Subtle background

### Cards
- Background: Card color
- Border: 1px solid border color
- Border radius: 0.75rem
- Padding: 1.5rem

### Active/Selected States
- Background: `rgba(221, 51, 51, 0.15)` (Red with 15% opacity)
- Text: Revolt Red
- Icon: Revolt Red

---

## Iconography
- Icon library: Lucide React
- Stroke width: 2 or 2.5
- Icon size: 16px (sm), 20px (md), 24px (lg)
- Color: Matches text color, Red for active

---

## Gradients

### Primary Gradient
```css
background: linear-gradient(135deg, #dd3333 0%, #b52828 100%);
```

### Subtle Red Background
```css
background: rgba(221, 51, 51, 0.1);
```

### Glow Effects
```css
/* Red Glow */
box-shadow: 0 0 20px rgba(221, 51, 51, 0.3);

/* Hover Glow */
box-shadow: 0 0 40px rgba(221, 51, 51, 0.5);
```

---

## Motion

### Transitions
- Default: 200ms ease
- Hover: 150ms ease
- Page transitions: 300ms ease-out

### Animations
- Fade in: Transform + opacity, 300ms
- Pulse glow: Red glow pulse, 2s infinite
- Slide in: Transform, 300ms

---

## Accessibility

- Minimum contrast ratio: 4.5:1 for text
- Focus states: 2px solid Revolt Red with 3px offset
- Interactive elements: Minimum 44x44px touch target
- Color is never the only indicator of state

---

## Application

### Page Titles
All page titles should follow the format:
`DRA - Onboarding | [Page Name]`

### Platform Name
- Full: "DRA - Onboarding"
- Short: "DRA"
- Never: "AI Receptionist" (legacy)

---

*© 2026 Data Revolt Agency. All rights reserved.*
