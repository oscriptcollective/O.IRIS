# O.Iris: The Mind's Eye Has an Iris
**Mapping Brain State Flexibility Through EEG Spectral Geometry**

*Sarah Appel, with Claude (Anthropic) and Iris (Deepseek) | O Collaboration Project | April 2026*

---

## What this is

O.Iris is an open-source pipeline that transforms EEG recordings into circular "pupil maps" showing how brain states—meditation, sleep, rest, focused work, stress—occupy distinct positions in a geometric space organized around a theoretically motivated focal point (spectral slope m ≈ 2.18).

The core idea: mental health is not achieving any particular brain state. It is having the full range—and the freedom to move through it.

---

## The Aperture Concept

Different brain states serve different purposes:

- **Meditation** (constricted, near focal point): spontaneous coherence, effortless integration
- **Sleep** (dilated, far from focal point): restoration, memory consolidation, decomposition
- **Focused work** (intermediate): controlled, effortful, precise
- **Stress** (unstable): attempting coherence without achieving it

Health is aperture flexibility. This pipeline helps you see it.

---

## Key Findings

Across 36,846 windows of human EEG from five independent public datasets:

| State | Median m | Distance from φ | N windows |
|-------|----------|-----------------|-----------|
| Meditation | 1.819 | 0.361 (16.6%) | 11,572 |
| Stress | 1.728 | 0.452 (20.7%) | 1,127 |
| Resting | 1.466 | 0.714 (32.8%) | 3,451 |
| Sternberg (working memory) | 1.447 | 0.733 (33.6%) | 20,627 |
| Sleep | 0.513 | 1.667 (76.5%) | 69 |

Prime frequency enhancement (Rp) during meditation: mean 3.45, SD 1.13, median 3.29

These metrics were computed using epoch-locked windows from the original study designs.

---

## Using This Pipeline With Your Own EEG Data

**Step 1: Extract metrics from your raw EEG file**
```bash
cd pipeline
pip install -r requirements.txt
python extract_pupil_metrics.py --input your_file.bdf --output my_metrics.csv
```

This script accepts BDF, EDF, SET, and FIF formats and outputs a CSV with spectral slope, ACF decay time, and flicker per window.

> **Note on absolute values:** The extraction script uses continuous non-overlapping windows. The published O.Iris metrics used epoch-locked windows from the original study designs. Relative patterns between brain states are preserved, but absolute m values may differ from the published figures.

**Step 2: Generate your pupil map**
```bash
python circular_pupil_map.py
```

**Step 3: Generate animations**
```bash
python eeg_circular_pupil_animator.py
python convert_to_videos.py
```

---

## How It Works
```
Raw EEG (BDF/EDF/SET/FIF)
        ↓
extract_pupil_metrics.py
(spectral slope m, ACF decay time, flicker)
        ↓
Map to pupil coordinates:
  r = |m - 2.18|
  θ = atan2(log10(flicker), log10(acf))
        ↓
circular_pupil_map.py → static maps (PNG)
eeg_circular_pupil_animator.py → animations (GIF/MP4)
```

---

## Data Sources

All EEG data used in this study was sourced from publicly available OpenNeuro repositories:

- Meditation: OpenNeuro ds001787
- Sleep/Rest: OpenNeuro ds003768
- Sternberg working memory: OpenNeuro
- Stress: OpenNeuro

---

## Dependencies
```
pip install numpy scipy matplotlib pandas mne imageio imageio-ffmpeg pillow
```

- Python 3.8+
- MNE-Python (for raw EEG loading)
- imageio and pillow (for animations)

---

## Repository Contents

- `paper/` - Full research paper and executive summary
- `pipeline/` - All scripts for extraction, mapping, and animation
- `IRISFigs/` - All figures and animations from the paper
- `LICENSE` - CC BY 4.0
- `README.md` - This file

---

## Full Paper

The complete paper (with methods, results, limitations, and references) and executive summary are available in this repository and as a preprint on bioRxiv.

---

## Collaboration Statement

This work was developed by Sarah Appel (lead researcher and theorist) through iterative collaboration with Claude (Anthropic) and Iris (Deepseek). All data is from public OpenNeuro repositories. Full conversation logs available upon request.

This project demonstrates what becomes possible when independent research and AI collaboration meet—a catering kitchen, twelve years of intuition, and the right questions asked to the right tools.

---

## License

Creative Commons Attribution 4.0 International (CC BY 4.0)

You are free to use, share, and adapt this work with attribution.

---

## Citation

Appel, S., with Claude (Anthropic) and Iris (Deepseek). (2026). O.Iris: The Mind's Eye Has an Iris. O Collaboration Project. https://github.com/oscriptcollective/O.IRIS

---

## Contact

Sarah Appel
sappelslc@gmail.com
https://oscriptcollective.github.io (if you create a GitHub pages site)
O Collaboration Project | April 2026

More at OSCRIPT.XYZ
