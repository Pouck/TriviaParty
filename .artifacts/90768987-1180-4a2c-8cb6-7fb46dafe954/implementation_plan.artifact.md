# Refactoring Canonical Question Bank and Game Setup for Clean Topics, Performance, and Parity

## Problem Description
1. **Performance Delay**: Switching between setup modes (Aléatoire, Vote, Sujets) causes noticeable lag because categories and question pools are re-computed and re-parsed on every recomposition.
2. **Subject Granularity & Taxonomy**: Fragmented legacy category strings (e.g., `"Architecture — Reconnaissance — Europe — Réponses écrites"`) result in hyper-narrow or malformed subjects (like `"A"` or `"8 jours"`), creating single-question trivia buckets.
3. **Legacy Package Permeation**: `GamePackageRepository` and `CanonicalQuestionBank` still rely on legacy package IDs and flat presentation groups, leaking old package structures into the UI.
4. **Mode Parity**: Vote, Random, and Subject panels should share the exact same clean, hierarchical topic/subject selection model.

---

## Proposed Changes

### 1. Canonical Question Bank & Repository (`CanonicalQuestionBank.kt`, `GamePackageRepository.kt`, `QuestionBankRepository.kt`)
- **Top-Level Canonical Topics**: Replace fragmented legacy category strings with clean, high-level canonical topics (e.g., *Architecture*, *Art*, *History*, *Geography*, *Movies*) derived from `BankQuestion.topics`.
- **Caching**: Cache computed subject/topic lists and question counts in `QuestionBankRepository` to eliminate switching delay.
- **Remove Legacy Package Leakage**: Fully detach `GamePackageRepository` from legacy package ID groupings when canonical bank views are installed.

### 2. Game Setup Screen (`GameSetupScreen.kt`)
- **Unified Selection Model**: Unify Aléatoire, Vote, and Sujets modes to operate on the same clean canonical topics and subjects.
- **Instant Mode Switching**: Use `remember` and cached collections so switching between setup tabs/modes is instantaneous.
- **Clear & Robust Categories**: Ensure every displayed topic/subject has a substantial question pool (no single-question trivia fragments).

---

## Verification Plan

### Automated Tests
- Run unit tests to verify repository loading and category grouping:
  ```bash
  ./gradlew.bat testDebugUnitTest
  ```

### Manual Verification
- Deploy to phone and verify:
  1. Switching between Aléatoire, Vote, and Sujets is instantaneous with zero lag.
  2. Categories/subjects are clean top-level topics (e.g., History, Art, Geography) instead of fragmented legacy paths.
  3. No legacy packages appear in setup.
