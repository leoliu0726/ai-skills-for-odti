# SCI Review Report Template

## Overview

This template provides a standardized structure for generating SCI peer review reports. The report consists of three main sections:

1. **Overall Summary**: Brief evaluation of the manuscript
2. **Detailed Comments**: Specific, actionable feedback
3. **Recommendation**: Final decision with justification

---

## Report Structure

```
# SCIENTIFIC REVIEW REPORT
================================================================================

[Header Information]
- Review ID
- Date
- Target Journal Style

[Opening Statement]
Standard salutation

================================================================================
OVERALL SUMMARY
================================================================================

[Manuscript Information]
- Title
- Authors

[Summary Assessment]
Paragraph 1: Novelty and significance
Paragraph 2: Strengths and weaknesses
Paragraph 3: Overall recommendation summary

================================================================================
DETAILED COMMENTS
================================================================================

[Critical Issues] (if any)
1. [Issue Title]
   Location: Section X.X, Page X
   Comment: [Specific feedback]
   Evidence: [Quote or data reference]

[Major Comments]
1. [Issue Title]
   Location: Section X.X, Page X
   Comment: [Specific feedback]
   Evidence: [Quote or data reference]

[Minor Comments]
1. [Suggestion Title]
   Location: Section X.X, Page X
   Comment: [Specific feedback]

[Editorial Notes]
1. [Note Title]
   Comment: [Format/language suggestions]

[AI Reference Comments]
Note: These are AI-generated reference comments for consideration only.
1. [AI observation]
   [Uncertain - requires verification]

================================================================================
RECOMMENDATION
================================================================================

Recommendation: [Accept / Minor Revision / Major Revision / Reject]
Reason: [Brief justification]

================================================================================
```

---

## Language Guidelines

### Opening Statements
```
Nature/Science style:
"To the Editor:
We were pleased to review this manuscript..."

Standard style:
"Dear Editor,
The manuscript by [Authors] reports on..."
```

### Positive Language
- "The authors demonstrate..."
- "The study provides valuable insight into..."
- "The methodology is well-established..."
- "The results are compelling and support..."

### Constructive Criticism
- "However, we have concerns regarding..."
- "It would strengthen the manuscript if..."
- "The authors should consider..."
- "Additional information is needed regarding..."

### Certainty Levels
- **Definite**: "The data clearly shows..."
- **Likely**: "This suggests that..."
- **Possible**: "This may indicate..."
- **Uncertain**: "[Uncertain] The authors claim..."

---

## Location Reference Formats

### Standard Format
```
Section 2.1, Page 5, Paragraph 2
Figure 3a, Panel B
Table 2, Entry 4
Line 15-18
```

### Accepted Variations
- "In the Results section (page 7)"
- "Figure 2 demonstrates..."
- "As shown in Table 1..."
- "The method described on page 3"

---

## Comment Writing Best Practices

### Good Comment Structure
1. **State the issue clearly**: "The statistical analysis is inappropriate because..."
2. **Provide evidence**: "The authors used a t-test for non-parametric data..."
3. **Suggest improvement**: "A Mann-Whitney U test would be more appropriate..."

### Common Pitfalls to Avoid
- Vague statements without specific references
- Personal opinions stated as facts
- Demanding changes without justification
- Ignoring positive aspects of the work

---

## Severity Level Examples

### Fatal (Critical)
```
Location: Results section, Page 8
Issue: Incorrect statistical analysis
Comment: The primary conclusion is based on an improper statistical 
method. The data (shown in Figure 3) clearly violates the assumption 
of normality required for ANOVA. This invalidates the main finding 
reported in lines 45-50.
Evidence: "A Shapiro-Wilk test of the data reveals p < 0.01..."
Recommendation: The analysis must be repeated with non-parametric 
methods before the manuscript can be reconsidered.
```

### Major
```
Location: Section 2.3, Page 5, Paragraph 3
Issue: Insufficient sample size
Comment: The sample size (n=5 per group) appears inadequate for 
detecting the effect sizes reported. Post-hoc power analysis suggests 
power = 0.45, below the conventional 0.80 threshold.
Evidence: "Using G*Power with the observed effect size (d=0.6)..."
Recommendation: Additional replicates should be included, or the 
expected effect size should be justified based on preliminary data 
or literature.
```

### Minor
```
Location: Figure 2 legend
Issue: Unclear axis labels
Comment: The y-axis label "Response" is ambiguous. Please specify 
the unit of measurement.
Recommendation: Change to "Response (%)" or "Signal Intensity (AU)"
```

### Editorial
```
Location: Throughout manuscript
Issue: Inconsistent terminology
Comment: The authors use "participants" (page 3) and "subjects" 
(pages 5, 8) interchangeably. Please choose one term and use it 
consistently.
```

---

## AI Reference Comments Format

When documenting AI observations for human review:

```
[AI reference comments]

1. [Observation]
   Location: [Where observed]
   Original text: "[Quote if applicable]"
   Note: [AI interpretation]

   [Uncertain - requires human verification]
```

### Example
```
[AI reference comments]

1. Potential comparison missing
   Location: Discussion, Page 12, Paragraph 2
   Original text: "Our results are consistent with previous studies"
   Note: The authors do not cite specific studies for comparison.
   
   [Uncertain - requires human verification]
```
