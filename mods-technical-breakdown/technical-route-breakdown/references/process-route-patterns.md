# Process Route Patterns

This reference distills reusable route-building patterns from two user-provided documents:

- `ALD_SnO2工艺深度分析：铅硫化物量子点红外芯片的关键挑战与解决方案.pdf`
- `热蒸发_C60_在_8_英寸晶圆上的均匀性解决方案深度分析(1).pdf`

Use these as engineering heuristics, not as fixed recipes.

## Pattern: ALD SnO2 On PbS Quantum-Dot Infrared Chips

Core challenge:
- PbS quantum-dot films and ligand-treated interfaces are chemically and mechanically fragile.
- ALD can provide dense, conformal, low-temperature oxide films, but precursors, oxidants, plasma, heat, and purge history can damage quantum-dot surfaces or change carrier transport.

Key questions:
- What role does SnO2 play: passivation, electron transport, barrier, optical spacer, encapsulation, or contact modification?
- What is the maximum safe thermal budget for the quantum-dot film and ligands?
- Is oxidant exposure causing surface oxidation, ligand displacement, trap formation, or dark-current increase?
- Does plasma assistance improve film quality or create unacceptable interface damage?
- What thickness gives enough coverage/barrier behavior without hurting transport or optical response?
- Which metrology can detect both film quality and device impact: ellipsometry, XPS, AFM, SEM/TEM, water/oxygen barrier tests, IV, EQE, noise, dark current, and stability?

Material requirements:
- Precursors must be compatible with low-temperature growth and leave low carbon/chlorine residue.
- Oxidant choice and dose must be selected for interface gentleness; prefer thermal ALD when plasma damage is suspected.
- Substrates must have controlled ligand state, moisture history, and particle levels before ALD.
- Store and transfer samples to limit oxygen/water exposure; document air-break time.

Equipment comparison dimensions:
- Thermal ALD: gentler interface, lower damage risk, potentially slower and more temperature-sensitive.
- Plasma-enhanced ALD: lower-temperature reactivity and denser films, but higher ion/radical damage risk.
- Batch ALD: higher throughput, but longer exposure history and more complex uniformity control.
- Spatial ALD: higher throughput potential, but requires careful precursor isolation and substrate handling.

Route heuristics:
- Begin with non-plasma low-temperature ALD and short exposure windows.
- Run a matrix of temperature, precursor pulse, oxidant dose, purge time, and thickness.
- Include uncoated and transferred-only controls to distinguish ALD chemistry from handling damage.
- Gate every recipe with both film metrics and device metrics; do not optimize thickness uniformity alone.

## Pattern: Thermal Evaporation C60 On 8-Inch Wafers

Core challenge:
- C60 thickness uniformity across an 8-inch wafer depends on evaporation source geometry, source-to-substrate distance, substrate rotation, fixture shadowing, chamber pressure, rate stability, source condition, and measurement method.
- Device impact may be driven by both thickness nonuniformity and material quality drift during repeated heating.

Key questions:
- What is the target C60 function: electron transport layer, buffer, interlayer, optical spacer, or protective layer?
- What thickness target and within-wafer nonuniformity are acceptable for device yield?
- Is the current nonuniformity radial, angular, edge-related, holder-related, or run-to-run?
- Is the dominant limit source geometry, substrate rotation, chamber pressure, tooling factor, source aging, or metrology bias?
- Is C60 purity and source history stable over repeated evaporation cycles?

Material requirements:
- Prefer high-purity sublimed C60 for device-grade evaporation, especially where the source is repeatedly heated.
- Track supplier, purity grade, batch, residual solvent, oxidation state, source loading, and number of heating cycles.
- Protect source material from oxygen, moisture, particles, and cross-contamination.
- Treat incoming QC and post-run residue checks as part of the route, not purchasing paperwork.

Equipment comparison dimensions:
- Single-point thermal source: simple and low cost; higher radial nonuniformity risk on large wafers.
- Multiple-source evaporation: better shape control; more calibration and matching complexity.
- Large-area linear/boat source: improved coverage potential; source stability and material utilization must be validated.
- Planetary rotation: improves angular/radial averaging; fixture design and edge shadowing remain critical.
- Mask/shaping plate or correction tooling: can tune flux profile; adds contamination and maintenance surfaces.
- In-situ thickness monitoring: useful for rate control; must be correlated with wafer map data.

Route heuristics:
- First map the existing process with dense wafer-point thickness and device data; classify the nonuniformity pattern.
- Calibrate tooling factor by wafer position, not only by the quartz-crystal monitor.
- Adjust source-to-substrate distance, rotation speed, source charge geometry, and correction tooling one factor at a time before complex redesign.
- Use repeated-run testing to capture source aging and chamber seasoning effects.
- Define release criteria for within-wafer uniformity, wafer-to-wafer repeatability, particles, device distribution, and source reuse count.

## Generic Route Template

Use this template to convert the user's challenge into an executable plan:

1. Baseline:
   - Collect current recipe, stack, equipment model, wafer map, defect map, device statistics, and measurement methods.
2. Failure classification:
   - Determine whether the issue is materials, interface chemistry, equipment field, process window, measurement, or integration.
3. Critical experiment:
   - Design a small DOE that isolates the highest-risk variables.
4. Pilot route:
   - Lock a temporary recipe with clear handling, pre-clean, deposition, cooldown, storage, and metrology steps.
5. Quality gates:
   - Define pass/fail thresholds and what decision follows each result.
6. Scale-up:
   - Confirm repeatability over multiple runs, source lots, operators, and maintenance states.
7. Fallback:
   - Provide at least one lower-risk fallback and one higher-performance stretch route.
