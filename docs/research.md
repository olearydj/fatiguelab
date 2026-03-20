# Fatigue Failure Theory for Musculoskeletal Disorder Risk Assessment

## Research Summary

This document summarizes the findings from a review of the fatigue failure framework for musculoskeletal disorder (MSD) risk assessment developed by Sean Gallagher, Richard F. Sesek, Mark C. Schall Jr., and collaborators at Auburn University's Department of Industrial & Systems Engineering.

The framework applies classical material fatigue failure theory — specifically S-N curves and Palmgren-Miner cumulative damage — to biological tissues, producing three ergonomic risk assessment tools: **LiFFT**, **DUET**, and the **Shoulder Tool**.

---

## Theoretical Foundation

### Core Premise

Musculoskeletal tissues subjected to repeated loading in vitro fail in accordance with material fatigue failure theory. The same process appears to occur in vivo. Just as metal fatigue leads to structural failure under cyclic loading well below ultimate strength, repetitive occupational loading causes cumulative micro-damage in tendons, spinal motion segments, and other tissues.

Two primary measures drive risk:
1. **Loading magnitude** (as a fraction of ultimate tissue strength)
2. **Number of repetitions**

These interact — the impact of repetition is highly dependent on force level, and vice versa. This interaction is naturally captured by the S-N curve framework.

### S-N Curves for Biological Tissues

An S-N curve plots stress magnitude (S) against the number of cycles to failure (N). For biological tissues, the relationship is log-linear:

```
S = a - b × log₁₀(N)
```

Where S is expressed as a percentage of ultimate tissue strength and N is the median number of cycles to failure.

### Palmgren-Miner Cumulative Damage Rule

Damage from multiple tasks at different stress levels accumulates linearly:

```
CD = Σ (nᵢ / Nᵢ)
```

Where:
- `nᵢ` = number of repetitions at stress level i during a workday
- `Nᵢ` = cycles to failure at stress level i (from the S-N curve)
- `CD` = cumulative damage (0 = undamaged, 1 = theoretical failure)

Equivalently: `CD = Σ (DPCᵢ × nᵢ)` where `DPCᵢ = 1/Nᵢ` is the damage per cycle.

---

## Key Biomechanical Data Sources

### Tendon Fatigue: Schechtman & Bader (1997)

**Paper:** "In vitro fatigue of human tendons." *Journal of Biomechanics*, 30(8):829-835. (PMID: 9239568)

- Tested 90 human **extensor digitorum longus (EDL)** tendon specimens
- 10 specimens per stress level, at 9 levels (10%-90% of UTS)
- Ultimate tensile strength: **100 MPa**
- Cyclic square tension-tension waveform at **4 Hz** (physiological frequency)
- Minimum stress: 1% of UTS (1 MPa)
- Statistical model: Weibull distribution for probability of failure at each stress level
- **Key finding:** No endurance limit — tendons will eventually fail at any cyclic stress level

**S-N Curve Equation:**

```
S = 101.25 - 14.83 × log₁₀(N)
```

Rearranged:

```
N = 10^((101.25 - S) / 14.83)
```

| Stress (% UTS) | Median Cycles to Failure |
|:-:|:-:|
| 10 | ~1,475,000 |
| 20 | ~311,000 |
| 30 | ~65,700 |
| 40 | ~13,900 |
| 50 | ~2,900 |
| 60 | ~617 |
| 70 | ~130 |
| 80 | ~27 |
| 90 | ~6 |

At 20% UTS (~20 MPa), the fatigue life of ~300,000 cycles equates to approximately four months of normal walking activity.

**Note:** An alternative regression by Gallagher & Heberger (2013) gives `S = 93.98 - 13.13 × log₁₀(N)` (R² = 0.88). The 101.25/14.83 version is what the published tools use.

### Spinal Compression: Jager & Luttmann (1991) and Brinckmann et al.

- Ultimate compressive strength of an "average" working-age spine: **~6,000 N (6 kN)**
- LiFFT uses spinal motion segment fatigue data (Brinckmann et al.) rather than the tendon curve
- The relationship between peak load moment and spinal compression was empirically derived

### Schechtman & Bader (2002) Follow-Up

**Paper:** "Fatigue damage of human tendons." *J Biomech*, 35(3):347-353. (PMID: 11858810)

- Tested 12 intact EDL tendons at 20% UTS with partial fatigue (25% of median fatigue life)
- Found peak stress and initial peak strain correlated with cycles to failure
- Rates of peak cyclic strain and modulus loss showed highest correlations (R² = 0.96 and 0.86)
- Failure strain ~15%, consistent across stress levels

