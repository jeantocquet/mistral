# Partenaires Peisey-Vallandry — slide Beamer vectoriel

Reproduction en **format vectoriel** de la diapositive « Merci à nos partenaires »
(image source : `uEHbguRS-image.png`, 810×806).

## Contenu

- `partenaires.tex` — le slide Beamer (16:9, bandeau turquoise #00AEC7)
- `partenaires.pdf` — rendu compilé (tectonic / XeTeX)
- `partenaires_preview.png` — aperçu PNG du rendu
- `logos/pdf/*.pdf` — chaque logo en **PDF vectoriel** (un vectoriel par logo, prêt pour `\includegraphics`)
- `logos/vec/*.svg` — chaque logo en **SVG** (sources éditables)
- `logos/svg/` — SVG officiels téléchargés (Intersport, esf)
- `logos/src_*.png` — recadrages d'origine (entrées de la vectorisation)
- `trace_logos.py` — pipeline de vectorisation (k-means couleurs + potrace multi-couches)

## Logos identifiés (ordre du slide)

| Angles | Source vectorielle |
|---|---|
| Mairie de Landry / SIVOM | tracé vectoriel depuis l'image |
| Ski Club Peisey-Vallandry (Paradiski) | tracé vectoriel |
| Commune de Peisey-Nancroix (blason) | tracé vectoriel |
| STR Terrassements Richermoz | tracé vectoriel |
| Intersport | SVG officiel (Wikimedia/intersport.com) ; version tracée de la composition complète aussi fournie (`intersport.pdf` = avec « PEISEY-VALLANDRY » et site web) |
| Aux Enfants Terribles de Montagne | tracé vectoriel |
| RPB | tracé vectoriel |
| Sherpa — mon super marché | tracé vectoriel |
| A.D.S. Domaine Skiable | tracé vectoriel |
| Fédération Française de Ski (coq) | tracé vectoriel (SVG officiel indisponible ; Wikimedia en 429) |
| esf Peisey-Vallandry | tracé vectoriel (composition locale ; SVG officiel esf aussi fourni : `esf_off.pdf`) |
| Comité Ski Savoie | tracé vectoriel |
| Carré Neige | tracé vectoriel |

Le bandeau « MERCI À NOS PARTENAIRES » est refait nativement en LaTeX
(boîte colorée) — donc 100 % vectoriel également.

## Compilation

```sh
tectonic partenaires.tex     # ou pdflatex/xelatex
```

## Méthode de vectorisation

Pour chaque logo : recadrage → recadrage auto des marges blanches →
agrandissement ×6 (Lanczos) + netteté → clustering k-means (≤6 couleurs)
sur les pixels d'encre → masque par couleur → tracé potrace (courbes
Bézier, trous gérés par fill-rule) → SVG multi-chemins → PDF (svglib).
Les mini-détails (< 12 px à l'échelle 6×) sont éliminés comme bruit.

Qualité : fidèle à l'image fournie ; pour un rendu « charte graphique »
parfait des logos nationaux (Intersport, esf, FFS), préférer
ultérieurement le SVG officiel fourni par chaque marque.
