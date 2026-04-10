# 🔍 Requirements Gap Analyzer

A tool that analyzes Product Requirement Documents (PRDs) to identify missing requirements, ambiguity, and gaps — with severity classification and a quality score.

---

## 🚀 Overview

PRDs are often incomplete or ambiguous, leading to misalignment between product, engineering, and stakeholders.

This tool helps:
- Detect missing requirement sections
- Identify vague or unclear statements
- Provide actionable suggestions
- Quantify PRD quality using a scoring system

---

## ✨ Features

- 📄 Analyze PRDs from multiple inputs:
  - Text input
  - PDF upload
  - DOCX upload
  - TXT files

- ⚠️ Detect requirement gaps:
  - Acceptance criteria
  - Edge cases
  - Dependencies
  - Security & privacy
  - KPIs / metrics

- 🧠 Identify ambiguity:
  - Flags vague terms like *“fast”*, *“easy”*, *“scalable”*

- 🎯 Severity classification:
  - High → Missing critical requirements
  - Medium → Ambiguous or unclear
  - Low → Minor improvements

- 📊 PRD Quality Score:
  - Weighted scoring system based on severity

- ✅ Requirement coverage checklist

- 📥 Export analysis as CSV

---

## 🧠 How It Works

The tool uses rule-based text analysis:

1. Converts input into structured text
2. Scans for required requirement categories
3. Detects vague or ambiguous language
4. Assigns severity levels
5. Computes a quality score
6. Generates actionable insights

---

## 📊 Scoring Logic

The PRD Quality Score is calculated using a weighted penalty system based on detected issues.

Score = 100 - (15 × High Severity Issues + 8 × Medium Severity Issues + 3 × Low Severity Issues)

Where:
- High severity issues represent missing critical requirements such as acceptance criteria, edge cases, dependencies, security, or KPIs.
- Medium severity issues represent ambiguous or unclear requirements (e.g., vague terms like "fast", "easy").
- Low severity issues represent minor improvements or refinements.

The final score is bounded between 0 and 100.

Higher score → Better structured and more complete PRD  
Lower score → More gaps, ambiguity, and missing requirements