---

## The Three Assessment Tools

### Tool 1: LiFFT (Lifting Fatigue Failure Tool)

**Paper:** Gallagher, S., Sesek, R.F., Schall, M.C., & Huangfu, R. (2017). "Development and validation of an easy-to-use risk assessment tool for cumulative low back loading: The Lifting Fatigue Failure Tool (LiFFT)." *Applied Ergonomics*, 63, 142-150.

**Target:** Low back disorders from lifting tasks.

**Inputs (3 variables per task):**
1. Load weight (lb or kg)
2. Maximum horizontal distance from spine to load center (in or cm)
3. Number of repetitions per workday

**Tissue Model:** Spinal motion segment fatigue data (Brinckmann et al.), NOT the tendon S-N curve.

**Peak Load Moment:**

```
Mpl = Load Weight × Horizontal Distance from Spine
```

(In Nm when using SI units)

**Cumulative Damage:**

```
D = Σᵢ (nᵢ / e^(0.038 × Mpl_i + 0.32)) × 1,902,416
```

More precisely, the damage equation from the Exo-LiFFT paper (Eq. 1) is:

```
D = Σᵢ nᵢ / (1,902,416 × e^(-(0.038 × Mpl_i + 0.32)))
```

Which simplifies to:

```
D = Σᵢ nᵢ × e^(0.038 × Mpl_i + 0.32) / 1,902,416
```

**Constants:**

| Constant | Value | Source |
|----------|-------|--------|
| Scalar denominator | 1,902,416 | Empirically derived from cadaveric spine testing |
| Moment coefficient | 0.038 | Empirical relationship between peak load moment and compressive spine force as fraction of ultimate strength |
| Offset | 0.32 | Exponent offset term |

**Probability of High-Risk Job (Logistic Regression):**

```
Y = 1.72 + 1.03 × log₁₀(D)
R = eʸ / (1 + eʸ)
```

Where "high-risk" is defined as a job having ≥12 injuries per 200,000 hours worked (Marras et al., 1993).

**Validation:** The LiFFT cumulative damage metric explained 72-95% of the deviance in low back disorders across two epidemiological databases.

**Caution:** Results should be interpreted carefully for peak moments > 100 Nm.

---

### Tool 2: DUET (Distal Upper Extremity Tool)

**Paper:** Gallagher, S., Schall, M.C., Sesek, R.F., & Huangfu, R. (2018). "An Upper Extremity Risk Assessment Tool Based on Material Fatigue Failure Theory: The Distal Upper Extremity Tool (DUET)." *Human Factors*, 60(8), 1146-1162.

**Target:** Distal upper extremity disorders (hand, wrist, forearm — e.g. carpal tunnel syndrome).

**Inputs (2 variables per task):**
1. Exertion intensity rating on the OMNI-RES scale (0-10)
2. Number of repetitions per workday

**OMNI-RES Scale:**

| Score | Descriptor |
|:-----:|------------|
| 0 | Extremely Easy |
| 2 | Easy |
| 4 | Somewhat Easy |
| 6 | Somewhat Hard |
| 8 | Hard |
| 10 | Extremely Hard |

(Odd numbers are valid intermediate ratings.)

**OMNI-RES to % UTS Mapping (Table 1):**

At 100% MVC, tendon strain is only ~73% of failure strain (Wren et al. 2001). The reciprocal (1/0.73 ≈ 1.4) means failure strain is 1.4× MVC. So OMNI 10 (max effort) = 100/1.4 = 71.4% UTS, not 100%.

**Tissue Model:** Schechtman & Bader (1997) tendon S-N curve.

**Damage Per Cycle:**

DPC is computed from the S-N curve using the Table 1 stress mapping.

**DPC Table (Table 1, Gallagher et al. 2018):**

| OMNI | S (% UTS) | N (cycles to failure) | DPC |
|:----:|:---------:|:---------------------:|:---:|
| 0 | 3.6 | 3,842,605 | 2.60 × 10⁻⁷ |
| 1 | 7.1 | 2,231,607 | 4.48 × 10⁻⁷ |
| 2 | 14.3 | 729,651 | 1.37 × 10⁻⁶ |
| 3 | 21.4 | 242,301 | 4.13 × 10⁻⁶ |
| 4 | 28.6 | 79,223 | 1.26 × 10⁻⁵ |
| 5 | 35.7 | 26,308 | 3.80 × 10⁻⁵ |
| 6 | 42.9 | 8,602 | 1.16 × 10⁻⁴ |
| 7 | 50.0 | 2,856 | 3.50 × 10⁻⁴ |
| 8 | 57.1 | 949 | 1.05 × 10⁻³ |
| 9 | 64.3 | 310 | 3.23 × 10⁻³ |
| 10 | 71.4 | 103 | 9.71 × 10⁻³ |

