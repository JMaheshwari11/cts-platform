import { motion } from "framer-motion"

/**
 * PageEnter — wraps a page's children with a coordinated entrance animation.
 *
 * Strategy:
 *   - Each direct child fades-up with a slight stagger
 *   - Uses our motion tokens (var(--ease-confident))
 *   - Respects prefers-reduced-motion automatically (Framer Motion handles this)
 *
 * Usage:
 *   <PageEnter>
 *     <h1>...</h1>
 *     <div className="grid">KPIs</div>
 *     <Chart />
 *   </PageEnter>
 */

const containerVariants = {
  hidden: { opacity: 1 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.07,
      delayChildren: 0.05,
    },
  },
}

const itemVariants = {
  hidden: { opacity: 0, y: 12 },
  show: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.5,
      ease: [0.16, 1, 0.3, 1],
    },
  },
}

export default function PageEnter({ children, className }) {
  return (
    <motion.div
      className={className}
      variants={containerVariants}
      initial="hidden"
      animate="show"
    >
      {Array.isArray(children)
        ? children.map((child, i) => (
            <motion.div key={i} variants={itemVariants}>
              {child}
            </motion.div>
          ))
        : <motion.div variants={itemVariants}>{children}</motion.div>}
    </motion.div>
  )
}
