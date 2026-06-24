import { useState, useRef, useEffect } from "react"
import { createPortal } from "react-dom"
import { Info } from "lucide-react"
import { getTooltip } from "../../utils/tooltipDefinitions"

/**
 * Tiny ⓘ that opens a structured mini-card.
 * Content has 3 lines: what / how / good.
 * Renders to document.body via Portal so it escapes all overflow:hidden parents.
 */
export default function InfoTooltip({ label, text, size = "sm" }) {
  // Resolve content: prefer structured object, fall back to plain text
  const tip = getTooltip(label)
  const fallbackText = text || (typeof tip === "string" ? tip : null)
  const structured = tip && typeof tip === "object" ? tip : null

  const triggerRef = useRef(null)
  const [open, setOpen] = useState(false)
  const [pos, setPos] = useState({ left: 0, top: 0 })

  if (!structured && !fallbackText) return null

  const sizeClass = size === "xs" ? "w-3 h-3" : size === "sm" ? "w-3.5 h-3.5" : "w-5 h-5"

  // Compute viewport-relative position
  const computePosition = () => {
    if (!triggerRef.current) return
    const rect = triggerRef.current.getBoundingClientRect()
    const TOOLTIP_W = 320
    const TOOLTIP_H_EST = structured ? 200 : 100
    const GAP = 8
    const PAD = 8

    const vw = window.innerWidth
    const vh = window.innerHeight

    // Default: place ABOVE icon, centered horizontally
    let left = rect.left + rect.width / 2 - TOOLTIP_W / 2
    let top = rect.top - TOOLTIP_H_EST - GAP

    // Flip below if not enough room above
    if (top < PAD) {
      top = rect.bottom + GAP
    }

    // Clamp horizontally
    if (left < PAD) left = PAD
    if (left + TOOLTIP_W > vw - PAD) left = vw - PAD - TOOLTIP_W

    setPos({ left, top })
  }

  useEffect(() => {
    if (!open) return
    computePosition()
    const handler = () => computePosition()
    window.addEventListener("scroll", handler, true)
    window.addEventListener("resize", handler)
    return () => {
      window.removeEventListener("scroll", handler, true)
      window.removeEventListener("resize", handler)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open])

  return (
    <>
      <span
        ref={triggerRef}
        className="inline-flex relative align-middle cursor-help"
        onMouseEnter={() => setOpen(true)}
        onMouseLeave={() => setOpen(false)}
        onFocus={() => setOpen(true)}
        onBlur={() => setOpen(false)}
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
            width: 320,
            zIndex: 99999,
            pointerEvents: "none",
            background: "linear-gradient(135deg, #1A0033 0%, #0A0014 100%)",
            border: "1px solid rgba(161,0,255,0.55)",
            borderRadius: 12,
            padding: "12px 14px",
            boxShadow: "0 16px 40px rgba(0,0,0,0.55), 0 0 22px rgba(161,0,255,0.25)",
            color: "#fff",
            fontFamily: "Inter, system-ui, sans-serif",
            animation: "fadeIn 0.15s ease-out",
          }}
        >
          {/* Label badge */}
          <div
            style={{
              fontSize: 9,
              fontWeight: 800,
              textTransform: "uppercase",
              letterSpacing: "0.16em",
              color: "#C266FF",
              marginBottom: 8,
              lineHeight: 1.2,
            }}
          >
            {label}
          </div>

          {structured ? (
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              <Section heading="What it is" body={structured.what} accent="#FFFFFF" />
              <Section heading="How it's calculated" body={structured.how} accent="#A5B4FC" mono />
              <Section heading="What good looks like" body={structured.good} accent="#FBBF24" />
            </div>
          ) : (
            <div style={{ fontSize: 12, lineHeight: 1.55, color: "rgba(255,255,255,0.92)" }}>
              {fallbackText}
            </div>
          )}
        </div>,
        document.body
      )}
    </>
  )
}

function Section({ heading, body, accent, mono }) {
  return (
    <div>
      <div
        style={{
          fontSize: 8.5,
          fontWeight: 800,
          textTransform: "uppercase",
          letterSpacing: "0.14em",
          color: "rgba(255,255,255,0.45)",
          marginBottom: 2,
        }}
      >
        {heading}
      </div>
      <div
        style={{
          fontSize: 11.5,
          lineHeight: 1.5,
          color: accent,
          fontFamily: mono ? "JetBrains Mono, monospace" : "Inter, system-ui, sans-serif",
        }}
      >
        {body}
      </div>
    </div>
  )
}
