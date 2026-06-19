/**
 * Theme tokens — referenced by ECharts and any JS that needs colors.
 * Light/dark variants kept in lock-step so themes feel coherent.
 */

const BRAND = {
  purple:        "#A100FF",
  purpleDark:    "#7F00CC",
  purpleLight:   "#C266FF",
  amber:         "#FBBF24",
  amberDark:     "#F59E0B",
  violet:        "#8B5CF6",
  pink:          "#EC4899",
  cyan:          "#06B6D4",
  emerald:       "#10B981",
  red:           "#EF4444",
  blue:          "#3B82F6",
}

export const THEME = {
  light: {
    bgPage:        "#FAFAFB",
    bgPanel:       "rgba(255,255,255,0.85)",
    border:        "rgba(0,0,0,0.06)",
    borderStrong:  "rgba(161,0,255,0.18)",
    text:          "#0F0F1A",
    textMuted:     "#64748B",
    textFaint:     "#94A3B8",
    grid:          "rgba(0,0,0,0.06)",
    surface:       "#FFFFFF",
    chartBg:       "transparent",
    tooltipBg:     "rgba(15,15,26,0.96)",
    tooltipText:   "#FFFFFF",
    tooltipBorder: "#A100FF",
    accent:        BRAND.purple,
    accentSoft:    "rgba(161,0,255,0.10)",
  },
  dark: {
    bgPage:        "#06030F",
    bgPanel:       "rgba(20,15,40,0.62)",
    border:        "rgba(161,0,255,0.18)",
    borderStrong:  "rgba(161,0,255,0.40)",
    text:          "#F5F5FA",
    textMuted:     "rgba(255,255,255,0.65)",
    textFaint:     "rgba(255,255,255,0.40)",
    grid:          "rgba(255,255,255,0.06)",
    surface:       "rgba(18,12,36,0.85)",
    chartBg:       "transparent",
    tooltipBg:     "rgba(10,0,20,0.96)",
    tooltipText:   "#FFFFFF",
    tooltipBorder: "#A100FF",
    accent:        BRAND.purple,
    accentSoft:    "rgba(161,0,255,0.18)",
  },
}

export const PALETTE = [
  BRAND.purple, BRAND.amber, BRAND.cyan, BRAND.emerald,
  BRAND.violet, BRAND.pink, BRAND.blue, BRAND.red,
]

export const isDark = () =>
  typeof document !== "undefined" &&
  document.documentElement.classList.contains("dark")

export const tokens = () => (isDark() ? THEME.dark : THEME.light)

/** Common ECharts option fragments. Use ...themedAxis() inside any option. */
export const themedAxis = () => {
  const t = tokens()
  return {
    axisLine:   { lineStyle: { color: t.border } },
    axisTick:   { lineStyle: { color: t.border } },
    axisLabel:  { color: t.textMuted, fontFamily: "Inter", fontSize: 11 },
    splitLine:  { lineStyle: { color: t.grid } },
    nameTextStyle: { color: t.textFaint, fontFamily: "Inter", fontSize: 11 },
  }
}

export const themedTooltip = () => {
  const t = tokens()
  return {
    backgroundColor: t.tooltipBg,
    borderColor:     t.tooltipBorder,
    borderWidth:     1,
    textStyle:       { color: t.tooltipText, fontFamily: "Inter", fontSize: 12 },
    extraCssText:    "backdrop-filter: blur(10px); box-shadow: 0 8px 24px rgba(0,0,0,0.4);",
  }
}

export const themedLegend = () => {
  const t = tokens()
  return {
    textStyle: { color: t.textMuted, fontFamily: "Inter", fontSize: 11 },
  }
}