**Cumulative Damage:**

```text
CD = Σᵢ (DPCᵢ × nᵢ)
```

**Probability of Distal Upper Extremity Outcome (Logistic Regression):**

Equation 6 from Gallagher et al. (2018), for the "Injury + Pain Last Year" outcome:

```text
Y = 0.573 + 0.747 × log₁₀(CD)
P = eʸ / (1 + eʸ)
```

Verified against published examples:
- Figure 2: OMNI=2, 5400 reps → CD=0.0074 → P=26.5% ✓
- Figure 3: Four-task example → CD=0.597 → P≈60.5% ✓

**DUET v1.3.0** (04/19/2018) updated the damage per cycle and related damage-risk relationship with a rounding correction.

---

### Tool 3: Shoulder Tool

**Paper:** Bani Hani, D., Huangfu, R., Sesek, R.F., Schall, M.C. Jr., Davis, G.A., & Gallagher, S. (2021). "Development and validation of a cumulative exposure shoulder risk assessment tool based on fatigue failure theory." *Ergonomics*, 64(1), 39-54.

**Dissertation:** Bani Hani, D. (2019). "Development and Validation of a Cumulative Exposure Shoulder Risk Assessment Tool Based on the Fatigue-Failure Theory." Auburn University.

**Target:** Shoulder musculoskeletal disorders.

**Inputs (3 variables per task):**
1. Weight held or force exerted (lb)
2. Horizontal distance from acromion to load center (in)
3. Number of repetitions per workday
4. Weight distribution between hands (for bilateral tasks)

**Task Types:**
- Handling loads (includes arm weight contribution)
- Horizontal push or pull
- Push or pull downward

**Shoulder Moment Calculation:**

For handling loads:
```
Moment (ft-lb) = [Load(lb) × LeverArm(in) + ArmWeight(lb) × LeverArm(in)/2] / 12
```

For push/pull:
```
Moment (ft-lb) = Load(lb) × LeverArm(in) / 12
```

Where arm weight ≈ 8.6 lb (estimated mass of the arm acting at half the lever arm distance).

**Shoulder Strength Normalization:**

```
Shoulder Strength = 681 in-lb = 56.75 ft-lb = 76.9 Nm
```

Source: 3DSSPP v6.0.6, shoulder strength capability for a 50th percentile male, standing posture, averaged for left and right shoulders.

**Normalized Stress:**

```
S = (Shoulder Moment / Shoulder Strength) × 100    (% UTS)
```

**Tissue Model:** Schechtman & Bader (1997) tendon S-N curve (same as DUET).

**Damage Per Cycle and Cumulative Damage:**

```
N = 10^((101.25 - S) / 14.83)
DPC = 1 / N
CD = Σᵢ (DPCᵢ × nᵢ)
```

The maximum CD between left and right shoulders is used as the risk metric.

**Probability of Shoulder Outcome (Logistic Regression):**

The online tool uses the FTOV (First Time Office Visit) crude model:

```
Y = 0.870 + 0.932 × log₁₀(CD)
P = eʸ / (1 + eʸ)
```

**All Five Outcome Models (from dissertation, crude logistic regression):**

| Outcome | β₀ | β₁ | OR |
|---------|:---:|:---:|:---:|
| FTOV (clinic visit) | 0.864 | 0.928 | 2.53 |
| Current pain (1/2 vs 4/5) | 1.502 | 1.555 | 4.73 |
| Current pain (1 vs 5) | 1.005 | 1.356 | 3.88 |
| Pain last year | 1.046 | 1.040 | 2.83 |
| Pain today | −0.068 | 0.801 | 2.23 |

**Adjusted Odds Ratios (from published paper, Table 3):**

| Outcome | Adjusted OR | 95% CI |
|---------|:-----------:|:------:|
| FTOV | 2.59 | (1.73, 3.89) |
| Pain today | 2.12 | (1.37, 3.28) |
| Pain last year | 2.85 | (1.88, 4.32) |
| 1,2 vs 4,5 | 5.20 | (3.02, 8.95) |
| 1 vs 5 | 3.98 | (2.28, 6.94) |

**Verification Against Published Test Cases (Appendix A of dissertation):**

