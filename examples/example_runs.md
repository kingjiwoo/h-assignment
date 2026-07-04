# 예시 실행 결과 (Example Runs)

> 생성 모드: **injected (intent 주입, 데이터는 실제 API)**
> 모든 `data`/`citations` 값은 ClinicalTrials.gov v2 API의 실제 응답에서 집계된 것입니다.
> `injected` 모드에서는 자연어→intent 해석 단계만 사람이 대체했고, 나머지 파이프라인 (쿼리 생성·API 조회·집계·차트 선택·스펙 조립)은 실제 코드가 그대로 실행했습니다.

## Time trend — 특정 약물의 연도별 시험 수

**요청:**
```json
{
  "query": "How has the number of Pembrolizumab trials changed per year since 2015?"
}
```

**응답:**
```json
{
  "visualization": {
    "type": "time_series",
    "title": "Trials over time for Pembrolizumab",
    "encoding": {
      "x": {
        "field": "year",
        "type": "temporal"
      },
      "y": {
        "field": "trial_count",
        "type": "quantitative"
      }
    },
    "data": [
      {
        "year": 2015,
        "trial_count": 13
      },
      {
        "year": 2016,
        "trial_count": 20
      },
      {
        "year": 2017,
        "trial_count": 28
      },
      {
        "year": 2018,
        "trial_count": 26
      },
      {
        "year": 2019,
        "trial_count": 36
      },
      {
        "year": 2020,
        "trial_count": 28
      },
      {
        "year": 2021,
        "trial_count": 26
      },
      {
        "year": 2022,
        "trial_count": 21
      },
      {
        "year": 2023,
        "trial_count": 26
      },
      {
        "year": 2024,
        "trial_count": 35
      },
      {
        "year": 2025,
        "trial_count": 29
      },
      {
        "year": 2026,
        "trial_count": 12
      }
    ]
  },
  "meta": {
    "filters": {},
    "analysis_type": "time_trend",
    "source": "clinicaltrials.gov",
    "study_count": 300,
    "capped": true,
    "notes": [
      "결과가 상한(MAX_STUDIES)에 걸려 최근/상위 일부 study만 집계했습니다. 수치는 전체가 아닌 표본 기준입니다."
    ]
  },
  "citations": {
    "2022": [
      {
        "nct_id": "NCT05578222",
        "excerpt": "Pembrolizumab as First-line Treatment for Advanced NSCLC Complicated With COPD"
      },
      {
        "nct_id": "NCT05383716",
        "excerpt": "Neoadjuvant/Adjuvant Pembrolizumab Plus Chemotherapy"
      },
      {
        "nct_id": "NCT05395052",
        "excerpt": "FT536 Monotherapy and in Combination With Monoclonal Antibodies in Advanced Solid Tumors"
      }
    ],
    "2020": [
      {
        "nct_id": "NCT04222972",
        "excerpt": "A Study of Pralsetinib Versus Standard of Care for First-Line Treatment of Advanced Non-Small Cell Lung Cancer (NSCLC)"
      },
      {
        "nct_id": "NCT04454528",
        "excerpt": "BreastVAX: Radiation Boost to Enhance Immune Checkpoint Blockade Therapy"
      },
      {
        "nct_id": "NCT04305054",
        "excerpt": "Substudy 02B: Safety and Efficacy of Pembrolizumab in Combination With Investigational Agents or Pembrolizumab Alone in Participants With First Line (1L) Advanced Melanoma (MK-3475-02B/KEYMAKER-U02)"
      }
    ],
    "2017": [
      {
        "nct_id": "NCT02971761",
        "excerpt": "Pembrolizumab and Enobosarm in Treating Patients With Androgen Receptor Positive Metastatic Triple Negative Breast Cancer"
      },
      {
        "nct_id": "NCT03153202",
        "excerpt": "Study to Evaluate the Safety and Preliminary Efficacy of Ibrutinib and Pembrolizumab in Patients With Chronic Lymphocytic Leukemia (CLL) or Mantle Cell Lymphoma (MCL)"
      },
      {
        "nct_id": "NCT03242915",
        "excerpt": "Pembrolizumab Plus Chemotherapy in NSCLC With Targetable Genetic Alterations After Progression on Targeted Agents"
      }
    ],
    "2018": [
      {
        "nct_id": "NCT03391973",
        "excerpt": "Pembrolizumab in Patients With Poor-Prognosis Carcinoma of Unknown Primary Site (CUP)"
      },
      {
        "nct_id": "NCT03488667",
        "excerpt": "Perioperative mFOLFOX Plus Pembrolizumab in Gastroesophageal Junction (GEJ) and Stomach Adenocarcinoma"
      },
      {
        "nct_id": "NCT03197467",
        "excerpt": "Neoadjuvant Anti PD-1 Immunotherapy in Resectable Non-small Cell Lung Cancer"
      }
    ],
    "2026": [
      {
        "nct_id": "NCT07264075",
        "excerpt": "Study Comparing Ivonescimab Alone or Ivonescimab in Combination With Ligufalimab Versus Pembrolizumab for the Treatment of SCCHN"
      },
      {
        "nct_id": "NCT07176312",
        "excerpt": "Zanidatamab in Combination With Pembrolizumab and Chemotherapy in HER2 and PD-L1 Positive Metastatic Gastroesophageal Adenocarcinoma (GEA) Patients"
      },
      {
        "nct_id": "NCT07618793",
        "excerpt": "Intermittent Hypoxic Training as Neoadjuvant Therapy for Lung Squamous Cell Carcinoma"
      }
    ],
    "2024": [
      {
        "nct_id": "NCT06197581",
        "excerpt": "Safety Assessment of Concurrent Radiotherapy and Novel Systemic Therapy for Breast Cancer"
      },
      {
        "nct_id": "NCT06178445",
        "excerpt": "Efficacy and Safety of GemCis Plus Trastuzumab Plus Pembrolizumab in Previously Untreated HER2-positive Biliary Tract Cancer"
      },
      {
        "nct_id": "NCT06400472",
        "excerpt": "A Study of LY4170156 in Participants With Selected Advanced Solid Tumors"
      }
    ],
    "2023": [
      {
        "nct_id": "NCT06052839",
        "excerpt": "Pulsed Dose Chemotherapy Plus Pembrolizumab in Recurrent/Metastatic HNSCC"
      },
      {
        "nct_id": "NCT05845814",
        "excerpt": "A Study of Efficacy and Safety of Pembrolizumab Plus Enfortumab Vedotin (EV) +/- Investigational Agents in First-Line Metastatic Urothelial Carcinoma (mUC) (MK-3475-04B/KEYMAKER-U04)"
      },
      {
        "nct_id": "NCT06083844",
        "excerpt": "Phase II Investigation of Pembrolizumab in Combination With Bevacizumab and Oral Cyclophosphamide in Patients With High Grade Ovarian Cancer and Surgically Documented Minimal Residual Disease After Frontline Therapy"
      }
    ],
    "2025": [
      {
        "nct_id": "NCT07100405",
        "excerpt": "TACE Combined With Anti-PD-1 Antibody in Patients With Advanced Hepatocellular Carcinoma: Study on Efficacy and Immune Microenvironment"
      },
      {
        "nct_id": "NCT06731478",
        "excerpt": "Study of TDXd, Chemotherapy, Pembrolizumab, and Trastuzumab in First-Line Metastatic HER2-Positive Gastric or Gastroesophageal Junction Cancer"
      },
      {
        "nct_id": "NCT06556563",
        "excerpt": "EF-41/KEYNOTE D58: Phase 3 Study of Optune Concomitant With Temozolomide Plus Pembrolizumab in Newly Diagnosed Glioblastoma"
      }
    ],
    "2021": [
      {
        "nct_id": "NCT04361851",
        "excerpt": "Study of Dara-Pembro for Multiple Myeloma Patients"
      },
      {
        "nct_id": "NCT04989322",
        "excerpt": "Pembrolizumab, Lenvatinib and Chemotherapy After TKIs in NSCLC"
      },
      {
        "nct_id": "NCT04999800",
        "excerpt": "Study of Pembrolizumab Combined With Anlotinib in the First Line Therapy for R/M HNSCC With CPS≥1"
      }
    ],
    "2019": [
      {
        "nct_id": "NCT03897881",
        "excerpt": "An Efficacy Study of Adjuvant Treatment With the Personalized Cancer Vaccine mRNA-4157 and Pembrolizumab in Participants With High-Risk Melanoma (KEYNOTE-942)"
      },
      {
        "nct_id": "NCT03776864",
        "excerpt": "Umbralisib and Pembrolizumab in Treating Patients With Relapsed or Refractory Classical Hodgkin Lymphoma"
      },
      {
        "nct_id": "NCT04083599",
        "excerpt": "GEN1042 Safety Trial and Anti-tumor Activity in Participants With Malignant Solid Tumors"
      }
    ],
    "2016": [
      {
        "nct_id": "NCT02826564",
        "excerpt": "Trial of Stereotactic Body Radiotherapy With Concurrent Pembrolizumab in Metastatic Urothelial Cancer"
      },
      {
        "nct_id": "NCT02499952",
        "excerpt": "Pembrolizumab in Subjects With Incurable Platinum-Refractory Germ Cell Tumors"
      },
      {
        "nct_id": "NCT02723955",
        "excerpt": "Dose Escalation and Expansion Study of GSK3359609 in Participants With Selected Advanced Solid Tumors (INDUCE-1)"
      }
    ],
    "2015": [
      {
        "nct_id": "NCT02370498",
        "excerpt": "A Study of Pembrolizumab (MK-3475) Versus Paclitaxel for Participants With Advanced Gastric/Gastroesophageal Junction Adenocarcinoma That Progressed After Therapy With Platinum and Fluoropyrimidine (MK-3475-061/KEYNOTE-061)"
      },
      {
        "nct_id": "NCT02559687",
        "excerpt": "Study of Pembrolizumab (MK-3475) in Previously-Treated Participants With Advanced Carcinoma of the Esophagus or Esophagogastric Junction (MK-3475-180/KEYNOTE-180)"
      },
      {
        "nct_id": "NCT02414269",
        "excerpt": "Malignant Pleural Disease Treated With Autologous T Cells Genetically Engineered to Target the Cancer-Cell Surface Antigen Mesothelin"
      }
    ]
  }
}
```

## Distribution — 질환의 phase별 분포

**요청:**
```json
{
  "query": "How are diabetes trials distributed across phases?",
  "condition": "diabetes"
}
```

