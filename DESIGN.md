---
name: Serene Assistive System
colors:
  surface: '#fbf9f8'
  surface-dim: '#dcd9d9'
  surface-bright: '#fbf9f8'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f6f3f2'
  surface-container: '#f0eded'
  surface-container-high: '#eae8e7'
  surface-container-highest: '#e4e2e1'
  on-surface: '#1b1c1c'
  on-surface-variant: '#404847'
  inverse-surface: '#303030'
  inverse-on-surface: '#f3f0f0'
  outline: '#707977'
  outline-variant: '#c0c8c6'
  surface-tint: '#386661'
  primary: '#386661'
  on-primary: '#ffffff'
  primary-container: '#8bbab4'
  on-primary-container: '#1b4b47'
  inverse-primary: '#a0d0c9'
  secondary: '#5f5b7a'
  on-secondary: '#ffffff'
  secondary-container: '#dfd8fe'
  on-secondary-container: '#625d7d'
  tertiary: '#456179'
  on-tertiary: '#ffffff'
  tertiary-container: '#97b4cf'
  on-tertiary-container: '#29465d'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#bcece5'
  primary-fixed-dim: '#a0d0c9'
  on-primary-fixed: '#00201d'
  on-primary-fixed-variant: '#1f4e4a'
  secondary-fixed: '#e5deff'
  secondary-fixed-dim: '#c9c2e6'
  on-secondary-fixed: '#1c1833'
  on-secondary-fixed-variant: '#474361'
  tertiary-fixed: '#cbe6ff'
  tertiary-fixed-dim: '#adcae5'
  on-tertiary-fixed: '#001e31'
  on-tertiary-fixed-variant: '#2d4960'
  background: '#fbf9f8'
  on-background: '#1b1c1c'
  surface-variant: '#e4e2e1'
typography:
  display-lg:
    fontFamily: Atkinson Hyperlegible Next
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 64px
    letterSpacing: 0.02em
  headline-lg:
    fontFamily: Atkinson Hyperlegible Next
    fontSize: 40px
    fontWeight: '600'
    lineHeight: 52px
    letterSpacing: 0.01em
  headline-md:
    fontFamily: Atkinson Hyperlegible Next
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 44px
    letterSpacing: 0.01em
  body-lg:
    fontFamily: Atkinson Hyperlegible Next
    fontSize: 28px
    fontWeight: '400'
    lineHeight: 40px
    letterSpacing: 0.015em
  body-md:
    fontFamily: Atkinson Hyperlegible Next
    fontSize: 24px
    fontWeight: '400'
    lineHeight: 36px
    letterSpacing: 0.015em
  label-lg:
    fontFamily: Atkinson Hyperlegible Next
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: 0.03em
rounded:
  sm: 0.5rem
  DEFAULT: 1rem
  md: 1.5rem
  lg: 2rem
  xl: 3rem
  full: 9999px
spacing:
  min_target: 120px
  gutter: 40px
  margin: 64px
  safe_zone: 80px
---

## Brand & Style

The design system is centered on the principles of **Dignity, Patience, and Clarity**. It is specifically architected for users with ALS, where eye-tracking and head-pointer interaction are the primary modes of navigation. The emotional response is one of safety and composure—avoiding the clinical "medical device" feel in favor of a warm, human-centric environment.

The design style is a hybrid of **Soft-Minimalism** and **Tactile Glassmorphism**. By using layered surfaces and extremely soft shadows, the system creates a sense of "physicality" that helps users distinguish interactive zones from static content without the need for harsh borders or high-contrast visual noise. Every element is designed to feel soft to the touch, even when interacted with via gaze.

## Colors

This color palette deliberately avoids high-frequency contrast that can cause eye fatigue during long sessions of gaze interaction. 

