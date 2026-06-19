import { useState, useRef, useEffect } from "react"
import { createPortal } from "react-dom"
import { Info } from "lucide-react"
import { getTooltip } from "../../utils/tooltipDefinitions"

/**
 * Info tooltip rendered via React Portal so it ALWAYS floats above
 * everything — escapes parent overflow:hidden, transform, z-index issues.
 *
 * Position is computed from the icon's getBoundingClientRect() so the
 * tooltip lands relative to the viewport, not relative to a transformed
 * ancestor.
 */
export default function InfoTooltip({ label, text, size = "sm" }) {
  const message = text || getTooltip(label)
  const triggerRef = useRef(null)
  const [open, setOpen] = useState(false)
  const [pos, setPos] = useState({ left: 0, top: 0, placement: "top" })

  if (!message) return null

  const sizeClass = size === "xs" ? "w-3 h-3" : size === "sm" ? "w-3.5 h-3.5" : "w-5 h-5"

  // Compute tooltip position when opening
  const computePosition = () => {
    if (!triggerRef.current) return
    const rect = triggerRef.current.getBoundingClientRect()
    const TOOLTIP_W = 256
    const TOOLTIP_H_EST = 110          // estimated; will self-correct visually
    const GAP = 8
    const PAD = 8                       // edge padding from viewport

    const vw = window.innerWidth
    const vh = window.innerHeight

    // Default: place ABOVE icon, centered horizontally
    let left = rect.left + rect.width / 2 - TOOLTIP_W / 2
    let top = rect.top - TOOLTIP_H_EST - GAP
    let placement = "top"

    // Flip below if not enough space above
    if (top < PAD) {
      top = rect.bottom + GAP
      placement = "bottom"
    }

    // Clamp horizontally to viewport
    if (left < PAD) left = PAD
    if (left + TOOLTIP_W > vw - PAD) left = vw - PAD - TOOLTIP_W

    setPos({ left, top, placement })
  }

  // Recompute on open + on scroll/resize while open
  useEffect(() => {
    if (!open) return
    computePosition()
    const handler = () => computePosition()
    window.addEventListener("scroll", handler, true)   // capture for nested scrollers
    window.addEventListener("resize", handler)
    return () => {
      window.removeEventListener("scroll", handler, true)
      window.removeEventListener("resize", handler)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open])

  const handleEnter = () => setOpen(true)
  const handleLeave = () => setOpen(false)
  const handleFocus = () => setOpen(true)
  const handleBlur = () => setOpen(false)

  return (
    <>
      <span
        ref={triggerRef}
        className="inline-flex relative align-middle cursor-help"
        onMouseEnter={handleEnter}
        onMouseLeave={handleLeave}
        onFocus={handleFocus}
        onBlur={handleBlur}
        tabIndex={0}
        aria-label={`Definition of ${label}`}
      >
        <Info
          className={`${sizeClass} transition opacity-70 hover:opacity-100`}
          style={{ color: open ? "#A100FF" : "var(--text-faint)" }}
        />
      </span>

      {open && createPortal(
        <div
          role="tooltip"
          style={{
            position: "fixed",
            left: pos.left,
            top: pos.top,
            width: 256,
            zIndex: 99999,
            pointerEvents: "none",
            background: "linear-gradient(135deg, #1A0033 0%, #0A0014 100%)",
            border: "1px solid rgba(161,0,255,0.55)",
            borderRadius: 10,
            padding: "10px 12px",
            boxShadow: "0 16px 40px rgba(0,0,0,0.55), 0 0 22px rgba(161,0,255,0.25)",
            color: "#fff",
            fontFamily: "Inter, system-ui, sans-serif",
            animation: "fadeIn 0.15s ease-out",
          }}
        >
          <div
            style={{
              fontSize: 9,
              fontWeight: 800,
              textTransform: "uppercase",
              letterSpacing: "0.14em",
              color: "#C266FF",
              marginBottom: 4,
              lineHeight: 1.2,
            }}
          >
            {label}
          </div>
          <div style={{ fontSize: 12, lineHeight: 1.5, color: "rgba(255,255,255,0.92)" }}>
            {message}
          </div>
        </div>,
        document.body
      )}
    </>
  )
}
