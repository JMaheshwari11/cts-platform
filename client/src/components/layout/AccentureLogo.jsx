export default function AccentureLogo({ collapsed = false }) {
  if (collapsed) {
    return (
      <div className="w-9 h-9 flex items-center justify-center">
        <span
          style={{
            color: "#A100FF",
            fontSize: "1.75rem",
            fontWeight: 800,
            lineHeight: 1,
            textShadow: "0 0 12px rgba(161,0,255,0.7)",
          }}
        >
          &gt;
        </span>
      </div>
    )
  }
  return (
    <div className="flex items-center gap-2">
      <span
        style={{
          color: "#A100FF",
          fontSize: "1.875rem",
          fontWeight: 800,
          lineHeight: 1,
          textShadow: "0 0 12px rgba(161,0,255,0.7)",
        }}
      >
        &gt;
      </span>
      <span
        style={{
          color: "#FFFFFF",
          fontSize: "1rem",
          fontWeight: 800,
          letterSpacing: "-0.01em",
        }}
      >
        Accenture S&amp;C
      </span>
    </div>
  )
}