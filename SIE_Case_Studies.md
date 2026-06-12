# Auto Family ID Engine Ver.0.1

## 1. Purpose

Auto Family ID Engine automatically assigns or suggests a manuscript family ID when a new manuscript file is registered.

Its purpose is to prevent confusion caused by title changes, version changes, translations, journal-specific rewrites, and derivative manuscripts.

The system does not insert the ID into the submitted manuscript.

The ID is used only inside ArcVault / Submission Integrity Engine.

---

## 2. Basic Principle

A manuscript’s identity is not determined by its current title.

It is determined by:

* core research question
* theoretical framework
* abstract similarity
* keyword similarity
* version lineage
* file history
* submission history
* DOI / OSF / preprint linkage

Therefore, even if the title changes, the system should detect whether the manuscript belongs to an existing family.

---

## 3. Workflow

New manuscript imported
↓
Extract title, abstract, keywords, headings, file name
↓
Compare with existing manuscript families
↓
Suggest existing Family ID or create new Family ID
↓
User confirms
↓
System locks future versions to that Family ID

---

## 4. ID Format

Examples:

* SRTD-001
* PHILO-001
* EPP-001
* UTCE-001
* SSO-001
* SIE-001

Version format:

* SRTD-001-V2.3.1
* SRTD-001-V2.3.1-STH
* SRTD-001-V2.3.1-RMM
* SRTD-001-V2.3.1-ANON

---

## 5. Similarity Check

The engine compares:

1. File name
2. Current title
3. Previous titles
4. Abstract
5. Keywords
6. Section headings
7. Core theoretical terms
8. DOI / OSF links
9. Submission history
10. Existing version tree

---

## 6. Decision Categories

### New Family

No strong similarity detected.

Action:

Create new Family ID.

---

### Possible Existing Family

Moderate similarity detected.

Action:

Ask user to confirm.

Example:

This manuscript may belong to SRTD-001.
Similarity: 68%
Confirm family assignment?

---

### Strong Existing Family

High similarity detected.

Action:

Recommend assigning to existing Family ID.

Example:

This manuscript appears to belong to SRTD-001.
Similarity: 91%
Suggested action: assign to existing family.

---

### Critical Conflict

Existing active submission detected.

Action:

Block new submission unless user overrides.

Example:

Critical Duplicate Risk
Family ID: SRTD-001
Active Journal: Social Theory & Health
Status: Under Review
New submission may create duplicate-submission risk.

---

## 7. Minimum Data Fields

Family:

* family_id
* short_code
* core_theme
* theory_framework
* original_title
* current_title
* alias_titles
* active_submission
* submission_lock

Version:

* version_id
* family_id
* version_number
* file_name
* created_at
* derived_from
* target_journal
* status

Submission:

* submission_record_id
* family_id
* version_id
* journal
* publisher
* submission_id
* submitted_at
* review_status
* withdrawn
* decision

---

## 8. Warning Example

Input file:

SRTD_Ver2.3.1_RMM_Anonymous.docx

System output:

Family candidate detected.

Family ID:
SRTD-001

Existing active submission:
Social Theory & Health

Status:
Under Review

Risk:
Critical duplicate submission risk

Recommended action:
Do not submit until the previous submission is withdrawn, rejected, or clarified with the editor.

---

## 9. System Position

Auto Family ID Engine belongs inside Submission Integrity Engine.

ArcText
↓
Academic Navigator
↓
Submission Integrity Engine
↓
Auto Family ID Engine
↓
ArcVault

---

## 10. One Sentence Summary

Auto Family ID Engine prevents title changes from destroying manuscript identity by assigning manuscripts to persistent internal family IDs.