**응답:**
```json
{
  "visualization": {
    "type": "bar_chart",
    "title": "Trial distribution by phase for diabetes",
    "encoding": {
      "x": {
        "field": "category",
        "type": "nominal"
      },
      "y": {
        "field": "trial_count",
        "type": "quantitative"
      }
    },
    "data": [
      {
        "category": "EARLY_PHASE1",
        "trial_count": 1
      },
      {
        "category": "PHASE1",
        "trial_count": 28
      },
      {
        "category": "PHASE2",
        "trial_count": 35
      },
      {
        "category": "PHASE3",
        "trial_count": 34
      },
      {
        "category": "PHASE4",
        "trial_count": 31
      },
      {
        "category": "NA",
        "trial_count": 180
      }
    ]
  },
  "meta": {
    "filters": {
      "condition": "diabetes"
    },
    "analysis_type": "distribution",
    "source": "clinicaltrials.gov",
    "study_count": 300,
    "capped": true,
    "notes": [
      "결과가 상한(MAX_STUDIES)에 걸려 최근/상위 일부 study만 집계했습니다. 수치는 전체가 아닌 표본 기준입니다."
    ]
  },
  "citations": {
    "PHASE4": [
      {
        "nct_id": "NCT03470961",
        "excerpt": "Observational Study to Evaluate the Safety and Efficacy of Polyclonal Antibodies in Simultaneous Pancreas Kidney Transplant Recipients"
      },
      {
        "nct_id": "NCT04200586",
        "excerpt": "The Effects of SGLTi on Diabetic Cardiomyopathy"
      },
      {
        "nct_id": "NCT02079805",
        "excerpt": "A Study to Explore the Effects of Azilsartan Compared to Telmisartan on Insulin Resistance of Patients With Essential Hypertension on Type 2 Diabetes Mellitus by HOMA-R"
      }
    ],
    "NA": [
      {
        "nct_id": "NCT04838561",
        "excerpt": "Assessing the Impact of Control-IQ Technology"
      },
      {
        "nct_id": "NCT07255170",
        "excerpt": "RED BEAN AND TOMATO SNACK BAR FORMULATIONS AS A HEALTHY SNACK FOR DIABETES MELLITUS PATIENTS"
      },
      {
        "nct_id": "NCT06054841",
        "excerpt": "Reshaping Postpartum Follow-up"
      }
    ],
    "PHASE2": [
      {
        "nct_id": "NCT02762370",
        "excerpt": "Study to Assess the Effects of FX006 on Blood Glucose in Patients With OA of the Knee and Type 2 Diabetes"
      },
      {
        "nct_id": "NCT00878605",
        "excerpt": "Development of A Novel Anti-Hyperglycemic Agent"
      },
      {
        "nct_id": "NCT01098357",
        "excerpt": "Comparative Study of 3 Dose Regimens of BioChaperone to Becaplermin Gel for the Treatment of Diabetic Foot Ulcer"
      }
    ],
    "PHASE1": [
      {
        "nct_id": "NCT01319331",
        "excerpt": "The Effects of Alpha-1 Antitrypsin (AAT) on the Progression of Type 1 Diabetes"
      },
      {
        "nct_id": "NCT02058641",
        "excerpt": "Effect of Darapladib on Cantharidin-Induced Inflammatory Blisters in Subjects With Type 2 Diabetes Mellitus (T2DM)"
      },
      {
        "nct_id": "NCT00453375",
        "excerpt": "Phase 1 Study of BHT-3021 in Subjects With Type 1 Diabetes Mellitus"
      }
    ],
    "PHASE3": [
      {
        "nct_id": "NCT02324569",
        "excerpt": "A Phase 4, Randomized, Double-blind, Parallel-group, Comparative Study and a Phase 4, Open-label, Long-term Study of SYR-472 (100 mg) in Combination With Insulin in Patients With Type 2 Diabetes"
      },
      {
        "nct_id": "NCT02516657",
        "excerpt": "Liraglutide in Adolescents With Type 1 Diabetes"
      },
      {
        "nct_id": "NCT00449930",
        "excerpt": "Sitagliptin Comparative Study in Patients With Type 2 Diabetes (0431-049)"
      }
    ],
    "EARLY_PHASE1": [
      {
        "nct_id": "NCT07528105",
        "excerpt": "Allogeneic Anti-CD7 CAR-T for Type 1 Diabetes"
      }
    ]
  }
}
```

## Comparison — 두 약물의 phase 비교

**요청:**
```json
{
  "query": "Compare trial phases for Pembrolizumab vs Nivolumab."
}
```

**응답:**
```json
{
  "visualization": {
    "type": "grouped_bar_chart",
    "title": "Comparison of trials: Clinical trials",
    "encoding": {
      "x": {
        "field": "category",
        "type": "nominal"
      },
      "y": {
        "field": "<group>",
        "type": "quantitative"
      },
      "series": [
        "Pembrolizumab",
        "Nivolumab"
      ]
    },
    "data": [
      {
        "category": "EARLY_PHASE1",
        "Pembrolizumab": 1,
        "Nivolumab": 4
      },
      {
        "category": "PHASE1",
        "Pembrolizumab": 48,
        "Nivolumab": 50
      },
      {
        "category": "PHASE2",
        "Pembrolizumab": 94,
        "Nivolumab": 87
      },
      {
        "category": "PHASE3",
        "Pembrolizumab": 21,
        "Nivolumab": 13
      },
      {
        "category": "PHASE4",
        "Pembrolizumab": 1,
        "Nivolumab": 0
      },
      {
        "category": "NA",
        "Pembrolizumab": 13,
        "Nivolumab": 21
      }
    ]
  },
  "meta": {
    "filters": {},
    "analysis_type": "comparison",
    "source": "clinicaltrials.gov",
    "study_count": 300,
    "capped": true,
    "notes": [
      "결과가 상한(MAX_STUDIES)에 걸려 최근/상위 일부 study만 집계했습니다. 수치는 전체가 아닌 표본 기준입니다."
    ]
  },
  "citations": {
    "Pembrolizumab|EARLY_PHASE1": [
      {
        "nct_id": "NCT06366451",
        "excerpt": "PBI-MST-01 (NCT04541108) Substudy AZN-05: Intratumoral Microdosing of Rilvegostomig, Volrustomig, Sabestomig, and AZD9592 in HNSCC"
      }
    ],
    "Nivolumab|EARLY_PHASE1": [
      {
        "nct_id": "NCT05704933",
        "excerpt": "Pilot Study of Nivolumab w/Ipilimumab or Relatlimab in Surgically Resectable Melanoma Brain Metastases"
      },
      {
        "nct_id": "NCT04570683",
        "excerpt": "Laser Immunotherapy With and Without Topical Anti-PD1 in Basal Cell Carcinomas"
      },
      {
        "nct_id": "NCT06204614",
        "excerpt": "Drug Screening Using IMD in Bladder Cancer"
      }
    ],
    "Pembrolizumab|PHASE1": [
      {
        "nct_id": "NCT04454528",
        "excerpt": "BreastVAX: Radiation Boost to Enhance Immune Checkpoint Blockade Therapy"
      },
      {
        "nct_id": "NCT04305054",
        "excerpt": "Substudy 02B: Safety and Efficacy of Pembrolizumab in Combination With Investigational Agents or Pembrolizumab Alone in Participants With First Line (1L) Advanced Melanoma (MK-3475-02B/KEYMAKER-U02)"
      },
      {
        "nct_id": "NCT03153202",
        "excerpt": "Study to Evaluate the Safety and Preliminary Efficacy of Ibrutinib and Pembrolizumab in Patients With Chronic Lymphocytic Leukemia (CLL) or Mantle Cell Lymphoma (MCL)"
      }
    ],
    "Nivolumab|PHASE1": [
      {
        "nct_id": "NCT01024231",
        "excerpt": "Dose-escalation Study of Combination BMS-936558 (MDX-1106) and Ipilimumab in Subjects With Unresectable Stage III or Stage IV Malignant Melanoma"
      },
      {
        "nct_id": "NCT03371381",
        "excerpt": "An Efficacy and Safety Study of JNJ-64041757, a Live Attenuated Listeria Monocytogenes Immunotherapy, in Combination With Nivolumab Versus Nivolumab Monotherapy in Participants With Advanced Adenocarcinoma of the Lung"
      },
      {
        "nct_id": "NCT03167177",
        "excerpt": "QUILT-3.046: NANT Melanoma Vaccine: Combination Immunotherapy in Subjects With Melanoma Who Have Progressed On or After Chemotherapy and PD-1/PD-L1 Therapy"
      }
    ],
    "Pembrolizumab|PHASE2": [
      {
        "nct_id": "NCT05578222",
        "excerpt": "Pembrolizumab as First-line Treatment for Advanced NSCLC Complicated With COPD"
      },
      {
        "nct_id": "NCT04454528",
        "excerpt": "BreastVAX: Radiation Boost to Enhance Immune Checkpoint Blockade Therapy"
      },
      {
        "nct_id": "NCT02971761",
        "excerpt": "Pembrolizumab and Enobosarm in Treating Patients With Androgen Receptor Positive Metastatic Triple Negative Breast Cancer"
      }
    ],
    "Nivolumab|PHASE2": [
      {
        "nct_id": "NCT06715241",
        "excerpt": "A MULTICENTER, SEEKING SIGNAL, RANDOMISED, OPEN-LABEL PHASE II OF RELATLIMAB AND NIVOLUMAB VS NIVOLUMAB ALONE IN LOCALLY ADVANCED CERVICAL CANCERS"
      },
      {
        "nct_id": "NCT03631641",
        "excerpt": "Nivolumab in Preventing Colon Adenomas in Participants With Lynch Syndrome and a History of Partial Colectomy"
      },
      {
        "nct_id": "NCT03991130",
        "excerpt": "High Dose IL-2 in Combination With Anti-PD-1 to Overcome Anti-PD-1 Resistance in Metastatic Melanoma and Renal Cell Carcinoma"
      }
    ],
    "Pembrolizumab|PHASE3": [
      {
        "nct_id": "NCT04222972",
        "excerpt": "A Study of Pralsetinib Versus Standard of Care for First-Line Treatment of Advanced Non-Small Cell Lung Cancer (NSCLC)"
      },
      {
        "nct_id": "NCT07264075",
        "excerpt": "Study Comparing Ivonescimab Alone or Ivonescimab in Combination With Ligufalimab Versus Pembrolizumab for the Treatment of SCCHN"
      },
      {
        "nct_id": "NCT06731478",
        "excerpt": "Study of TDXd, Chemotherapy, Pembrolizumab, and Trastuzumab in First-Line Metastatic HER2-Positive Gastric or Gastroesophageal Junction Cancer"
      }
    ],
    "Nivolumab|PHASE3": [
      {
        "nct_id": "NCT02538666",
        "excerpt": "An Investigational Immuno-therapy Study of Nivolumab, or Nivolumab in Combination With Ipilimumab, or Placebo in Patients With Extensive-Stage Disease Small Cell Lung Cancer (ED-SCLC) After Completion of Platinum-based Chemotherapy"
      },
      {
        "nct_id": "NCT04026412",
        "excerpt": "A Study of Nivolumab and Ipilimumab in Untreated Participants With Stage 3 Non-small Cell Lung Cancer (NSCLC) That is Unable or Not Planned to be Removed by Surgery"
      },
      {
        "nct_id": "NCT07431281",
        "excerpt": "Sonesitatug Vedotin in Combination With Capecitabine With or Without Rilvegostomig in Participants With Advanced or Metastatic Gastric, Gastroesophageal Junction, or Esophageal Adenocarcinoma Expressing Claudin18.2"
      }
    ],
    "Pembrolizumab|PHASE4": [
      {
        "nct_id": "NCT03891979",
        "excerpt": "Gut Microbiome Modulation to Enable Efficacy of Checkpoint-based Immunotherapy in Pancreatic Adenocarcinoma"
      }
    ],
    "Pembrolizumab|NA": [
      {
        "nct_id": "NCT06197581",
        "excerpt": "Safety Assessment of Concurrent Radiotherapy and Novel Systemic Therapy for Breast Cancer"
      },
      {
        "nct_id": "NCT07100405",
        "excerpt": "TACE Combined With Anti-PD-1 Antibody in Patients With Advanced Hepatocellular Carcinoma: Study on Efficacy and Immune Microenvironment"
      },
      {
        "nct_id": "NCT07420855",
        "excerpt": "International Multicentric Retrospective Study on the Use of EV+P as First-line Therapy in Patients With la/mUC"
      }
    ],
    "Nivolumab|NA": [
      {
        "nct_id": "NCT07100405",
        "excerpt": "TACE Combined With Anti-PD-1 Antibody in Patients With Advanced Hepatocellular Carcinoma: Study on Efficacy and Immune Microenvironment"
      },
      {
        "nct_id": "NCT04146064",
        "excerpt": "Breathomics as Predictive Biomarker for Checkpoint Inhibitor Response"
      },
      {
        "nct_id": "NCT04490564",
        "excerpt": "Validation of Molecular Diagnostic Assays to Detect Cancer Biomarkers in Blood and Primary Tumor in HNSCC/NSCLC/Melanoma"
      }
    ]
  }
}
```

