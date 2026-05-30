---
name: technical-route-breakdown
description: Generate concrete technical route breakdowns for semiconductor, optoelectronic, photovoltaic, thin-film, ALD, thermal evaporation, quantum-dot, and wafer-scale process challenges. Use when a user asks for a technical roadmap, process route, equipment selection, industrialization plan, failure analysis route, or implementation plan that should include clarifying questions, key questions, material requirements, equipment comparison, past experience, and a concrete scheme.
---

# Technical Route Breakdown

## Purpose

Turn an under-specified process or device challenge into an engineering route that a team can discuss, test, and execute. Anchor the answer in the user's documents and known process logic, then separate assumptions from confirmed facts.

When the request references ALD SnO2, PbS quantum-dot infrared chips, thermal evaporation of C60, 8-inch wafers, perovskite devices, or wafer uniformity, read `references/process-route-patterns.md` before answering.

## Interaction Flow

After the user's first request that triggers this skill, ask one mandatory confirmation round before producing the full route. The confirmation must cover demand, purpose, process, equipment, materials, metrics, and constraints. Do not skip this first question round unless the user explicitly says they do not want questions or has already provided all required details in the same message.

Keep the confirmation concise: ask 6-10 numbered questions in one message. If the user asks to proceed without answering, state assumptions and continue with the full route.

Ask about:
- Demand and scope: what technical route, product, module, device, or process section the user wants to solve.
- Purpose and success definition: R&D exploration, pilot-line scale-up, mass production, failure analysis, cost reduction, yield improvement, or supplier/equipment selection.
- Process context: upstream/downstream stack, integration order, sensitive interfaces, thermal budget, cleanroom level, and allowed rework.
- Equipment context: available tools, target tool class, wafer/substrate size, chamber configuration, deposition source, metrology, and maintenance state.
- Materials context: substrate, target/source/precursor, purity grade, supplier, storage, pretreatment, and batch variation.
- Target product and structure: device stack, substrate size, active area, intended volume, and current process baseline.
- Performance targets: efficiency, EQE, dark current, uniformity, yield, lifetime, takt time, or cost limits.
- Current bottleneck: uniformity, interface damage, contamination, adhesion, thermal budget, encapsulation, repeatability, or equipment availability.
- Boundary conditions: available tools, material suppliers, purity grade, cleanroom level, measurement methods, budget, and timeline.
- Evidence already available: recipes, wafer maps, metrology, defect photos, IV/EQE data, thickness data, or prior trial logs.

Use this first-round question template when the user gives only a topic:

1. What is the exact demand: route design, problem diagnosis, equipment selection, material specification, scale-up, or cost/yield optimization?
2. What is the purpose and success metric: R&D proof, pilot production, mass production, reliability, uniformity, efficiency, dark current, or another KPI?
3. What product or device stack is involved, and where is this process located in the stack?
4. What process route is currently considered or used, including temperature, pressure, power, gas/precursor/source, thickness, and post-treatment if known?
5. What equipment is available or planned, including tool type, substrate size, chamber/source configuration, rotation, and in-situ monitoring?
6. What materials are used, including substrate, target/source/precursor, purity grade, supplier, storage, and pretreatment?
7. What constraints matter most: thermal budget, plasma damage, oxygen/water exposure, particles, cost, takt time, yield, or compatibility with downstream steps?
8. What data already exists: wafer maps, film thickness, sheet resistance, optical spectra, IV/EQE, defect images, reliability data, or trial logs?

## Required Output Form

Always output in this order:

1. **User Intake**
   - List the mandatory first-round confirmation questions and the user's answers.
   - If the user skipped answers, list the assumptions used.
   - Mark missing high-impact information.

2. **Key Questions**
   - Convert the problem into 5-10 decision questions.
   - Include acceptance criteria and the experiment or metrology that will answer each question.

3. **Material Requirements**
   - Specify grade, purity, pretreatment, storage, handling, compatibility, and incoming QC.
   - Include risk items such as oxygen/water, residual solvent, particle count, ligand residue, source aging, thermal degradation, and batch variation when relevant.

4. **Equipment Comparison**
   - Compare realistic equipment paths in a table.
   - Include process capability, wafer-scale uniformity, contamination risk, throughput, maintainability, cost, and scaling risk.
   - Make a recommendation and explain the tradeoff.

5. **Past Experience**
   - Summarize comparable experience from the provided references and general domain practice.
   - State what is transferable, what is not, and what must be verified locally.

6. **Concrete Plan**
   - Provide a staged route: baseline characterization, DOE, pilot recipe, process window, quality gates, scale-up, and fallback options.
   - Include measurable targets, sample splits, metrology, decision gates, and expected deliverables.

## Engineering Rules

- Prefer route options that can be verified by measurable wafer maps, device statistics, and repeat runs.
- For film uniformity problems, separate flux/source geometry, substrate motion, temperature field, chamber pressure, tooling shadowing, and measurement bias.
- For interface-sensitive devices, isolate chemical damage, plasma damage, thermal budget, solvent exposure, roughness, and band alignment.
- For industrial route proposals, include material supply chain, incoming QC, SPC, PM cycle, chamber seasoning, and operator repeatability.
- Do not present a single "best" route without naming the assumptions that make it best.
- Use tables for comparisons and decision gates; use concise prose for recommendations.

## Reference Use

Use `references/process-route-patterns.md` for domain heuristics distilled from:
- ALD SnO2 process analysis for PbS quantum-dot infrared chips.
- Thermal evaporation C60 uniformity analysis for 8-inch wafers.

Do not quote the reference as if it were a standard. Treat it as prior engineering experience and adapt it to the user's actual stack, tools, and constraints.
