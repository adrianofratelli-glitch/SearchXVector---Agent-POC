import { palette } from "@leafygreen-ui/palette";

// Paleta no estilo da pitch five-pillar (MongoDB Atlas dark)
export const T = {
  bg:        palette.black,            // #001E2B — fundo Atlas dark
  surface:   "#002838",                // bg-secondary — painéis
  surface2:  "#003345",                // bg-card — superfícies elevadas
  sidebar:   "#00141C",
  border:    "rgba(255,255,255,0.06)", // border-subtle
  borderSub: "rgba(255,255,255,0.06)",
  borderAcc: "rgba(0,237,100,0.25)",   // border-accent

  green:     palette.green.base,       // #00ED64
  greenDark: palette.green.dark1,
  blue:      "#06b6d4",                // cyan da pitch
  purple:    "#a855f7",
  yellow:    "#f97316",                // orange da pitch
  teal:      "#14b8a6",
  red:       "#FF6960",

  text:      "#fafafa",
  text2:     "#b8d8e8",
  text3:     "#7fa8bc",

  codeBg:    "#0a1628",                // fundo dos blocos de código

  font: "'Outfit', 'Helvetica Neue', Arial, sans-serif",
  mono: "'JetBrains Mono', Menlo, monospace",
};

export const fmtCount = (n) => {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + "M";
  if (n >= 1_000) return Math.round(n / 1_000) + "k";
  return String(n ?? 0);
};

export const fmtBRL = (v) =>
  "R$ " + (v ?? 0).toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
