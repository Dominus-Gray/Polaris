# Business Readiness Score (BRS) v2.0 Logic

## 1. Overview

The Business Readiness Score (BRS) is a composite score that measures a small business's preparedness for government contracting. BRS v2.0 introduces a more sophisticated, transparent, and accurate scoring model that accounts for different levels of verification and the relative importance of various business areas.

The score is calculated on a scale of 0-100 and is the primary KPI for clients on the Polaris platform.

## 2. Scoring Framework

The BRS is calculated as a weighted average of the scores from the 10 assessment areas. Each area's score is determined by the completion and verification status of its questions.

### 2.1. Assessment Area Weights

Each of the 10 assessment areas is assigned a weight based on its impact on overall procurement readiness.

| Area ID | Assessment Area                               | Weight |
| :------ | :-------------------------------------------- | :----- |
| area1   | Business Formation & Registration             | 15%    |
| area2   | Financial Operations & Management             | 15%    |
| area3   | Legal & Contracting Compliance                | 15%    |
| area4   | Quality Management & Standards                | 10%    |
| area5   | Technology & Security Infrastructure          | 10%    |
| area6   | Human Resources & Capacity                    | 10%    |
| area7   | Performance Tracking & Reporting              | 5%     |
| area8   | Risk Management & Business Continuity         | 5%     |
| area9   | Supply Chain Management & Vendor Relations    | 5%     |
| area10  | Competitive Advantage & Market Position       | 10%    |
| **Total** |                                               | **100%** |

### 2.2. Question Scoring Across Tiers

Each question within an assessment area contributes to that area's score. The value of each question is determined by the tier of completion. There are 3 questions per area.

*   **Max Score per Question:** 10 points
*   **Max Score per Area:** 30 points (3 questions * 10 points)

The points awarded for each question are based on the following tier completion levels:

| Tier                             | Status                             | Points Awarded | Description                                                                 |
| :------------------------------- | :--------------------------------- | :------------- | :-------------------------------------------------------------------------- |
| **Tier 1: Self-Attestation**     | `yes` (Compliant)                  | 3              | The user attests that they meet the requirement.                            |
|                                  | `no_help` (Gap Identified)         | 0              | The user indicates they do not meet the requirement.                        |
|                                  | `pending_free_resources`           | 1              | The user is addressing the gap with free resources.                         |
|                                  | `pending_professional_help`        | 1              | The user is seeking professional help for the gap.                          |
| **Tier 2: Evidence-Sufficient**  | Evidence Uploaded & Awaiting Review | 7              | The user has uploaded evidence, which is pending review by a Navigator.     |
| **Tier 3: Verified**             | Evidence Approved by Navigator     | 10             | A Navigator has reviewed and approved the evidence, verifying compliance. |
|                                  | Evidence Rejected by Navigator     | 3              | A Navigator has rejected the evidence. Score reverts to self-attestation. |

### 2.3. BRS Calculation Formula

The BRS is calculated as follows:

1.  **Calculate Area Score:** For each of the 10 areas:
    `AreaScore = (Sum of Points for all questions in the area)`

2.  **Calculate Weighted Score for each Area:**
    `WeightedAreaScore = AreaScore * AreaWeight`

3.  **Calculate Final BRS:**
    `BRS = Sum of all WeightedAreaScores / 3`

    *The division by 3 normalizes the score to a 100-point scale, since the maximum raw score is 300 (10 areas * 30 points).*

## 3. Example Calculation

Assume the following for the "Business Formation & Registration" area (Weight: 15%):

*   **Question 1.1:** Evidence Approved (Tier 3) -> 10 points
*   **Question 1.2:** Evidence Uploaded (Tier 2) -> 7 points
*   **Question 1.3:** Self-Attested 'Yes' (Tier 1) -> 3 points

1.  **Area Score (`area1`):**
    `10 + 7 + 3 = 20 points`

2.  **Weighted Score (`area1`):**
    `20 * 0.15 = 3`

This calculation is repeated for all 10 areas. The sum of the weighted scores is then divided by 3 to get the final BRS.

## 4. Implementation Notes

*   The BRS should be recalculated automatically whenever a user answers a question, uploads evidence, or a Navigator reviews evidence.
*   The frontend dashboard should display the overall BRS, as well as a breakdown of scores for each of the 10 areas.
*   The system must store the historical progression of the BRS for analytics and reporting.
*   A dedicated API endpoint (e.g., `/api/brs/calculate`) should be created to trigger BRS recalculation for a user.
