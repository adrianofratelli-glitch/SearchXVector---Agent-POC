import { palette } from "@leafygreen-ui/palette";

// Paleta MongoDB Atlas (LeafyGreen) — tokens reutilizados no app
export const T = {
  bg:        palette.black,          // #001E2B — fundo Atlas dark
  surface:   "#00263A",              // cards / superfícies elevadas
  surface2:  "#002A40",
  sidebar:   "#00141C",
  border:    "rgba(0,237,100,0.12)",
  borderSub: "rgba(255,255,255,0.08)",

  green:     palette.green.base,     // #00ED64
  greenDark: palette.green.dark1,
  blue:      "#0498EC",
  purple:    "#B45AF2",
  yellow:    "#FFC010",
  teal:      "#00D2FF",
  red:       "#FF6960",

  text:      "#E3FCF7",
  text2:     palette.gray.base,      // #889397
  text3:     "#5C6C75",

  font: "'Euclid Circular A', 'Helvetica Neue', Arial, sans-serif",
  mono: "'Source Code Pro', Menlo, monospace",
};

export const fmtCount = (n) => {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + "M";
  if (n >= 1_000) return Math.round(n / 1_000) + "k";
  return String(n ?? 0);
};

export const fmtBRL = (v) =>
  "R$ " + (v ?? 0).toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