| Test Case | Inputs | CD | P(FTOV) |
|-----------|--------|:---:|:-------:|
| Mono-task | 2 lb, 16 in, 2880 reps | 0.00428 | 20.8% |
| Two-hand lift | 5 lb/hand, 18 in, 4800 reps | 0.03331 | 37.6% |
| Multi-task (4 tasks) | various | 0.04097 | 39.6% |
| Binning (3 bins) | various | 0.19214 | 55.0% |

---

## Comparison of the Three Tools

| Feature | LiFFT | DUET | Shoulder Tool |
|---------|-------|------|---------------|
| **Body region** | Low back | Distal upper extremity | Shoulder |
| **Tissue model** | Spinal motion segment (Brinckmann) | Tendon (Schechtman & Bader) | Tendon (Schechtman & Bader) |
| **S-N curve** | Exponential (custom) | S = 101.25 − 14.83 log₁₀(N) | S = 101.25 − 14.83 log₁₀(N) |
| **Loading input** | Load × distance (moment) | OMNI-RES rating (0-10) | Force × distance (moment) |
| **Strength reference** | ~6 kN (spine compression) | 71.4% UTS at OMNI 10 | 681 in-lb (3DSSPP) |
| **Logistic β₀** | 1.72 | 0.573 | 0.870 |
| **Logistic β₁** | 1.03 | 0.747 | 0.932 |
| **Deviance explained** | 72-95% | significant dose-response | significant dose-response |

---

## Research Team

### Primary Authors
- **Sean Gallagher** — Originated the application of fatigue failure theory to MSDs. Auburn ISE. Lead author on LiFFT and DUET papers.
- **Richard F. Sesek** — Auburn ISE, Tim Cook Professor. Co-author on all three tools.
- **Mark C. Schall Jr.** — Auburn ISE. Co-author on all three tools.

### Other Key Contributors
- **Rong Huangfu** — Co-author on LiFFT and DUET; Auburn dissertation (2018) contains detailed methodology.
- **Dania Bani Hani** — Lead author on Shoulder Tool paper; Auburn dissertation (2019) contains full derivation.
- **Gerard A. Davis** — Co-author on Shoulder Tool.
- **Menekse S. Barim** — Co-author on torso flexion extension to LiFFT.
- **M. Fehmi Capanoglu** — Co-author on LiFFT extensions.
- **Robert M. Sesek** — Co-author on LiFFT extension work.

### Foundational Biomechanics Researchers (not Auburn)
- **H. Schechtman & D.L. Bader** — Tendon fatigue S-N curve (1997, 2002)
- **M. Jager & A. Luttmann** — Spinal compressive strength data (1991)
- **P. Brinckmann et al.** — Spinal motion segment fatigue data

---

## Existing Online Implementations

The Auburn team hosts three web calculators on PythonAnywhere:
- **LiFFT:** https://lifft.pythonanywhere.com/
- **DUET:** https://duet.pythonanywhere.com/
- **Shoulder Tool:** https://theshouldertool.pythonanywhere.com/

All calculations are server-side (Python/Django). Source code is not publicly available. No GitHub repositories were found.

A related **Exo-LiFFT** calculator (Vanderbilt, Zelik Lab) extends LiFFT for exoskeleton assessment and is available at https://lab.vanderbilt.edu/zelik/resources/exo-lifft/. An Excel worksheet version is also provided.

---

## Key References

### Core Tool Papers
1. Gallagher, S., Sesek, R.F., Schall, M.C., & Huangfu, R. (2017). Development and validation of an easy-to-use risk assessment tool for cumulative low back loading: The Lifting Fatigue Failure Tool (LiFFT). *Applied Ergonomics*, 63, 142-150. https://pubmed.ncbi.nlm.nih.gov/28477843/
2. Gallagher, S., Schall, M.C., Sesek, R.F., & Huangfu, R. (2018). An Upper Extremity Risk Assessment Tool Based on Material Fatigue Failure Theory: The Distal Upper Extremity Tool (DUET). *Human Factors*, 60(8), 1146-1162. https://journals.sagepub.com/doi/abs/10.1177/0018720818789319
3. Bani Hani, D., Huangfu, R., Sesek, R.F., Schall, M.C. Jr., Davis, G.A., & Gallagher, S. (2021). Development and validation of a cumulative exposure shoulder risk assessment tool based on fatigue failure theory. *Ergonomics*, 64(1), 39-54. https://pubmed.ncbi.nlm.nih.gov/32812850/

### Foundational Biomechanics
4. Schechtman, H. & Bader, D.L. (1997). In vitro fatigue of human tendons. *Journal of Biomechanics*, 30(8), 829-835. https://pubmed.ncbi.nlm.nih.gov/9239568/
5. Schechtman, H. & Bader, D.L. (2002). Fatigue damage of human tendons. *J Biomech*, 35(3), 347-353. https://pubmed.ncbi.nlm.nih.gov/11858810/