## Geographic — 국가별 모집중 시험 수

**요청:**
```json
{
  "query": "Which countries have the most recruiting trials for breast cancer?",
  "condition": "breast cancer"
}
```

**응답:**
```json
{
  "visualization": {
    "type": "bar_chart",
    "title": "Trials by country for breast cancer",
    "encoding": {
      "x": {
        "field": "country",
        "type": "nominal"
      },
      "y": {
        "field": "trial_count",
        "type": "quantitative"
      }
    },
    "data": [
      {
        "country": "United States",
        "trial_count": 123
      },
      {
        "country": "China",
        "trial_count": 68
      },
      {
        "country": "Italy",
        "trial_count": 26
      },
      {
        "country": "Spain",
        "trial_count": 23
      },
      {
        "country": "Netherlands",
        "trial_count": 20
      },
      {
        "country": "France",
        "trial_count": 19
      },
      {
        "country": "Germany",
        "trial_count": 15
      },
      {
        "country": "Belgium",
        "trial_count": 14
      },
      {
        "country": "South Korea",
        "trial_count": 13
      },
      {
        "country": "Canada",
        "trial_count": 11
      },
      {
        "country": "Australia",
        "trial_count": 9
      },
      {
        "country": "Turkey (Türkiye)",
        "trial_count": 8
      },
      {
        "country": "Brazil",
        "trial_count": 7
      },
      {
        "country": "Singapore",
        "trial_count": 6
      },
      {
        "country": "Japan",
        "trial_count": 5
      },
      {
        "country": "Taiwan",
        "trial_count": 5
      },
      {
        "country": "United Kingdom",
        "trial_count": 5
      },
      {
        "country": "Egypt",
        "trial_count": 5
      },
      {
        "country": "Austria",
        "trial_count": 4
      },
      {
        "country": "Israel",
        "trial_count": 4
      },
      {
        "country": "Poland",
        "trial_count": 4
      },
      {
        "country": "Portugal",
        "trial_count": 4
      },
      {
        "country": "Ireland",
        "trial_count": 3
      },
      {
        "country": "Argentina",
        "trial_count": 3
      },
      {
        "country": "Chile",
        "trial_count": 3
      }
    ]
  },
  "meta": {
    "filters": {
      "condition": "breast cancer"
    },
    "analysis_type": "geo",
    "source": "clinicaltrials.gov",
    "study_count": 300,
    "capped": true,
    "notes": [
      "국가 57개 중 상위 25개만 표시합니다.",
      "결과가 상한(MAX_STUDIES)에 걸려 최근/상위 일부 study만 집계했습니다. 수치는 전체가 아닌 표본 기준입니다."
    ]
  },
  "citations": {
    "United States": [
      {
        "nct_id": "NCT06892275",
        "excerpt": "The FYI on MRI: A Multilevel Decision Support Intervention for Screening Breast MRI"
      },
      {
        "nct_id": "NCT03954431",
        "excerpt": "High-Resolution Lower Dose Dedicated Breast Computed Tomography (CT)"
      },
      {
        "nct_id": "NCT06400472",
        "excerpt": "A Study of LY4170156 in Participants With Selected Advanced Solid Tumors"
      }
    ],
    "China": [
      {
        "nct_id": "NCT06197581",
        "excerpt": "Safety Assessment of Concurrent Radiotherapy and Novel Systemic Therapy for Breast Cancer"
      },
      {
        "nct_id": "NCT07335081",
        "excerpt": "ctDNA in HER2+ EBC Neoadjuvant Treatment"
      },
      {
        "nct_id": "NCT06992336",
        "excerpt": "Circulating Tumor DNA Guided Boost Therapy in Early Triple Negative Breast Patients With Residual Disease After Neoadjuvant Therapy"
      }
    ],
    "Italy": [
      {
        "nct_id": "NCT06400472",
        "excerpt": "A Study of LY4170156 in Participants With Selected Advanced Solid Tumors"
      },
      {
        "nct_id": "NCT05057598",
        "excerpt": "DianaWeb: Before and After Study Online Based Participatory Research on Breast Cancer Women"
      },
      {
        "nct_id": "NCT06065748",
        "excerpt": "A Study to Evaluate Efficacy and Safety of Giredestrant Compared With Fulvestrant (Plus a CDK4/6 Inhibitor), in Participants With ER-Positive, HER2-Negative Advanced Breast Cancer Resistant to Adjuvant Endocrine Therapy (pionERA Breast Cancer)"
      }
    ],
    "Spain": [
      {
        "nct_id": "NCT06400472",
        "excerpt": "A Study of LY4170156 in Participants With Selected Advanced Solid Tumors"
      },
      {
        "nct_id": "NCT06638307",
        "excerpt": "A First-in-Human Study of MEN2312 in Adults With Advanced Breast Cancer"
      },
      {
        "nct_id": "NCT06065748",
        "excerpt": "A Study to Evaluate Efficacy and Safety of Giredestrant Compared With Fulvestrant (Plus a CDK4/6 Inhibitor), in Participants With ER-Positive, HER2-Negative Advanced Breast Cancer Resistant to Adjuvant Endocrine Therapy (pionERA Breast Cancer)"
      }
    ],
    "Netherlands": [
      {
        "nct_id": "NCT07511933",
        "excerpt": "Novel Ga68-PSMA PET/CT-tracer to Differentiate Between Radiation Necrosis and Tumor Progression in Brain Metastases"
      },
      {
        "nct_id": "NCT07310758",
        "excerpt": "Contrast-enhanced Ultrasound for Sentinel Node Detection"
      },
      {
        "nct_id": "NCT06266312",
        "excerpt": "Feasibility of a Preoperative, Multimodal Lifestyle Intervention in Patients With Breastcancer"
      }
    ],
    "France": [
      {
        "nct_id": "NCT06400472",
        "excerpt": "A Study of LY4170156 in Participants With Selected Advanced Solid Tumors"
      },
      {
        "nct_id": "NCT06065748",
        "excerpt": "A Study to Evaluate Efficacy and Safety of Giredestrant Compared With Fulvestrant (Plus a CDK4/6 Inhibitor), in Participants With ER-Positive, HER2-Negative Advanced Breast Cancer Resistant to Adjuvant Endocrine Therapy (pionERA Breast Cancer)"
      },
      {
        "nct_id": "NCT03017573",
        "excerpt": "Prospective Biobanking Study in Cancer Patients Aiming at Better Understand the Link Between the Molecular Alterations of the Tumor Itself, Its Microenvironment and Immune Response (SCANDARE)"
      }
    ],
    "Germany": [
      {
        "nct_id": "NCT06065748",
        "excerpt": "A Study to Evaluate Efficacy and Safety of Giredestrant Compared With Fulvestrant (Plus a CDK4/6 Inhibitor), in Participants With ER-Positive, HER2-Negative Advanced Breast Cancer Resistant to Adjuvant Endocrine Therapy (pionERA Breast Cancer)"
      },
      {
        "nct_id": "NCT04172753",
        "excerpt": "Feasibility of Online MR-guided Radiotherapy on a 1.5T MR-Linac"
      },
      {
        "nct_id": "NCT06830720",
        "excerpt": "A Non-interventional Study for Kisqali (Ribociclib) in Combination With an Aromatase Inhibitor for Adjuvant Treatment in Patients With HR+/HER2- Early Breast Cancer at High Risk of Recurrence"
      }
    ],
    "Belgium": [
      {
        "nct_id": "NCT06835426",
        "excerpt": "High-resolution PET-CT Specimen Imaging for the Perioperative Visualization of Resection Margins"
      },
      {
        "nct_id": "NCT06065748",
        "excerpt": "A Study to Evaluate Efficacy and Safety of Giredestrant Compared With Fulvestrant (Plus a CDK4/6 Inhibitor), in Participants With ER-Positive, HER2-Negative Advanced Breast Cancer Resistant to Adjuvant Endocrine Therapy (pionERA Breast Cancer)"
      },
      {
        "nct_id": "NCT05950945",
        "excerpt": "Trastuzumab Deruxtecan (T-DXd) in Patients Who Have Hormone Receptor-negative and Hormone Receptor-positive HER2-low or HER2 IHC 0 Metastatic Breast Cancer"
      }
    ],
    "South Korea": [
      {
        "nct_id": "NCT07525869",
        "excerpt": "An Open-label Prospective Study to Evaluate the Efficacy and Safety of Pegfilgrastim in Triple-Negative Breast Cancer Patients Receiving AC Regimen Following Paclitaxel and Carboplatin as Neoadjuvant Therapy"
      },
      {
        "nct_id": "NCT06400472",
        "excerpt": "A Study of LY4170156 in Participants With Selected Advanced Solid Tumors"
      },
      {
        "nct_id": "NCT06065748",
        "excerpt": "A Study to Evaluate Efficacy and Safety of Giredestrant Compared With Fulvestrant (Plus a CDK4/6 Inhibitor), in Participants With ER-Positive, HER2-Negative Advanced Breast Cancer Resistant to Adjuvant Endocrine Therapy (pionERA Breast Cancer)"
      }
    ],
    "Canada": [
      {
        "nct_id": "NCT04671511",
        "excerpt": "Targeted Axillary Dissection (TAD) in Early-stage Node Positive Breast Cancer"
      },
      {
        "nct_id": "NCT06065748",
        "excerpt": "A Study to Evaluate Efficacy and Safety of Giredestrant Compared With Fulvestrant (Plus a CDK4/6 Inhibitor), in Participants With ER-Positive, HER2-Negative Advanced Breast Cancer Resistant to Adjuvant Endocrine Therapy (pionERA Breast Cancer)"
      },
      {
        "nct_id": "NCT06982521",
        "excerpt": "Phase 3 Study of RLY-2608 + Fulvestrant vs Capivasertib + Fulvestrant as Treatment for Locally Advanced or Metastatic PIK3CA-mutant HR+/HER2- Breast Cancer"
      }
    ],
    "Australia": [
      {
        "nct_id": "NCT06400472",
        "excerpt": "A Study of LY4170156 in Participants With Selected Advanced Solid Tumors"
      },
      {
        "nct_id": "NCT06065748",
        "excerpt": "A Study to Evaluate Efficacy and Safety of Giredestrant Compared With Fulvestrant (Plus a CDK4/6 Inhibitor), in Participants With ER-Positive, HER2-Negative Advanced Breast Cancer Resistant to Adjuvant Endocrine Therapy (pionERA Breast Cancer)"
      },
      {
        "nct_id": "NCT07358377",
        "excerpt": "A Trial of HRS-6209-205 to Evaluate the Safety, Tolerability, Pharmacokinetics and Efficacy of HRS-6209 in Combination Therapy in Subjects With HR-Positive/HER2-Negative Cancer"
      }
    ],
    "Turkey (Türkiye)": [
      {
        "nct_id": "NCT05386628",
        "excerpt": "The Effect of Myofascial Chain Release Techniques on Shoulder Joint Range of Motion in Breast Cancer Survivors"
      },
      {
        "nct_id": "NCT07670221",
        "excerpt": "Nurse-Led Self-Management Program on Taste Alteration in Women With Breast Cancer"
      },
      {
        "nct_id": "NCT06065748",
        "excerpt": "A Study to Evaluate Efficacy and Safety of Giredestrant Compared With Fulvestrant (Plus a CDK4/6 Inhibitor), in Participants With ER-Positive, HER2-Negative Advanced Breast Cancer Resistant to Adjuvant Endocrine Therapy (pionERA Breast Cancer)"
      }
    ],
    "Brazil": [
      {
        "nct_id": "NCT06065748",
        "excerpt": "A Study to Evaluate Efficacy and Safety of Giredestrant Compared With Fulvestrant (Plus a CDK4/6 Inhibitor), in Participants With ER-Positive, HER2-Negative Advanced Breast Cancer Resistant to Adjuvant Endocrine Therapy (pionERA Breast Cancer)"
      },
      {
        "nct_id": "NCT05950945",
        "excerpt": "Trastuzumab Deruxtecan (T-DXd) in Patients Who Have Hormone Receptor-negative and Hormone Receptor-positive HER2-low or HER2 IHC 0 Metastatic Breast Cancer"
      },
      {
        "nct_id": "NCT06982521",
        "excerpt": "Phase 3 Study of RLY-2608 + Fulvestrant vs Capivasertib + Fulvestrant as Treatment for Locally Advanced or Metastatic PIK3CA-mutant HR+/HER2- Breast Cancer"
      }
    ],
    "Singapore": [
      {
        "nct_id": "NCT06065748",
        "excerpt": "A Study to Evaluate Efficacy and Safety of Giredestrant Compared With Fulvestrant (Plus a CDK4/6 Inhibitor), in Participants With ER-Positive, HER2-Negative Advanced Breast Cancer Resistant to Adjuvant Endocrine Therapy (pionERA Breast Cancer)"
      },
      {
        "nct_id": "NCT06977360",
        "excerpt": "Feasibility, Acceptability and Preliminary Efficacy of the New Iteration of the Innovative Smartphone-based Care Solution for Women With Breast Cancer Undergoing Chemotherapy (iCareBreast+): A Pilot Study Research Proposal"
      },
      {
        "nct_id": "NCT06982521",
        "excerpt": "Phase 3 Study of RLY-2608 + Fulvestrant vs Capivasertib + Fulvestrant as Treatment for Locally Advanced or Metastatic PIK3CA-mutant HR+/HER2- Breast Cancer"
      }
    ],
    "Japan": [
      {
        "nct_id": "NCT06400472",
        "excerpt": "A Study of LY4170156 in Participants With Selected Advanced Solid Tumors"
      },
      {
        "nct_id": "NCT06526819",
        "excerpt": "SMP-3124LP in Adults With Advanced Solid Tumors"
      },
      {
        "nct_id": "NCT06330064",
        "excerpt": "A Study To Evaluate The Efficacy And Safety Of Ifinatamab Deruxtecan (I-DXd) In Subjects With Recurrent Or Metastatic Solid Tumors (IDeate-PanTumor02)"
      }
    ],
    "Taiwan": [
      {
        "nct_id": "NCT06065748",
        "excerpt": "A Study to Evaluate Efficacy and Safety of Giredestrant Compared With Fulvestrant (Plus a CDK4/6 Inhibitor), in Participants With ER-Positive, HER2-Negative Advanced Breast Cancer Resistant to Adjuvant Endocrine Therapy (pionERA Breast Cancer)"
      },
      {
        "nct_id": "NCT06982521",
        "excerpt": "Phase 3 Study of RLY-2608 + Fulvestrant vs Capivasertib + Fulvestrant as Treatment for Locally Advanced or Metastatic PIK3CA-mutant HR+/HER2- Breast Cancer"
      },
      {
        "nct_id": "NCT06797635",
        "excerpt": "Study of Patritumab Deruxtecan Plus Pembrolizumab With Other Anticancer Agents in Participants With High-Risk Early-Stage Triple-Negative or Hormone Receptor-Low Positive/HER-2 Negative Breast Cancer (MK-1022-010, HERTHENA-Breast-03)"
      }
    ],
    "United Kingdom": [
      {
        "nct_id": "NCT05329532",
        "excerpt": "Modi-1 Moditope in Breast, Head and Neck, Ovarian, or Renal Cancer"
      },
      {
        "nct_id": "NCT04985266",
        "excerpt": "A Trial of Early Detection of Molecular Relapse With Circulating Tumour DNA Tracking and Treatment With Palbociclib Plus Fulvestrant Versus Standard Endocrine Therapy in Patients With ER Positive HER2 Negative Breast Cancer"
      },
      {
        "nct_id": "NCT05573126",
        "excerpt": "Phase 1/2 Study to Evaluate EP0062 as Monotherapy and in Combination in Patients With Advanced or Metastatic AR+/HER-2-/ER+ Breast Cancer"
      }
    ],
    "Egypt": [
      {
        "nct_id": "NCT06548646",
        "excerpt": "Ultrasound-guided Thoracic Interfascial Plane Nerve Block Versus Erector Spinae Plane Block for Pain Control After Modified Radical Mastectomy"
      },
      {
        "nct_id": "NCT06947330",
        "excerpt": "Comparison Between Erector Spinae Plane Block Versus Serratus Anterior Plane Block Regarding Analgesia Post Modified Radical Mastectomy"
      },
      {
        "nct_id": "NCT07390448",
        "excerpt": "Rhomboid Intercostal Sub-serratus Plane Blocks and Erector Spinae Plane Block in Mastectomy Surgeries"
      }
    ],
    "Austria": [
      {
        "nct_id": "NCT06065748",
        "excerpt": "A Study to Evaluate Efficacy and Safety of Giredestrant Compared With Fulvestrant (Plus a CDK4/6 Inhibitor), in Participants With ER-Positive, HER2-Negative Advanced Breast Cancer Resistant to Adjuvant Endocrine Therapy (pionERA Breast Cancer)"
      },
      {
        "nct_id": "NCT06830720",
        "excerpt": "A Non-interventional Study for Kisqali (Ribociclib) in Combination With an Aromatase Inhibitor for Adjuvant Treatment in Patients With HR+/HER2- Early Breast Cancer at High Risk of Recurrence"
      },
      {
        "nct_id": "NCT06982521",
        "excerpt": "Phase 3 Study of RLY-2608 + Fulvestrant vs Capivasertib + Fulvestrant as Treatment for Locally Advanced or Metastatic PIK3CA-mutant HR+/HER2- Breast Cancer"
      }
    ],
    "Israel": [
      {
        "nct_id": "NCT06065748",
        "excerpt": "A Study to Evaluate Efficacy and Safety of Giredestrant Compared With Fulvestrant (Plus a CDK4/6 Inhibitor), in Participants With ER-Positive, HER2-Negative Advanced Breast Cancer Resistant to Adjuvant Endocrine Therapy (pionERA Breast Cancer)"
      },
      {
        "nct_id": "NCT05753657",
        "excerpt": "A Pilot Study of Monitoring Insulin Levels and Treating Hyperinsulinemia and Hyperglycemia With Pioglitazone in Patients Treated With Alpelisib for Metastatic Breast Cancer."
      },
      {
        "nct_id": "NCT03463954",
        "excerpt": "Confirmatory Clinical Evaluation of Novilase® Laser Therapy for Focal Destruction of Malignant Breast Tumors"
      }
    ],
    "Poland": [
      {
        "nct_id": "NCT06065748",
        "excerpt": "A Study to Evaluate Efficacy and Safety of Giredestrant Compared With Fulvestrant (Plus a CDK4/6 Inhibitor), in Participants With ER-Positive, HER2-Negative Advanced Breast Cancer Resistant to Adjuvant Endocrine Therapy (pionERA Breast Cancer)"
      },
      {
        "nct_id": "NCT06982521",
        "excerpt": "Phase 3 Study of RLY-2608 + Fulvestrant vs Capivasertib + Fulvestrant as Treatment for Locally Advanced or Metastatic PIK3CA-mutant HR+/HER2- Breast Cancer"
      },
      {
        "nct_id": "NCT06330064",
        "excerpt": "A Study To Evaluate The Efficacy And Safety Of Ifinatamab Deruxtecan (I-DXd) In Subjects With Recurrent Or Metastatic Solid Tumors (IDeate-PanTumor02)"
      }
    ],
    "Portugal": [
      {
        "nct_id": "NCT06065748",
        "excerpt": "A Study to Evaluate Efficacy and Safety of Giredestrant Compared With Fulvestrant (Plus a CDK4/6 Inhibitor), in Participants With ER-Positive, HER2-Negative Advanced Breast Cancer Resistant to Adjuvant Endocrine Therapy (pionERA Breast Cancer)"
      },
      {
        "nct_id": "NCT05950945",
        "excerpt": "Trastuzumab Deruxtecan (T-DXd) in Patients Who Have Hormone Receptor-negative and Hormone Receptor-positive HER2-low or HER2 IHC 0 Metastatic Breast Cancer"
      },
      {
        "nct_id": "NCT06982521",
        "excerpt": "Phase 3 Study of RLY-2608 + Fulvestrant vs Capivasertib + Fulvestrant as Treatment for Locally Advanced or Metastatic PIK3CA-mutant HR+/HER2- Breast Cancer"
      }
    ],
    "Ireland": [
      {
        "nct_id": "NCT07672392",
        "excerpt": "The Effect of a Post-operative Exercise Programme Versus Standard Care on Physical Fitness of Patients With Breast Cancer Undergoing Deep Inferior Epigastric Perforator (DIEP) Flap Reconstruction Surgery"
      },
      {
        "nct_id": "NCT05950945",
        "excerpt": "Trastuzumab Deruxtecan (T-DXd) in Patients Who Have Hormone Receptor-negative and Hormone Receptor-positive HER2-low or HER2 IHC 0 Metastatic Breast Cancer"
      },
      {
        "nct_id": "NCT06330064",
        "excerpt": "A Study To Evaluate The Efficacy And Safety Of Ifinatamab Deruxtecan (I-DXd) In Subjects With Recurrent Or Metastatic Solid Tumors (IDeate-PanTumor02)"
      }
    ],
    "Argentina": [
      {
        "nct_id": "NCT06065748",
        "excerpt": "A Study to Evaluate Efficacy and Safety of Giredestrant Compared With Fulvestrant (Plus a CDK4/6 Inhibitor), in Participants With ER-Positive, HER2-Negative Advanced Breast Cancer Resistant to Adjuvant Endocrine Therapy (pionERA Breast Cancer)"
      },
      {
        "nct_id": "NCT06982521",
        "excerpt": "Phase 3 Study of RLY-2608 + Fulvestrant vs Capivasertib + Fulvestrant as Treatment for Locally Advanced or Metastatic PIK3CA-mutant HR+/HER2- Breast Cancer"
      },
      {
        "nct_id": "NCT06330064",
        "excerpt": "A Study To Evaluate The Efficacy And Safety Of Ifinatamab Deruxtecan (I-DXd) In Subjects With Recurrent Or Metastatic Solid Tumors (IDeate-PanTumor02)"
      }
    ],
    "Chile": [
      {
        "nct_id": "NCT06065748",
        "excerpt": "A Study to Evaluate Efficacy and Safety of Giredestrant Compared With Fulvestrant (Plus a CDK4/6 Inhibitor), in Participants With ER-Positive, HER2-Negative Advanced Breast Cancer Resistant to Adjuvant Endocrine Therapy (pionERA Breast Cancer)"
      },
      {
        "nct_id": "NCT05447988",
        "excerpt": "Motiva Flora Tissue Expander PMCF"
      },
      {
        "nct_id": "NCT06330064",
        "excerpt": "A Study To Evaluate The Efficacy And Safety Of Ifinatamab Deruxtecan (I-DXd) In Subjects With Recurrent Or Metastatic Solid Tumors (IDeate-PanTumor02)"
      }
    ]
  }
}
```