- **Primary (Muted Teal):** Used for affirmative actions and primary communication triggers.
- **Secondary (Soft Lavender):** Used for secondary utility functions like settings or menu shifts.
- **Tertiary (Gentle Sky Blue):** Reserved for informative states or passive background accents.
- **Typography (Deep Charcoal):** We avoid #000000 to reduce "ink bleed" on bright backgrounds, ensuring high legibility through #333333.
- **Surfaces:** The backgrounds use off-white and warm grays to create a "paper-like" warmth, reducing the blue-light strain typically associated with pure white interfaces.

## Typography

The typography uses **Atkinson Hyperlegible Next**, a typeface specifically designed for high legibility and character differentiation. 

The scale is intentionally oversized. The smallest font in the entire system is 24px to ensure that users with varying levels of visual acuity or those using the app from a mounted distance (e.g., on a wheelchair) can read content without strain. 

**Key Rules:**
- **Letter Spacing:** Increased slightly across all levels to prevent "character crowding."
- **Line Height:** Very generous (1.5x minimum) to ensure that gaze tracking doesn't accidentally skip lines.
- **Alignment:** Primarily left-aligned to provide a consistent "anchor" for the eyes to return to.

## Layout & Spacing

The layout philosophy follows a **"Safe-Zone Fluid Grid."** Because gaze-tracking precision can fluctuate, the layout prioritizes isolation of interactive elements over information density.

- **Interaction Targets:** Every button or trigger must be a minimum of 120x120px. 
- **The Buffer Rule:** A mandatory 40px "dead-space" gutter exists between any two interactive elements to prevent mis-selection.
- **Screen Margins:** Ultra-wide 64px margins ensure that gaze triggers near the edge of the screen—which are often harder for hardware to track accurately—are avoided for critical actions.
- **Grid:** A 4-column layout on tablet/desktop is preferred, ensuring each column is wide enough to house large, legible text blocks.

## Elevation & Depth

Depth is used functionally to signify "pressability." Instead of traditional shadows, we use **Ambient Layering**:

- **Level 0 (Background):** The base off-white surface (#F9F9F8).
- **Level 1 (Cards/Zones):** Raised using a soft, very diffused shadow (Color: #333333 at 4% opacity, Blur: 40px) and a subtle 1px inner stroke of white to create a "beveled" soft edge.
- **Level 2 (Active/Hover):** When a gaze "dwell" begins, the element uses a **Backdrop Blur (12px)** and a subtle scale-up (1.02x). A soft outer glow in the primary color (#8BBAB4) at 20% opacity fades in to indicate the progress of the selection.

This system creates a "pillowy" aesthetic that feels responsive and alive without being visually aggressive.

## Shapes

The shape language is defined by extreme **Radius Curvature**. 

- **Interactive Zones:** All buttons and selection cards use a minimum 32px corner radius (Referenced as `rounded-xl`).
- **Containers:** Large layouts use the `rounded-lg` (2rem) setting to maintain a soft, non-threatening aesthetic.
- **Pill Philosophy:** Where possible, navigation elements and chips use a full pill-shape to maximize the "softness" of the interface. This organic geometry is easier for the eye to scan and follow compared to sharp, geometric corners.

## Components

### Interaction Cards (The Core Component)
The central component of the design system is the **Gaze Card**. It is a 120px+ container used for letters, phrases, or menu options.
- **Style:** Background #F2F0ED, 32px rounded corners.
- **Dwell State:** Upon gaze-focus, the card scales up 2% and a circular progress loader (using the primary teal) grows from the center to indicate the "click" timing.

### Buttons
Buttons are never "ghost" or "outline" only. They must have a solid, soft-colored background to provide a clear hit-target.
- **Primary:** Muted Teal with White text.
- **Secondary:** Soft Lavender with Deep Charcoal text.

### Typography Lists
Lists do not use thin dividers. Instead, list items are separated by 24px of white space and use a soft background fill on the active row.

### Input Fields
Since manual typing is difficult, input fields are "Output Display" areas. They use a large, recessed background (inner shadow) to show the text currently being constructed via gaze-board.

### Safe-Exit Trigger
A special component located in a consistent corner (usually top-right) that requires a longer dwell time to prevent accidental exits. It uses a "Soft Sky Blue" to distinguish it from communication tools.