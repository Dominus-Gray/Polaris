# Polaris Platform - Sample MongoDB Document Structures

This document provides detailed sample document structures for the key MongoDB collections used in the Polaris platform. All documents use UUID4 format for IDs and follow the data standardization principles implemented in the platform.

## Table of Contents
1. [Users Collection](#users-collection)
2. [Assessments Collection](#assessments-collection)
3. [Service Requests Collection](#service-requests-collection)

---

## Users Collection

The `users` collection stores all user accounts across different roles (client, provider, agency, navigator) with role-based fields and approval workflows.

### Sample Client User Document
```json
{
  "_id": "7b425866-1819-49ce-9647-b10d47eab5bf",
  "id": "7b425866-1819-49ce-9647-b10d47eab5bf",
  "email": "client.qa@polaris.example.com",
  "hashed_password": "$pbkdf2-sha256$29000$...",
  "role": "client",
  "approval_status": "approved",
  "is_active": true,
  "created_at": "2025-01-15T10:30:00Z",
  "profile_complete": true,
  "terms_accepted": true,
  "terms_accepted_at": "2025-01-15T10:30:00Z",
  "license_code": "7536291048",
  "payment_info": {
    "stripe_customer_id": "cus_P8yJ3kLmN9qR2s",
    "payment_methods": ["pm_1O2N3k4L5m6N7o8P9q"]
  },
  "profile_data": {
    "business_name": "Tech Solutions LLC",
    "business_type": "LLC",
    "industry": "Technology Services",
    "employees": "5-10",
    "annual_revenue": "$100K-$500K",
    "phone": "+1-210-555-0123",
    "address": {
      "street": "123 Commerce St",
      "city": "San Antonio",
      "state": "TX",
      "zip": "78205",
      "country": "USA"
    },
    "website": "https://techsolutions.example.com",
    "years_in_business": 3,
    "certifications": ["MBE", "SBE"],
    "service_areas": ["area5", "area1", "area4"],
    "target_contract_value": "$50K-$250K"
  },
  "assessment_progress": {
    "sessions_completed": 2,
    "last_session": "2025-01-14T15:45:00Z",
    "current_readiness_score": 75.5,
    "areas_completed": ["area1", "area2", "area5"],
    "gaps_identified": 3,
    "certificates_earned": []
  },
  "engagement_history": {
    "total_services": 5,
    "active_engagements": 1,
    "completed_engagements": 4,
    "total_spent": 8750.00,
    "average_rating": 4.7,
    "preferred_providers": ["66040b94-1323-45bb-867e-95c92785707a"]
  },
  "last_login": "2025-01-15T09:15:00Z",
  "login_count": 47,
  "knowledge_base_access": {
    "unlocked_areas": ["area1", "area2", "area5"],
    "total_downloads": 12,
    "last_access": "2025-01-14T16:20:00Z",
    "subscription_status": "partial"
  }
}
```

### Sample Provider User Document
```json
{
  "_id": "66040b94-1323-45bb-867e-95c92785707a",
  "id": "66040b94-1323-45bb-867e-95c92785707a",
  "email": "provider.qa@polaris.example.com",
  "hashed_password": "$pbkdf2-sha256$29000$...",
  "role": "provider",
  "approval_status": "approved",
  "is_active": true,
  "created_at": "2025-01-10T14:20:00Z",
  "profile_complete": true,
  "terms_accepted": true,
  "terms_accepted_at": "2025-01-10T14:20:00Z",
  "profile_data": {
    "business_name": "Enterprise Consulting Group",
    "business_type": "Corporation",
    "contact_name": "Sarah Rodriguez",
    "phone": "+1-210-555-0456",
    "address": {
      "street": "456 Business Park Dr",
      "city": "San Antonio", 
      "state": "TX",
      "zip": "78230",
      "country": "USA"
    },
    "website": "https://enterpriseconsulting.example.com",
    "years_in_business": 8,
    "employee_count": "25-50",
    "certifications": ["ISO 9001", "CMMI Level 3", "SOC 2"],
    "service_areas": ["area1", "area2", "area3", "area4", "area5"],
    "specialties": ["Business Formation", "Financial Systems", "Compliance"],
    "hourly_rate_range": "$150-$300",
    "project_capacity": "5-10 concurrent projects",
    "service_description": "Full-service business consulting with 8+ years helping small businesses achieve procurement readiness"
  },
  "service_metrics": {
    "total_proposals": 23,
    "proposals_accepted": 18,
    "completion_rate": 96.5,
    "average_rating": 4.8,
    "total_earnings": 125400.00,
    "active_engagements": 3,
    "response_time_hours": 2.5
  },
  "capabilities": {
    "service_areas": {
      "area1": {
        "name": "Business Formation & Registration",
        "expertise_level": "expert",
        "years_experience": 8,
        "success_rate": 98.2,
        "typical_timeline": "2-4 weeks",
        "price_range": "$2000-$5000"
      },
      "area5": {
        "name": "Technology & Security Infrastructure", 
        "expertise_level": "advanced",
        "years_experience": 5,
        "success_rate": 94.8,
        "typical_timeline": "3-6 weeks",
        "price_range": "$5000-$15000"
      }
    },
    "tools_used": ["Microsoft Suite", "QuickBooks", "Salesforce", "DocuSign"],
    "languages": ["English", "Spanish"],
    "availability": "Monday-Friday 8AM-6PM CST"
  },
  "last_login": "2025-01-15T08:30:00Z",
  "notification_preferences": {
    "email": true,
    "sms": false,
    "new_requests": true,
    "engagement_updates": true,
    "payment_notifications": true
  }
}
```

### Sample Agency User Document
```json
{
  "_id": "3e33ce75-d3ab-4fad-8101-f6a40b98b03d",
  "id": "3e33ce75-d3ab-4fad-8101-f6a40b98b03d", 
  "email": "agency.qa@polaris.example.com",
  "hashed_password": "$pbkdf2-sha256$29000$...",
  "role": "agency",
  "approval_status": "approved",
  "is_active": true,
  "created_at": "2025-01-08T11:15:00Z",
  "profile_complete": true,
  "terms_accepted": true,
  "terms_accepted_at": "2025-01-08T11:15:00Z",
  "profile_data": {
    "agency_name": "San Antonio SBDC",
    "agency_type": "Small Business Development Center",
    "contact_name": "Maria Garcia",
    "phone": "+1-210-555-0789",
    "address": {
      "street": "789 Economic Development Blvd",
      "city": "San Antonio",
      "state": "TX", 
      "zip": "78215",
      "country": "USA"
    },
    "website": "https://sanantonio-sbdc.example.com",
    "service_territory": "Bexar County, TX",
    "certification_authority": "SBA Regional Office",
    "license_authority": "City of San Antonio Economic Development"
  },
  "agency_metrics": {
    "licenses_issued": 247,
    "active_licenses": 89,
    "businesses_served": 156,
    "total_contract_value_facilitated": 2850000.00,
    "success_rate": 87.3,
    "average_readiness_improvement": 42.5
  },
  "licensing_config": {
    "license_prefix": "SA2025",
    "default_validity_months": 12,
    "renewal_notice_days": 30,
    "max_licenses_per_batch": 100,
    "current_sequence": 1247
  },
  "branding_config": {
    "primary_color": "#2563eb",
    "secondary_color": "#1e40af", 
    "logo_url": "https://sanantonio-sbdc.example.com/logo.png",
    "custom_domain": "polaris.sanantonio-sbdc.com",
    "white_label_enabled": true,
    "certificate_template": "sa_custom_v2"
  },
  "approval_history": {
    "approved_at": "2025-01-09T09:30:00Z",
    "approved_by": "e488f229-6885-4e68-b6c4-55268295bcab",
    "verification_documents": ["business_license.pdf", "sba_certification.pdf"],
    "approval_notes": "Verified SBA certification and local authority"
  }
}
```

### Sample Navigator User Document
```json
{
  "_id": "e488f229-6885-4e68-b6c4-55268295bcab",
  "id": "e488f229-6885-4e68-b6c4-55268295bcab",
  "email": "navigator.qa@polaris.example.com", 
  "hashed_password": "$pbkdf2-sha256$29000$...",
  "role": "navigator",
  "approval_status": "approved",
  "is_active": true,
  "created_at": "2025-01-05T13:45:00Z",
  "profile_complete": true,
  "terms_accepted": true,
  "terms_accepted_at": "2025-01-05T13:45:00Z",
  "profile_data": {
    "full_name": "Dr. Jennifer Martinez",
    "title": "Senior Business Navigator",
    "organization": "City of San Antonio SBAP",
    "phone": "+1-210-555-0321",
    "extension": "1001",
    "office_address": {
      "street": "100 Military Plaza",
      "city": "San Antonio", 
      "state": "TX",
      "zip": "78205",
      "country": "USA"
    },
    "certifications": ["Certified Business Advisor", "PTAC Procurement Counselor"],
    "years_experience": 12,
    "specializations": ["Procurement Readiness", "Small Business Development", "Contract Compliance"]
  },
  "navigator_metrics": {
    "agencies_managed": 5,
    "providers_approved": 34,
    "businesses_assisted": 278,
    "total_assessments_reviewed": 445,
    "avg_readiness_improvement": 38.7,
    "total_contract_value_facilitated": 5200000.00,
    "success_stories": 67
  },
  "responsibilities": {
    "regions": ["Bexar County", "Guadalupe County"],
    "agency_oversight": ["3e33ce75-d3ab-4fad-8101-f6a40b98b03d"],
    "provider_approval": true,
    "analytics_access": "full",
    "system_administration": false
  },
  "performance_targets": {
    "monthly_assessments": 40,
    "quarterly_certifications": 15,
    "annual_contract_value": 1500000.00,
    "business_success_rate": 85.0
  }
}
```

---

## Assessments Collection

The `assessment_sessions` collection stores assessment sessions with 8-area maturity evaluation, progress tracking, and gap identification.

### Sample Assessment Session Document
```json
{
  "_id": "sess_a7f3c2e8-4b91-4d5f-8e2a-1c9b0d7f6e5a",
  "session_id": "sess_a7f3c2e8-4b91-4d5f-8e2a-1c9b0d7f6e5a",
  "user_id": "7b425866-1819-49ce-9647-b10d47eab5bf",
  "status": "completed",
  "created_at": "2025-01-14T15:30:00Z",
  "updated_at": "2025-01-14T16:45:00Z", 
  "completed_at": "2025-01-14T16:45:00Z",
  "version": "8-area-v2.1",
  "progress": {
    "total_questions": 24,
    "answered_questions": 24,
    "completion_percentage": 100,
    "areas_completed": 8,
    "current_area": null,
    "time_spent_minutes": 42
  },
  "responses": {
    "q1_1": {
      "answer": "yes",
      "timestamp": "2025-01-14T15:32:15Z",
      "confidence_level": "high",
      "evidence_files": ["business_license_2025.pdf"],
      "notes": "Current business license valid until December 2025"
    },
    "q1_2": {
      "answer": "yes", 
      "timestamp": "2025-01-14T15:33:22Z",
      "confidence_level": "high",
      "evidence_files": ["state_registration.pdf", "city_permit.pdf"],
      "notes": "Registered with Texas Secretary of State and City of San Antonio"
    },
    "q1_3": {
      "answer": "no_need_help",
      "timestamp": "2025-01-14T15:34:45Z", 
      "confidence_level": "medium",
      "evidence_files": [],
      "notes": "Need to research appropriate coverage levels",
      "gap_identified": true,
      "resources_used": ["insurance_guide_area1.pdf"]
    },
    "q2_1": {
      "answer": "yes",
      "timestamp": "2025-01-14T15:37:12Z",
      "confidence_level": "high", 
      "evidence_files": ["quickbooks_setup.png"],
      "notes": "Using QuickBooks Pro with CPA oversight"
    },
    "q2_2": {
      "answer": "no_need_help",
      "timestamp": "2025-01-14T15:38:33Z",
      "confidence_level": "low",
      "evidence_files": [],
      "notes": "Records are current but not audit-ready format",
      "gap_identified": true,
      "resources_used": []
    }
  },
  "area_scores": {
    "area1": {
      "name": "Business Formation & Registration",
      "score": 66.7,
      "max_score": 100,
      "questions_answered": 3,
      "questions_total": 3,
      "gaps_identified": 1,
      "strength_level": "good",
      "priority": "medium"
    },
    "area2": {
      "name": "Financial Operations & Management", 
      "score": 33.3,
      "max_score": 100,
      "questions_answered": 3,
      "questions_total": 3, 
      "gaps_identified": 2,
      "strength_level": "needs_improvement",
      "priority": "high"
    },
    "area5": {
      "name": "Technology & Security Infrastructure",
      "score": 100,
      "max_score": 100,
      "questions_answered": 3,
      "questions_total": 3,
      "gaps_identified": 0,
      "strength_level": "excellent", 
      "priority": "low"
    }
  },
  "overall_metrics": {
    "overall_score": 75.5,
    "readiness_percentage": 75.5,
    "total_gaps": 3,
    "critical_gaps": 1,
    "medium_gaps": 2,
    "low_gaps": 0,
    "procurement_ready": false,
    "certification_eligible": false,
    "improvement_potential": 24.5
  },
  "gap_analysis": {
    "critical_areas": ["area2"],
    "improvement_areas": ["area1", "area4"],
    "strength_areas": ["area5", "area7"],
    "next_steps": [
      {
        "area_id": "area2",
        "priority": "high",
        "action": "Implement audit-ready financial record system",
        "estimated_effort": "2-3 weeks",
        "resources": ["financial_systems_guide.pdf"]
      },
      {
        "area_id": "area1", 
        "priority": "medium",
        "action": "Obtain comprehensive business insurance",
        "estimated_effort": "1 week",
        "resources": ["insurance_requirements.pdf"]
      }
    ]
  },
  "ai_insights": {
    "generated_at": "2025-01-14T16:45:00Z",
    "strengths_summary": "Strong technology infrastructure and performance tracking capabilities", 
    "weaknesses_summary": "Financial systems need audit-readiness improvements and insurance gaps",
    "recommendations": [
      "Focus on financial operations improvements for immediate procurement readiness gains",
      "Consider engaging with certified accounting provider for audit preparation",
      "Review insurance requirements for target contract types"
    ],
    "readiness_timeline": "4-6 weeks with focused improvements",
    "confidence_score": 0.87
  },
  "resource_usage": {
    "kb_articles_accessed": 5,
    "templates_downloaded": 3,
    "ai_explanations_requested": 7,
    "total_time_on_resources_minutes": 18
  },
  "session_metadata": {
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "device_type": "desktop",
    "browser": "Chrome 120.0",
    "session_quality": "complete",
    "interruptions": 0,
    "save_points": 8
  }
}
```

### Sample Assessment Progress Document (Incomplete Session)
```json
{
  "_id": "sess_b3d8e1f9-7c2a-4e6b-9f1d-5a8c3b2e7f4g",
  "session_id": "sess_b3d8e1f9-7c2a-4e6b-9f1d-5a8c3b2e7f4g",
  "user_id": "7b425866-1819-49ce-9647-b10d47eab5bf",
  "status": "in_progress",
  "created_at": "2025-01-15T10:15:00Z",
  "updated_at": "2025-01-15T10:32:00Z",
  "version": "8-area-v2.1", 
  "progress": {
    "total_questions": 24,
    "answered_questions": 8,
    "completion_percentage": 33.3,
    "areas_completed": 2,
    "current_area": "area3",
    "current_question": "q3_2",
    "time_spent_minutes": 17
  },
  "responses": {
    "q1_1": {
      "answer": "yes",
      "timestamp": "2025-01-15T10:16:30Z",
      "confidence_level": "high"
    },
    "q1_2": {
      "answer": "yes", 
      "timestamp": "2025-01-15T10:17:15Z",
      "confidence_level": "high"
    },
    "q1_3": {
      "answer": "yes",
      "timestamp": "2025-01-15T10:18:45Z",
      "confidence_level": "medium",
      "evidence_files": ["general_liability.pdf"]
    }
  },
  "area_scores": {
    "area1": {
      "name": "Business Formation & Registration",
      "score": 100,
      "max_score": 100,
      "questions_answered": 3,
      "questions_total": 3,
      "gaps_identified": 0,
      "strength_level": "excellent",
      "priority": "low"
    }
  },
  "session_metadata": {
    "last_activity": "2025-01-15T10:32:00Z",
    "auto_save_enabled": true,
    "bookmark_url": "/assessment?session=sess_b3d8e1f9-7c2a-4e6b-9f1d-5a8c3b2e7f4g&area=area3&question=q3_2",
    "estimated_completion_time": "35-40 minutes"
  }
}
```

---

## Service Requests Collection

The `service_requests` collection stores client requests for professional services with standardized data models, provider matching, and engagement tracking.

### Sample Active Service Request Document
```json
{
  "_id": "req_c4e9f2a1-8d3b-4f7c-9e6a-2b5d8f1c4a7e",
  "id": "req_c4e9f2a1-8d3b-4f7c-9e6a-2b5d8f1c4a7e",
  "request_id": "req_c4e9f2a1-8d3b-4f7c-9e6a-2b5d8f1c4a7e",
  "client_id": "7b425866-1819-49ce-9647-b10d47eab5bf",
  "user_id": "7b425866-1819-49ce-9647-b10d47eab5bf",
  "area_id": "area5",
  "area_name": "Technology & Security Infrastructure",
  "status": "active",
  "created_at": "2025-01-14T09:15:00Z",
  "updated_at": "2025-01-14T14:32:00Z",
  "data_version": "1.0",
  "request_details": {
    "title": "Cybersecurity Assessment and Implementation",
    "description": "Need comprehensive cybersecurity assessment for our small tech company preparing for government contracts. Require implementation of security frameworks, employee training, and compliance documentation.",
    "budget_range": "$5,000-$15,000",
    "timeline": "2-3 months", 
    "priority": "high",
    "urgency": "medium",
    "specific_requirements": [
      "SOC 2 Type II compliance preparation",
      "Employee cybersecurity training program", 
      "Incident response plan development",
      "Network security assessment",
      "Documentation for contract requirements"
    ],
    "deliverables_expected": [
      "Cybersecurity assessment report",
      "Implementation roadmap",
      "Policy and procedure documentation",
      "Training materials and sessions",
      "Compliance certification support"
    ],
    "current_capabilities": "Basic firewall and antivirus, Office 365 business premium, need significant improvements for government contracting"
  },
  "client_profile": {
    "business_name": "Tech Solutions LLC",
    "industry": "Technology Services",
    "employee_count": 8,
    "annual_revenue": "$250K-$500K", 
    "target_contracts": "Federal and state government technology services",
    "previous_experience": "Limited government contracting experience"
  },
  "matching_criteria": {
    "required_expertise": ["area5"],
    "preferred_certifications": ["CISSP", "CISA", "SOC 2"],
    "location_preference": "San Antonio metro or remote", 
    "provider_size": "small_to_medium",
    "experience_level": "advanced",
    "availability": "within_2_weeks"
  },
  "provider_responses": [
    {
      "response_id": "resp_d5f8a3b2-9e4c-4a7f-8d1e-6b9c2f5a8e1d",
      "provider_id": "66040b94-1323-45bb-867e-95c92785707a",
      "provider_name": "Enterprise Consulting Group",
      "proposed_fee": 12500.00,
      "currency": "USD", 
      "fee_formatted": "$12,500.00",
      "estimated_timeline": "6-8 weeks",
      "proposal_note": "Comprehensive cybersecurity program including SOC 2 preparation, policy development, employee training, and ongoing support. Our team has 8+ years in government contracting cybersecurity requirements.",
      "status": "submitted",
      "submitted_at": "2025-01-14T11:45:00Z",
      "provider_qualifications": {
        "certifications": ["CISSP", "CISA", "SOC 2 Auditor"],
        "years_experience": 8,
        "similar_projects": 23,
        "success_rate": 96.5,
        "client_references": ["reference1@client.com", "reference2@gov.agency"]
      },
      "proposal_breakdown": {
        "assessment_phase": "$3,500 (2 weeks)",
        "implementation_phase": "$7,000 (4 weeks)",
        "training_phase": "$1,500 (1 week)", 
        "documentation_phase": "$500 (ongoing)"
      }
    },
    {
      "response_id": "resp_e6g9b4c3-af5d-5b8g-9e2f-7c0d3g6b9f2e",
      "provider_id": "a1b2c3d4-e5f6-7g8h-9i0j-k1l2m3n4o5p6",
      "provider_name": "SecureGov Solutions",
      "proposed_fee": 9800.00,
      "currency": "USD",
      "fee_formatted": "$9,800.00", 
      "estimated_timeline": "4-6 weeks",
      "proposal_note": "Focused approach leveraging our government contracting expertise and SOC 2 templates. Efficient delivery with proven methodologies.",
      "status": "submitted",
      "submitted_at": "2025-01-14T14:20:00Z",
      "provider_qualifications": {
        "certifications": ["CISM", "SOC 2 Auditor"],
        "years_experience": 6,
        "similar_projects": 31,
        "success_rate": 94.2,
        "government_contracts": 15
      }
    }
  ],
  "notifications_sent": [
    {
      "provider_id": "66040b94-1323-45bb-867e-95c92785707a",
      "sent_at": "2025-01-14T09:20:00Z",
      "notification_type": "new_opportunity",
      "status": "delivered"
    },
    {
      "provider_id": "a1b2c3d4-e5f6-7g8h-9i0j-k1l2m3n4o5p6", 
      "sent_at": "2025-01-14T09:20:00Z",
      "notification_type": "new_opportunity",
      "status": "delivered"
    }
  ],
  "engagement_info": {
    "engagement_id": null,
    "selected_provider": null,
    "selection_date": null,
    "contract_signed": false,
    "work_started": false
  },
  "analytics": {
    "views": 127,
    "provider_interest": 8,
    "response_rate": 0.25,
    "time_to_first_response_hours": 2.5,
    "client_engagement_score": 0.85
  },
  "metadata": {
    "created_by": "7b425866-1819-49ce-9647-b10d47eab5bf",
    "source": "polaris_platform",
    "standardized": true,
    "validation_passed": true,
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0..."
  }
}
```

### Sample Completed Service Request Document
```json
{
  "_id": "req_f7a0d8e2-3b9c-4f6e-8a1d-5c2b7f0e3a6f",
  "id": "req_f7a0d8e2-3b9c-4f6e-8a1d-5c2b7f0e3a6f", 
  "request_id": "req_f7a0d8e2-3b9c-4f6e-8a1d-5c2b7f0e3a6f",
  "client_id": "7b425866-1819-49ce-9647-b10d47eab5bf",
  "user_id": "7b425866-1819-49ce-9647-b10d47eab5bf",
  "area_id": "area1",
  "area_name": "Business Formation & Registration",
  "status": "completed",
  "created_at": "2025-01-08T14:30:00Z",
  "updated_at": "2025-01-12T16:45:00Z",
  "completed_at": "2025-01-12T16:45:00Z",
  "data_version": "1.0",
  "request_details": {
    "title": "Business License and Registration Assistance", 
    "description": "Need help obtaining proper business licenses and completing registration requirements for technology services company in San Antonio.",
    "budget_range": "$1,000-$2,500",
    "timeline": "2-4 weeks",
    "priority": "medium",
    "urgency": "medium",
    "specific_requirements": [
      "Texas business registration",
      "City of San Antonio business license",
      "Professional services permits", 
      "Tax ID setup assistance"
    ]
  },
  "selected_provider": {
    "provider_id": "66040b94-1323-45bb-867e-95c92785707a",
    "provider_name": "Enterprise Consulting Group",
    "selected_at": "2025-01-09T10:15:00Z",
    "final_fee": 1800.00,
    "actual_timeline": "12 days",
    "contract_signed_at": "2025-01-09T15:30:00Z"
  },
  "engagement_summary": {
    "engagement_id": "eng_h8c1f9d3-4e7a-5f8b-9c2e-6d0a4g7c0f3h",
    "status": "completed",
    "work_started": "2025-01-10T09:00:00Z",
    "work_completed": "2025-01-12T16:45:00Z",
    "deliverables_provided": [
      "Texas Secretary of State registration certificate",
      "San Antonio business license (BL-2025-078423)",
      "Federal EIN confirmation",
      "Professional services permit documentation",
      "Compliance checklist and renewal calendar"
    ],
    "client_satisfaction": {
      "overall_rating": 5,
      "quality_rating": 5,
      "communication_rating": 5,
      "timeliness_rating": 5,
      "would_recommend": true,
      "feedback": "Excellent service, completed ahead of schedule with thorough documentation and follow-up support."
    }
  },
  "financial_summary": {
    "service_fee": 1800.00,
    "marketplace_fee": 90.00,
    "total_paid": 1890.00,
    "payment_date": "2025-01-09T16:00:00Z",
    "payment_method": "Stripe",
    "transaction_id": "pi_1O4P5Q6R7S8T9U0V1W2X"
  },
  "outcome_metrics": {
    "procurement_readiness_improvement": 15.5,
    "compliance_score": 98.5,
    "certificate_earned": false,
    "follow_up_services_recommended": ["area2", "area4"],
    "business_impact": "Enabled to bid on city contracts up to $50K value"
  }
}
```

---

## Data Relationships and Indexes

### Key Relationships
- **Users ↔ Assessment Sessions**: One-to-many (user_id)
- **Users ↔ Service Requests**: One-to-many (client_id/user_id)  
- **Service Requests ↔ Provider Responses**: One-to-many (request_id)
- **Service Requests ↔ Engagements**: One-to-one (request_id)

### Recommended Indexes
```javascript
// Users Collection
db.users.createIndex({ "email": 1 }, { unique: true })
db.users.createIndex({ "role": 1, "approval_status": 1 })
db.users.createIndex({ "license_code": 1 })
db.users.createIndex({ "created_at": -1 })

// Assessment Sessions Collection  
db.assessment_sessions.createIndex({ "user_id": 1, "created_at": -1 })
db.assessment_sessions.createIndex({ "status": 1 })
db.assessment_sessions.createIndex({ "overall_metrics.overall_score": -1 })

// Service Requests Collection
db.service_requests.createIndex({ "client_id": 1, "created_at": -1 })
db.service_requests.createIndex({ "area_id": 1, "status": 1 })
db.service_requests.createIndex({ "status": 1, "created_at": -1 })
db.service_requests.createIndex({ "provider_responses.provider_id": 1 })
```

---

## Data Standards Summary

All collections follow these standardization principles:
- **ID Format**: UUID4 strings for all identifiers
- **Timestamps**: ISO 8601 format in UTC
- **Currency**: USD with 2 decimal precision
- **Status Values**: Predefined enums for consistency
- **Text Fields**: Sanitized and length-validated
- **Nested Objects**: Structured for analytics and reporting
- **Versioning**: Data version tracking for schema evolution
- **Audit Trail**: Created/updated timestamps and user tracking