## Network — 질환의 sponsor↔drug 관계망

**요청:**
```json
{
  "query": "Show a network of sponsors and drugs for melanoma trials.",
  "condition": "melanoma"
}
```

**응답:**
```json
{
  "visualization": {
    "type": "network_graph",
    "title": "Sponsor–drug network for melanoma",
    "encoding": {
      "nodes": {
        "id": "id",
        "group": "kind",
        "size": "degree"
      },
      "edges": {
        "source": "source",
        "target": "target",
        "weight": "weight"
      }
    },
    "data": {
      "nodes": [
        {
          "id": "National Cancer Institute (NCI)",
          "kind": "sponsor",
          "degree": 21
        },
        {
          "id": "ImmunityBio, Inc.",
          "kind": "sponsor",
          "degree": 17
        },
        {
          "id": "Merck Sharp & Dohme LLC",
          "kind": "sponsor",
          "degree": 9
        },
        {
          "id": "Cyclophosphamide",
          "kind": "drug",
          "degree": 6
        },
        {
          "id": "Fred Hutchinson Cancer Center",
          "kind": "sponsor",
          "degree": 5
        },
        {
          "id": "Bristol-Myers Squibb",
          "kind": "sponsor",
          "degree": 4
        },
        {
          "id": "City of Hope Medical Center",
          "kind": "sponsor",
          "degree": 4
        },
        {
          "id": "Aldesleukin",
          "kind": "drug",
          "degree": 3
        },
        {
          "id": "therapeutic autologous lymphocytes",
          "kind": "drug",
          "degree": 3
        },
        {
          "id": "Fludarabine",
          "kind": "drug",
          "degree": 3
        },
        {
          "id": "Ipilimumab",
          "kind": "drug",
          "degree": 3
        },
        {
          "id": "aldesleukin",
          "kind": "drug",
          "degree": 3
        },
        {
          "id": "Vastra Gotaland Region",
          "kind": "sponsor",
          "degree": 3
        },
        {
          "id": "Pembrolizumab",
          "kind": "drug",
          "degree": 2
        },
        {
          "id": "Peking University Cancer Hospital & Institute",
          "kind": "sponsor",
          "degree": 2
        },
        {
          "id": "Dabrafenib Mesylate",
          "kind": "drug",
          "degree": 2
        },
        {
          "id": "Lenvatinib",
          "kind": "drug",
          "degree": 2
        },
        {
          "id": "MEK162",
          "kind": "drug",
          "degree": 2
        },
        {
          "id": "Hoffmann-La Roche",
          "kind": "sponsor",
          "degree": 2
        },
        {
          "id": "Celecoxib",
          "kind": "drug",
          "degree": 2
        },
        {
          "id": "Diwakar Davar",
          "kind": "sponsor",
          "degree": 2
        },
        {
          "id": "Trametinib Dimethyl Sulfoxide",
          "kind": "drug",
          "degree": 2
        },
        {
          "id": "Pfizer",
          "kind": "sponsor",
          "degree": 2
        },
        {
          "id": "sitravatinib",
          "kind": "drug",
          "degree": 1
        },
        {
          "id": "ALT-803",
          "kind": "drug",
          "degree": 1
        },
        {
          "id": "fludarabine phosphate",
          "kind": "drug",
          "degree": 1
        },
        {
          "id": "ATRA",
          "kind": "drug",
          "degree": 1
        },
        {
          "id": "FLX475",
          "kind": "drug",
          "degree": 1
        },
        {
          "id": "humanized anti-PD-1 monoclonal antibody toripalimab",
          "kind": "drug",
          "degree": 1
        },
        {
          "id": "M200 (volociximab) in Combination with Dacarbazine (DTIC)",
          "kind": "drug",
          "degree": 1
        },
        {
          "id": "Pembrolizumab/Quavonlimab",
          "kind": "drug",
          "degree": 1
        },
        {
          "id": "nab-paclitaxel",
          "kind": "drug",
          "degree": 1
        },
        {
          "id": "Recombinant Interferon Alfa 2a",
          "kind": "drug",
          "degree": 1
        },
        {
          "id": "cyclophosphamide",
          "kind": "drug",
          "degree": 1
        },
        {
          "id": "PDL BioPharma, Inc.",
          "kind": "sponsor",
          "degree": 1
        },
        {
          "id": "GP100 peptide",
          "kind": "drug",
          "degree": 1
        },
        {
          "id": "Melphalan",
          "kind": "drug",
          "degree": 1
        },
        {
          "id": "ETBX-011",
          "kind": "drug",
          "degree": 1
        },
        {
          "id": "Cisplatin",
          "kind": "drug",
          "degree": 1
        },
        {
          "id": "haNK",
          "kind": "drug",
          "degree": 1
        },
        {
          "id": "ALVAC MART-1 Vaccine",
          "kind": "drug",
          "degree": 1
        },
        {
          "id": "Therapeutic Tumor Infiltrating Lymphocytes",
          "kind": "drug",
          "degree": 1
        },
        {
          "id": "ETBX-061",
          "kind": "drug",
          "degree": 1
        },
        {
          "id": "IL-2",
          "kind": "drug",
          "degree": 1
        },
        {
          "id": "autologous anti-MART-1 F5 T-cell receptor gene-engineered peripheral blood lymphocytes",
          "kind": "drug",
          "degree": 1
        },
        {
          "id": "Favezelimab/Pembrolizumab",
          "kind": "drug",
          "degree": 1
        },
        {
          "id": "Temozolomide",
          "kind": "drug",
          "degree": 1
        },
        {
          "id": "omega-3-acid ethyl esters",
          "kind": "drug",
          "degree": 1
        },
        {
          "id": "Autologous Tumor Infiltrating Lymphocytes",
          "kind": "drug",
          "degree": 1
        },
        {
          "id": "Gregory Daniels",
          "kind": "sponsor",
          "degree": 1
        },
        {
          "id": "GI-6207",
          "kind": "drug",
          "degree": 1
        },
        {
          "id": "Vibostolimab",
          "kind": "drug",
          "degree": 1
        },
        {
          "id": "Shanghai Junshi Bioscience Co., Ltd.",
          "kind": "sponsor",
          "degree": 1
        },
        {
          "id": "Pegylated Interferon Alfa-2a",
          "kind": "drug",
          "degree": 1
        },
        {
          "id": "Interleukin-2",
          "kind": "drug",
          "degree": 1
        },
        {
          "id": "IL-2 and Nivolumab",
          "kind": "drug",
          "degree": 1
        },
        {
          "id": "Novartis Pharmaceuticals",
          "kind": "sponsor",
          "degree": 1
        },
        {
          "id": "Domvanalimab",
          "kind": "drug",
          "degree": 1
        },
        {
          "id": "Capecitabine",
          "kind": "drug",
          "degree": 1
        },
        {
          "id": "Leucovorin",
          "kind": "drug",
          "degree": 1
        },
        {
          "id": "Avelumab",
          "kind": "drug",
          "degree": 1
        },
        {
          "id": "tislelizumab",
          "kind": "drug",
          "degree": 1
        },
        {
          "id": "GI-6301",
          "kind": "drug",
          "degree": 1
        },
        {
          "id": "Nivolumab",
          "kind": "drug",
          "degree": 1
        },
        {
          "id": "TKI258",
          "kind": "drug",
          "degree": 1
        },
        {
          "id": "Zimberelimab",
          "kind": "drug",
          "degree": 1
        },
        {
          "id": "ETBX-051",
          "kind": "drug",
          "degree": 1
        },
        {
          "id": "RAPT Therapeutics, Inc.",
          "kind": "sponsor",
          "degree": 1
        },
        {
          "id": "Bevacizumab",
          "kind": "drug",
          "degree": 1
        },
        {
          "id": "BMS-936558 (MDX1106-04)",
          "kind": "drug",
          "degree": 1
        },
        {
          "id": "5-fluorouracil",
          "kind": "drug",
          "degree": 1
        }
      ],
      "edges": [
        {
          "source": "National Cancer Institute (NCI)",
          "target": "Cyclophosphamide",
          "weight": 4
        },
        {
          "source": "Bristol-Myers Squibb",
          "target": "Ipilimumab",
          "weight": 3
        },
        {
          "source": "Fred Hutchinson Cancer Center",
          "target": "therapeutic autologous lymphocytes",
          "weight": 3
        },
        {
          "source": "Merck Sharp & Dohme LLC",
          "target": "Pembrolizumab",
          "weight": 2
        },
        {
          "source": "Merck Sharp & Dohme LLC",
          "target": "Lenvatinib",
          "weight": 2
        },
        {
          "source": "National Cancer Institute (NCI)",
          "target": "Aldesleukin",
          "weight": 2
        },
        {
          "source": "National Cancer Institute (NCI)",
          "target": "Fludarabine",
          "weight": 2
        },
        {
          "source": "Fred Hutchinson Cancer Center",
          "target": "aldesleukin",
          "weight": 2
        },
        {
          "source": "National Cancer Institute (NCI)",
          "target": "Celecoxib",
          "weight": 2
        },
        {
          "source": "Pfizer",
          "target": "MEK162",
          "weight": 2
        },
        {
          "source": "National Cancer Institute (NCI)",
          "target": "Trametinib Dimethyl Sulfoxide",
          "weight": 2
        },
        {
          "source": "National Cancer Institute (NCI)",
          "target": "Dabrafenib Mesylate",
          "weight": 2
        },
        {
          "source": "National Cancer Institute (NCI)",
          "target": "fludarabine phosphate",
          "weight": 1
        },
        {
          "source": "National Cancer Institute (NCI)",
          "target": "aldesleukin",
          "weight": 1
        },
        {
          "source": "National Cancer Institute (NCI)",
          "target": "ALVAC MART-1 Vaccine",
          "weight": 1
        },
        {
          "source": "National Cancer Institute (NCI)",
          "target": "autologous anti-MART-1 F5 T-cell receptor gene-engineered peripheral blood lymphocytes",
          "weight": 1
        },
        {
          "source": "National Cancer Institute (NCI)",
          "target": "cyclophosphamide",
          "weight": 1
        },
        {
          "source": "Novartis Pharmaceuticals",
          "target": "TKI258",
          "weight": 1
        },
        {
          "source": "Bristol-Myers Squibb",
          "target": "BMS-936558 (MDX1106-04)",
          "weight": 1
        },
        {
          "source": "Diwakar Davar",
          "target": "Domvanalimab",
          "weight": 1
        },
        {
          "source": "Diwakar Davar",
          "target": "Zimberelimab",
          "weight": 1
        },
        {
          "source": "Gregory Daniels",
          "target": "IL-2 and Nivolumab",
          "weight": 1
        },
        {
          "source": "Merck Sharp & Dohme LLC",
          "target": "Vibostolimab",
          "weight": 1
        },
        {
          "source": "Merck Sharp & Dohme LLC",
          "target": "ATRA",
          "weight": 1
        },
        {
          "source": "Merck Sharp & Dohme LLC",
          "target": "Pembrolizumab/Quavonlimab",
          "weight": 1
        },
        {
          "source": "Merck Sharp & Dohme LLC",
          "target": "Favezelimab/Pembrolizumab",
          "weight": 1
        },
        {
          "source": "National Cancer Institute (NCI)",
          "target": "GP100 peptide",
          "weight": 1
        },
        {
          "source": "National Cancer Institute (NCI)",
          "target": "IL-2",
          "weight": 1
        },
        {
          "source": "Shanghai Junshi Bioscience Co., Ltd.",
          "target": "humanized anti-PD-1 monoclonal antibody toripalimab",
          "weight": 1
        },
        {
          "source": "Vastra Gotaland Region",
          "target": "Autologous Tumor Infiltrating Lymphocytes",
          "weight": 1
        },
        {
          "source": "Vastra Gotaland Region",
          "target": "Melphalan",
          "weight": 1
        },
        {
          "source": "Vastra Gotaland Region",
          "target": "Interleukin-2",
          "weight": 1
        },
        {
          "source": "Merck Sharp & Dohme LLC",
          "target": "Temozolomide",
          "weight": 1
        },
        {
          "source": "ImmunityBio, Inc.",
          "target": "Avelumab",
          "weight": 1
        },
        {
          "source": "ImmunityBio, Inc.",
          "target": "ALT-803",
          "weight": 1
        },
        {
          "source": "ImmunityBio, Inc.",
          "target": "GI-6207",
          "weight": 1
        },
        {
          "source": "ImmunityBio, Inc.",
          "target": "ETBX-011",
          "weight": 1
        },
        {
          "source": "ImmunityBio, Inc.",
          "target": "Cisplatin",
          "weight": 1
        },
        {
          "source": "ImmunityBio, Inc.",
          "target": "GI-6301",
          "weight": 1
        },
        {
          "source": "ImmunityBio, Inc.",
          "target": "Nivolumab",
          "weight": 1
        },
        {
          "source": "ImmunityBio, Inc.",
          "target": "ETBX-051",
          "weight": 1
        },
        {
          "source": "ImmunityBio, Inc.",
          "target": "haNK",
          "weight": 1
        },
        {
          "source": "ImmunityBio, Inc.",
          "target": "Cyclophosphamide",
          "weight": 1
        },
        {
          "source": "ImmunityBio, Inc.",
          "target": "ETBX-061",
          "weight": 1
        },
        {
          "source": "ImmunityBio, Inc.",
          "target": "nab-paclitaxel",
          "weight": 1
        },
        {
          "source": "ImmunityBio, Inc.",
          "target": "Bevacizumab",
          "weight": 1
        },
        {
          "source": "ImmunityBio, Inc.",
          "target": "Capecitabine",
          "weight": 1
        },
        {
          "source": "ImmunityBio, Inc.",
          "target": "Leucovorin",
          "weight": 1
        },
        {
          "source": "ImmunityBio, Inc.",
          "target": "5-fluorouracil",
          "weight": 1
        },
        {
          "source": "ImmunityBio, Inc.",
          "target": "omega-3-acid ethyl esters",
          "weight": 1
        },
        {
          "source": "Hoffmann-La Roche",
          "target": "Pegylated Interferon Alfa-2a",
          "weight": 1
        },
        {
          "source": "Hoffmann-La Roche",
          "target": "Recombinant Interferon Alfa 2a",
          "weight": 1
        },
        {
          "source": "Peking University Cancer Hospital & Institute",
          "target": "sitravatinib",
          "weight": 1
        },
        {
          "source": "Peking University Cancer Hospital & Institute",
          "target": "tislelizumab",
          "weight": 1
        },
        {
          "source": "PDL BioPharma, Inc.",
          "target": "M200 (volociximab) in Combination with Dacarbazine (DTIC)",
          "weight": 1
        },
        {
          "source": "City of Hope Medical Center",
          "target": "Therapeutic Tumor Infiltrating Lymphocytes",
          "weight": 1
        },
        {
          "source": "City of Hope Medical Center",
          "target": "Aldesleukin",
          "weight": 1
        },
        {
          "source": "City of Hope Medical Center",
          "target": "Fludarabine",
          "weight": 1
        },
        {
          "source": "City of Hope Medical Center",
          "target": "Cyclophosphamide",
          "weight": 1
        },
        {
          "source": "RAPT Therapeutics, Inc.",
          "target": "FLX475",
          "weight": 1
        }
      ]
    }
  },
  "meta": {
    "filters": {
      "condition": "melanoma"
    },
    "analysis_type": "network",
    "source": "clinicaltrials.gov",
    "study_count": 300,
    "capped": true,
    "notes": [
      "엣지 441개 중 가중치 상위 60개만 표시합니다(허브 중심 관계망).",
      "결과가 상한(MAX_STUDIES)에 걸려 최근/상위 일부 study만 집계했습니다. 수치는 전체가 아닌 표본 기준입니다."
    ]
  },
  "citations": {
    "National Cancer Institute (NCI)|Cyclophosphamide": [
      {
        "nct_id": "NCT00924001",
        "excerpt": "Chemotherapy Followed by Infusion of DMF5 Cells to Treat Metastatic Melanoma"
      },
      {
        "nct_id": "NCT01341496",
        "excerpt": "Tumor Cell Vaccines and ISCOMATRIX With Chemotherapy After Tumor Removal"
      },
      {
        "nct_id": "NCT02489266",
        "excerpt": "In Vivo Persistence of Adoptively-Transferred TIL Cultured With Akti in People With Metastatic Melanoma"
      }
    ],
    "Bristol-Myers Squibb|Ipilimumab": [
      {
        "nct_id": "NCT01024231",
        "excerpt": "Dose-escalation Study of Combination BMS-936558 (MDX-1106) and Ipilimumab in Subjects With Unresectable Stage III or Stage IV Malignant Melanoma"
      },
      {
        "nct_id": "NCT02050594",
        "excerpt": "Ipilimumab 12-month Intensive Pharmacovigilance Protocol"
      },
      {
        "nct_id": "NCT02516527",
        "excerpt": "A Phase 1 Dose Escalation Study of the Safety, Tolerability, and Pharmacokinetics of Ipilimumab in Chinese Subjects With Select Advanced Solid Tumors"
      }
    ],
    "Fred Hutchinson Cancer Center|therapeutic autologous lymphocytes": [
      {
        "nct_id": "NCT00945269",
        "excerpt": "Therapeutic Autologous Lymphocytes, Aldesleukin, and Denileukin Diftitox in Treating Patients With Stage III-IV Melanoma"
      },
      {
        "nct_id": "NCT00317759",
        "excerpt": "Fludarabine Followed By Adoptive Immunotherapy in Treating Patients With Stage IV Melanoma"
      },
      {
        "nct_id": "NCT00553306",
        "excerpt": "Laboratory-Treated T Cells and Aldesleukin After Cyclophosphamide in Treating Patients With Stage IV Melanoma"
      }
    ],
    "Merck Sharp & Dohme LLC|Pembrolizumab": [
      {
        "nct_id": "NCT04305054",
        "excerpt": "Substudy 02B: Safety and Efficacy of Pembrolizumab in Combination With Investigational Agents or Pembrolizumab Alone in Participants With First Line (1L) Advanced Melanoma (MK-3475-02B/KEYMAKER-U02)"
      },
      {
        "nct_id": "NCT03820986",
        "excerpt": "Safety and Efficacy Study of Pembrolizumab (MK-3475) Combined With Lenvatinib (MK-7902/E7080) as First-line Intervention in Adults With Advance Melanoma (MK-7902-003/E7080-G000-312/LEAP-003)"
      }
    ],
    "Merck Sharp & Dohme LLC|Lenvatinib": [
      {
        "nct_id": "NCT04305054",
        "excerpt": "Substudy 02B: Safety and Efficacy of Pembrolizumab in Combination With Investigational Agents or Pembrolizumab Alone in Participants With First Line (1L) Advanced Melanoma (MK-3475-02B/KEYMAKER-U02)"
      },
      {
        "nct_id": "NCT03820986",
        "excerpt": "Safety and Efficacy Study of Pembrolizumab (MK-3475) Combined With Lenvatinib (MK-7902/E7080) as First-line Intervention in Adults With Advance Melanoma (MK-7902-003/E7080-G000-312/LEAP-003)"
      }
    ],
    "National Cancer Institute (NCI)|Aldesleukin": [
      {
        "nct_id": "NCT00924001",
        "excerpt": "Chemotherapy Followed by Infusion of DMF5 Cells to Treat Metastatic Melanoma"
      },
      {
        "nct_id": "NCT02489266",
        "excerpt": "In Vivo Persistence of Adoptively-Transferred TIL Cultured With Akti in People With Metastatic Melanoma"
      }
    ],
    "National Cancer Institute (NCI)|Fludarabine": [
      {
        "nct_id": "NCT00924001",
        "excerpt": "Chemotherapy Followed by Infusion of DMF5 Cells to Treat Metastatic Melanoma"
      },
      {
        "nct_id": "NCT02489266",
        "excerpt": "In Vivo Persistence of Adoptively-Transferred TIL Cultured With Akti in People With Metastatic Melanoma"
      }
    ],
    "Fred Hutchinson Cancer Center|aldesleukin": [
      {
        "nct_id": "NCT00945269",
        "excerpt": "Therapeutic Autologous Lymphocytes, Aldesleukin, and Denileukin Diftitox in Treating Patients With Stage III-IV Melanoma"
      },
      {
        "nct_id": "NCT00553306",
        "excerpt": "Laboratory-Treated T Cells and Aldesleukin After Cyclophosphamide in Treating Patients With Stage IV Melanoma"
      }
    ],
    "National Cancer Institute (NCI)|Celecoxib": [
      {
        "nct_id": "NCT01341496",
        "excerpt": "Tumor Cell Vaccines and ISCOMATRIX With Chemotherapy After Tumor Removal"
      },
      {
        "nct_id": "NCT02054104",
        "excerpt": "Adjuvant Tumor Lysate Vaccine and Iscomatrix With or Without Metronomic Oral Cyclophosphamide and Celecoxib in Patients With Malignancies Involving Lungs, Esophagus, Pleura, or Mediastinum"
      }
    ],
    "Pfizer|MEK162": [
      {
        "nct_id": "NCT01909453",
        "excerpt": "Study Comparing Combination of LGX818 Plus MEK162 Versus Vemurafenib and LGX818 Monotherapy in BRAF Mutant Melanoma"
      },
      {
        "nct_id": "NCT01781572",
        "excerpt": "A Phase Ib/II Study of LEE011 in Combination With MEK162 in Patients With NRAS Mutant Melanoma"
      }
    ],
    "National Cancer Institute (NCI)|Trametinib Dimethyl Sulfoxide": [
      {
        "nct_id": "NCT04439292",
        "excerpt": "Testing Trametinib and Dabrafenib as a Potential Targeted Treatment in Cancers With BRAF Genetic Changes (MATCH-Subprotocol H)"
      },
      {
        "nct_id": "NCT02196181",
        "excerpt": "Testing Two Different Treatment Schedules of Dabrafenib and Trametinib for Skin Cancer Which Has Spread"
      }
    ],
    "National Cancer Institute (NCI)|Dabrafenib Mesylate": [
      {
        "nct_id": "NCT04439292",
        "excerpt": "Testing Trametinib and Dabrafenib as a Potential Targeted Treatment in Cancers With BRAF Genetic Changes (MATCH-Subprotocol H)"
      },
      {
        "nct_id": "NCT02196181",
        "excerpt": "Testing Two Different Treatment Schedules of Dabrafenib and Trametinib for Skin Cancer Which Has Spread"
      }
    ],
    "National Cancer Institute (NCI)|fludarabine phosphate": [
      {
        "nct_id": "NCT00612222",
        "excerpt": "Anti-MART-1 F5 Cells Plus ALVAC MART-1 Vaccine to Treat Advanced Melanoma"
      }
    ],
    "National Cancer Institute (NCI)|aldesleukin": [
      {
        "nct_id": "NCT00612222",
        "excerpt": "Anti-MART-1 F5 Cells Plus ALVAC MART-1 Vaccine to Treat Advanced Melanoma"
      }
    ],
    "National Cancer Institute (NCI)|ALVAC MART-1 Vaccine": [
      {
        "nct_id": "NCT00612222",
        "excerpt": "Anti-MART-1 F5 Cells Plus ALVAC MART-1 Vaccine to Treat Advanced Melanoma"
      }
    ],
    "National Cancer Institute (NCI)|autologous anti-MART-1 F5 T-cell receptor gene-engineered peripheral blood lymphocytes": [
      {
        "nct_id": "NCT00612222",
        "excerpt": "Anti-MART-1 F5 Cells Plus ALVAC MART-1 Vaccine to Treat Advanced Melanoma"
      }
    ],
    "National Cancer Institute (NCI)|cyclophosphamide": [
      {
        "nct_id": "NCT00612222",
        "excerpt": "Anti-MART-1 F5 Cells Plus ALVAC MART-1 Vaccine to Treat Advanced Melanoma"
      }
    ],
    "Novartis Pharmaceuticals|TKI258": [
      {
        "nct_id": "NCT00303251",
        "excerpt": "Safety of TKI258 in Advanced/Metastatic Melanoma Subjects"
      }
    ],
    "Bristol-Myers Squibb|BMS-936558 (MDX1106-04)": [
      {
        "nct_id": "NCT01024231",
        "excerpt": "Dose-escalation Study of Combination BMS-936558 (MDX-1106) and Ipilimumab in Subjects With Unresectable Stage III or Stage IV Malignant Melanoma"
      }
    ],
    "Diwakar Davar|Domvanalimab": [
      {
        "nct_id": "NCT05130177",
        "excerpt": "Zimberelimab (AB122) With TIGIT Inhibitor Domvanalimab (AB154) in PD-1 Relapsed/Refractory Melanoma"
      }
    ],
    "Diwakar Davar|Zimberelimab": [
      {
        "nct_id": "NCT05130177",
        "excerpt": "Zimberelimab (AB122) With TIGIT Inhibitor Domvanalimab (AB154) in PD-1 Relapsed/Refractory Melanoma"
      }
    ],
    "Gregory Daniels|IL-2 and Nivolumab": [
      {
        "nct_id": "NCT03991130",
        "excerpt": "High Dose IL-2 in Combination With Anti-PD-1 to Overcome Anti-PD-1 Resistance in Metastatic Melanoma and Renal Cell Carcinoma"
      }
    ],
    "Merck Sharp & Dohme LLC|Vibostolimab": [
      {
        "nct_id": "NCT04305054",
        "excerpt": "Substudy 02B: Safety and Efficacy of Pembrolizumab in Combination With Investigational Agents or Pembrolizumab Alone in Participants With First Line (1L) Advanced Melanoma (MK-3475-02B/KEYMAKER-U02)"
      }
    ],
    "Merck Sharp & Dohme LLC|ATRA": [
      {
        "nct_id": "NCT04305054",
        "excerpt": "Substudy 02B: Safety and Efficacy of Pembrolizumab in Combination With Investigational Agents or Pembrolizumab Alone in Participants With First Line (1L) Advanced Melanoma (MK-3475-02B/KEYMAKER-U02)"
      }
    ],
    "Merck Sharp & Dohme LLC|Pembrolizumab/Quavonlimab": [
      {
        "nct_id": "NCT04305054",
        "excerpt": "Substudy 02B: Safety and Efficacy of Pembrolizumab in Combination With Investigational Agents or Pembrolizumab Alone in Participants With First Line (1L) Advanced Melanoma (MK-3475-02B/KEYMAKER-U02)"
      }
    ],
    "Merck Sharp & Dohme LLC|Favezelimab/Pembrolizumab": [
      {
        "nct_id": "NCT04305054",
        "excerpt": "Substudy 02B: Safety and Efficacy of Pembrolizumab in Combination With Investigational Agents or Pembrolizumab Alone in Participants With First Line (1L) Advanced Melanoma (MK-3475-02B/KEYMAKER-U02)"
      }
    ],
    "National Cancer Institute (NCI)|GP100 peptide": [
      {
        "nct_id": "NCT00001705",
        "excerpt": "Immunization of Patients With Metastatic Melanoma Using the GP100 Peptide Preceded by an Endoplasmic Reticulum Insertion Signal Sequence"
      }
    ],
    "National Cancer Institute (NCI)|IL-2": [
      {
        "nct_id": "NCT00001705",
        "excerpt": "Immunization of Patients With Metastatic Melanoma Using the GP100 Peptide Preceded by an Endoplasmic Reticulum Insertion Signal Sequence"
      }
    ],
    "Shanghai Junshi Bioscience Co., Ltd.|humanized anti-PD-1 monoclonal antibody toripalimab": [
      {
        "nct_id": "NCT03013101",
        "excerpt": "Safety and Efficacy of Recombinant Humanized Anti-PD-1 mAb for Patients With Locally Advanced or Metastatic Melanoma"
      }
    ],
    "Vastra Gotaland Region|Autologous Tumor Infiltrating Lymphocytes": [
      {
        "nct_id": "NCT04812470",
        "excerpt": "Hepatic Arterial Infusion of Autologous Tumor Infiltrating Lymphocytes in Patients With Melanoma and Liver Metastases"
      }
    ],
    "Vastra Gotaland Region|Melphalan": [
      {
        "nct_id": "NCT04812470",
        "excerpt": "Hepatic Arterial Infusion of Autologous Tumor Infiltrating Lymphocytes in Patients With Melanoma and Liver Metastases"
      }
    ],
    "Vastra Gotaland Region|Interleukin-2": [
      {
        "nct_id": "NCT04812470",
        "excerpt": "Hepatic Arterial Infusion of Autologous Tumor Infiltrating Lymphocytes in Patients With Melanoma and Liver Metastases"
      }
    ],
    "Merck Sharp & Dohme LLC|Temozolomide": [
      {
        "nct_id": "NCT00831545",
        "excerpt": "Study to Evaluate the Efficacy and Safety of Temozolomide in Subjects With Brain Metastases of Either Malignant Melanoma, Breast, or Non-small Cell Lung Cancer (P02064)"
      }
    ],
    "ImmunityBio, Inc.|Avelumab": [
      {
        "nct_id": "NCT03167177",
        "excerpt": "QUILT-3.046: NANT Melanoma Vaccine: Combination Immunotherapy in Subjects With Melanoma Who Have Progressed On or After Chemotherapy and PD-1/PD-L1 Therapy"
      }
    ],
    "ImmunityBio, Inc.|ALT-803": [
      {
        "nct_id": "NCT03167177",
        "excerpt": "QUILT-3.046: NANT Melanoma Vaccine: Combination Immunotherapy in Subjects With Melanoma Who Have Progressed On or After Chemotherapy and PD-1/PD-L1 Therapy"
      }
    ],
    "ImmunityBio, Inc.|GI-6207": [
      {
        "nct_id": "NCT03167177",
        "excerpt": "QUILT-3.046: NANT Melanoma Vaccine: Combination Immunotherapy in Subjects With Melanoma Who Have Progressed On or After Chemotherapy and PD-1/PD-L1 Therapy"
      }
    ],
    "ImmunityBio, Inc.|ETBX-011": [
      {
        "nct_id": "NCT03167177",
        "excerpt": "QUILT-3.046: NANT Melanoma Vaccine: Combination Immunotherapy in Subjects With Melanoma Who Have Progressed On or After Chemotherapy and PD-1/PD-L1 Therapy"
      }
    ],
    "ImmunityBio, Inc.|Cisplatin": [
      {
        "nct_id": "NCT03167177",
        "excerpt": "QUILT-3.046: NANT Melanoma Vaccine: Combination Immunotherapy in Subjects With Melanoma Who Have Progressed On or After Chemotherapy and PD-1/PD-L1 Therapy"
      }
    ],
    "ImmunityBio, Inc.|GI-6301": [
      {
        "nct_id": "NCT03167177",
        "excerpt": "QUILT-3.046: NANT Melanoma Vaccine: Combination Immunotherapy in Subjects With Melanoma Who Have Progressed On or After Chemotherapy and PD-1/PD-L1 Therapy"
      }
    ],
    "ImmunityBio, Inc.|Nivolumab": [
      {
        "nct_id": "NCT03167177",
        "excerpt": "QUILT-3.046: NANT Melanoma Vaccine: Combination Immunotherapy in Subjects With Melanoma Who Have Progressed On or After Chemotherapy and PD-1/PD-L1 Therapy"
      }
    ],
    "ImmunityBio, Inc.|ETBX-051": [
      {
        "nct_id": "NCT03167177",
        "excerpt": "QUILT-3.046: NANT Melanoma Vaccine: Combination Immunotherapy in Subjects With Melanoma Who Have Progressed On or After Chemotherapy and PD-1/PD-L1 Therapy"
      }
    ],
    "ImmunityBio, Inc.|haNK": [
      {
        "nct_id": "NCT03167177",
        "excerpt": "QUILT-3.046: NANT Melanoma Vaccine: Combination Immunotherapy in Subjects With Melanoma Who Have Progressed On or After Chemotherapy and PD-1/PD-L1 Therapy"
      }
    ],
    "ImmunityBio, Inc.|Cyclophosphamide": [
      {
        "nct_id": "NCT03167177",
        "excerpt": "QUILT-3.046: NANT Melanoma Vaccine: Combination Immunotherapy in Subjects With Melanoma Who Have Progressed On or After Chemotherapy and PD-1/PD-L1 Therapy"
      }
    ],
    "ImmunityBio, Inc.|ETBX-061": [
      {
        "nct_id": "NCT03167177",
        "excerpt": "QUILT-3.046: NANT Melanoma Vaccine: Combination Immunotherapy in Subjects With Melanoma Who Have Progressed On or After Chemotherapy and PD-1/PD-L1 Therapy"
      }
    ],
    "ImmunityBio, Inc.|nab-paclitaxel": [
      {
        "nct_id": "NCT03167177",
        "excerpt": "QUILT-3.046: NANT Melanoma Vaccine: Combination Immunotherapy in Subjects With Melanoma Who Have Progressed On or After Chemotherapy and PD-1/PD-L1 Therapy"
      }
    ],
    "ImmunityBio, Inc.|Bevacizumab": [
      {
        "nct_id": "NCT03167177",
        "excerpt": "QUILT-3.046: NANT Melanoma Vaccine: Combination Immunotherapy in Subjects With Melanoma Who Have Progressed On or After Chemotherapy and PD-1/PD-L1 Therapy"
      }
    ],
    "ImmunityBio, Inc.|Capecitabine": [
      {
        "nct_id": "NCT03167177",
        "excerpt": "QUILT-3.046: NANT Melanoma Vaccine: Combination Immunotherapy in Subjects With Melanoma Who Have Progressed On or After Chemotherapy and PD-1/PD-L1 Therapy"
      }
    ],
    "ImmunityBio, Inc.|Leucovorin": [
      {
        "nct_id": "NCT03167177",
        "excerpt": "QUILT-3.046: NANT Melanoma Vaccine: Combination Immunotherapy in Subjects With Melanoma Who Have Progressed On or After Chemotherapy and PD-1/PD-L1 Therapy"
      }
    ],
    "ImmunityBio, Inc.|5-fluorouracil": [
      {
        "nct_id": "NCT03167177",
        "excerpt": "QUILT-3.046: NANT Melanoma Vaccine: Combination Immunotherapy in Subjects With Melanoma Who Have Progressed On or After Chemotherapy and PD-1/PD-L1 Therapy"
      }
    ],
    "ImmunityBio, Inc.|omega-3-acid ethyl esters": [
      {
        "nct_id": "NCT03167177",
        "excerpt": "QUILT-3.046: NANT Melanoma Vaccine: Combination Immunotherapy in Subjects With Melanoma Who Have Progressed On or After Chemotherapy and PD-1/PD-L1 Therapy"
      }
    ],
    "Hoffmann-La Roche|Pegylated Interferon Alfa-2a": [
      {
        "nct_id": "NCT02829775",
        "excerpt": "A Study of Continued Treatment Among Participants Who Have Responded to Peginterferon Alfa-2a (Pegasys®) or Recombinant Interferon Alfa-2a (Roferon-A®) in Prior Clinical Studies"
      }
    ],
    "Hoffmann-La Roche|Recombinant Interferon Alfa 2a": [
      {
        "nct_id": "NCT02829775",
        "excerpt": "A Study of Continued Treatment Among Participants Who Have Responded to Peginterferon Alfa-2a (Pegasys®) or Recombinant Interferon Alfa-2a (Roferon-A®) in Prior Clinical Studies"
      }
    ],
    "Peking University Cancer Hospital & Institute|sitravatinib": [
      {
        "nct_id": "NCT05104801",
        "excerpt": "Sitravatinib With or Without Tislelizumab in Patients With Unresectable or Metastatic Melanoma"
      }
    ],
    "Peking University Cancer Hospital & Institute|tislelizumab": [
      {
        "nct_id": "NCT05104801",
        "excerpt": "Sitravatinib With or Without Tislelizumab in Patients With Unresectable or Metastatic Melanoma"
      }
    ],
    "PDL BioPharma, Inc.|M200 (volociximab) in Combination with Dacarbazine (DTIC)": [
      {
        "nct_id": "NCT00099970",
        "excerpt": "Volociximab in Combination With DTIC in Patients With Metastatic Melanoma Not Previously Treated With Chemotherapy"
      }
    ],
    "City of Hope Medical Center|Therapeutic Tumor Infiltrating Lymphocytes": [
      {
        "nct_id": "NCT06626256",
        "excerpt": "STIL101 for Injection for the Treatment of Locally Advanced, Metastatic or Unresectable Pancreatic Cancer, Colorectal Cancer, Renal Cell Cancer, Cervical Cancer and Melanoma"
      }
    ],
    "City of Hope Medical Center|Aldesleukin": [
      {
        "nct_id": "NCT06626256",
        "excerpt": "STIL101 for Injection for the Treatment of Locally Advanced, Metastatic or Unresectable Pancreatic Cancer, Colorectal Cancer, Renal Cell Cancer, Cervical Cancer and Melanoma"
      }
    ],
    "City of Hope Medical Center|Fludarabine": [
      {
        "nct_id": "NCT06626256",
        "excerpt": "STIL101 for Injection for the Treatment of Locally Advanced, Metastatic or Unresectable Pancreatic Cancer, Colorectal Cancer, Renal Cell Cancer, Cervical Cancer and Melanoma"
      }
    ],
    "City of Hope Medical Center|Cyclophosphamide": [
      {
        "nct_id": "NCT06626256",
        "excerpt": "STIL101 for Injection for the Treatment of Locally Advanced, Metastatic or Unresectable Pancreatic Cancer, Colorectal Cancer, Renal Cell Cancer, Cervical Cancer and Melanoma"
      }
    ],
    "RAPT Therapeutics, Inc.|FLX475": [
      {
        "nct_id": "NCT04894994",
        "excerpt": "FLX475 in Combination With Ipilimumab in Advanced Melanoma"
      }
    ]
  }
}
```

## Empty result — 존재하지 않는 약물(graceful handling)

**요청:**
```json
{
  "query": "How are trials for Zzzznonexistentdrug distributed across phases?"
}
```

**응답:**
```json
{
  "visualization": {
    "type": "no_data",
    "title": "Trial distribution by phase for Zzzznonexistentdrug",
    "encoding": {},
    "data": []
  },
  "meta": {
    "filters": {},
    "analysis_type": "distribution",
    "source": "clinicaltrials.gov",
    "study_count": 0,
    "capped": false,
    "notes": [
      "조건에 맞는 시험을 찾지 못했습니다."
    ]
  },
  "citations": null
}
```