### Theoretical Framework
6. Gallagher, S. & Heberger, J.R. (2013). Examining the Interaction of Force and Repetition on Musculoskeletal Disorder Risk. *Human Factors*, 55(1), 108-124. https://pmc.ncbi.nlm.nih.gov/articles/PMC4495348/
7. Gallagher, S. & Schall, M.C. (2017). Musculoskeletal disorders as a fatigue failure process. *Human Factors*, 59(2), 351-360. https://stacks.cdc.gov/view/cdc/211461/cdc_211461_DS1.pdf

### Extensions
8. Capanoglu, M.F., Barim, M.S., Sesek, R.F., Sesek, R.M., Schall, M.C., & Gallagher, S. (2023). Exploring the Addition of Torso Flexion to the LiFFT Analysis Tool. *Proceedings of the Human Factors and Ergonomics Society*. https://journals.sagepub.com/doi/abs/10.1177/21695067231199687
9. Exo-LiFFT paper (PMC): https://pmc.ncbi.nlm.nih.gov/articles/PMC9827614/

### Dissertations
10. Huangfu, R. (2018). [Dissertation, Auburn University]. https://etd.auburn.edu/bitstream/handle/10415/6542/Dissertation_RongHuangfu_Final.pdf
11. Bani Hani, D. (2019). Development and Validation of a Cumulative Exposure Shoulder Risk Assessment Tool Based on the Fatigue-Failure Theory. [Dissertation, Auburn University]. https://etd.auburn.edu/handle/10415/6964

---

## Confidence Assessment

| Element | Confidence | Source |
|---------|:----------:|--------|
| Tendon S-N curve (101.25, 14.83) | **High** | Published in Shoulder Tool paper, Bani Hani dissertation, multiple reviews |
| LiFFT damage equation (1,902,416 / 0.038 / 0.32) | **High** | Published in Exo-LiFFT paper (PMC9827614) |
| LiFFT logistic regression (1.72 / 1.03) | **High** | Published in Exo-LiFFT paper |
| DUET OMNI-RES → % UTS mapping (Table 1) | **High** | Verified against Table 1 of Gallagher et al. (2018); each OMNI point ≈ 7.14% UTS |
| DUET logistic regression (0.573 / 0.747) | **High** | Equation 6 of Gallagher et al. (2018); verified against Figures 2 and 3 |
| Shoulder Tool moment calculation | **High** | From dissertation and online tool |
| Shoulder Tool strength (681 in-lb) | **High** | From dissertation variable naming and 3DSSPP |
| Shoulder Tool FTOV logistic (0.870 / 0.932) | **High** | From dissertation fitted line plots and verified against test cases |
| Shoulder Tool all 5 outcome models | **High** | From dissertation |

---

## Open Questions

1. ~~**DUET logistic coefficients**~~ — Resolved. Coefficients are β₀ = 0.573, β₁ = 0.747 from Equation 6 of Gallagher et al. (2018), for the "Injury + Pain Last Year" outcome. Verified against Figures 2 and 3 in the paper.

2. ~~**OMNI-RES to % UTS mapping in DUET**~~ — Resolved. Table 1 of Gallagher et al. (2018) gives explicit mappings: each OMNI point ≈ 100/14 ≈ 7.14% UTS (not 10%). At 100% MVC, tendon strain is ~73% of failure strain (Wren et al. 2001), so OMNI 10 = 71.4% UTS.

3. **LiFFT damage equation form** — The equation `D = Σ nᵢ × e^(0.038 × Mpl_i + 0.32) / 1,902,416` needs careful attention to whether the exponential is in the numerator or denominator. The Exo-LiFFT paper (Eq. 1) presents it as a ratio, and the denominator form is: `D = Σ nᵢ / [1,902,416 × e^(-(0.038 × Mpl_i + 0.32))]`. Both are equivalent.

4. **Shoulder Tool arm weight** — The ~8.6 lb value was reverse-engineered from tool outputs and verified against Figures 8-10 of Bani Hani et al. (2021). Reproduces published examples accurately. The tool may use a more sophisticated anthropometric model internally.

5. **Healing/recovery** — The theoretical framework acknowledges tissue healing (~1% per day for tendons), but none of the current tools incorporate a healing function. All assess single-day cumulative damage only.

6. **Torso flexion extension to LiFFT** — Capanoglu et al. (2023) explored adding torso flexion as a variable. The details of this extension were not fully extracted.
