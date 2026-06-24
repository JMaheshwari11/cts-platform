/**
 * Centralized motion presets for Framer Motion.
 * Keeps animations coordinated across the dashboard.
 */

export const easings = {
  default:    [0.25, 0.46, 0.45, 0.94],
  snappy:     [0.34, 1.56, 0.64, 1],
  confident:  [0.16, 1, 0.3, 1],
  decelerate: [0, 0, 0.2, 1],
}

export const durations = {
  instant:   0.12,
  default:   0.24,
  confident: 0.36,
  story:     0.60,
}

// ─── Variant presets ───

export const fadeUp = {
  hidden: { opacity: 0, y: 12 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: durations.story, ease: easings.confident },
  },
}

export const fadeIn = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { duration: durations.default, ease: easings.default },
  },
}

export const slideInLeft = {
  hidden: { opacity: 0, x: -16 },
  show: {
    opacity: 1, x: 0,
    transition: { duration: durations.confident, ease: easings.confident },
  },
}

export const scaleIn = {
  hidden: { opacity: 0, scale: 0.96 },
  show: {
    opacity: 1, scale: 1,
    transition: { duration: durations.confident, ease: easings.snappy },
  },
}

export const stagger = {
  hidden: { opacity: 1 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.07, delayChildren: 0.05 },
  },
}
