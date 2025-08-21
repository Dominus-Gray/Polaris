// Assessment Flow Improvements - Implementation Plan

/* ISSUES TO FIX:
1. Free resources should be external local resources (not platform hosted)
2. Professional help maturity statement should show "pending" 
3. Continue Assessment button text not visible
4. Start AI Consultation button text not visible and needs centering
5. View All Resources should navigate to area-specific templates
6. Knowledge Base deliverables needed for each business area
7. Replace notification icon
8. Remove "describe your services" from business profile
9. Lock AI assistant behind paywall
10. Make AI responses more concise
11. Fix AI-generated template content
*/

// External Local Resources by Business Area
const EXTERNAL_LOCAL_RESOURCES = {
  area1: { // Business Formation & Registration
    name: "Business Formation & Registration",
    resources: [
      {
        title: "Texas Secretary of State - Business Registration",
        url: "https://www.sos.state.tx.us/corp/index.shtml",
        description: "Official state portal for business entity formation and registration",
        type: "Government",
        location: "Texas Statewide"
      },
      {
        title: "City of San Antonio Business License Portal", 
        url: "https://www.sanantonio.gov/Development-Services/Business-Licenses",
        description: "Local business license applications and permits",
        type: "Municipal",
        location: "San Antonio, TX"
      },
      {
        title: "Small Business Administration (SBA) - Business Guide",
        url: "https://www.sba.gov/business-guide/10-steps-start-your-business",
        description: "Comprehensive 10-step business startup guide",
        type: "Federal",
        location: "National"
      },
      {
        title: "SCORE San Antonio - Free Business Mentoring",
        url: "https://sanantonio.score.org/",
        description: "Free business mentoring and workshops for entrepreneurs",
        type: "Nonprofit",
        location: "San Antonio, TX"
      },
      {
        title: "San Antonio SBDC - Business Counseling",
        url: "https://www.utsa.edu/business/sbdc/",
        description: "Free business counseling and training programs",
        type: "Educational",
        location: "San Antonio, TX"
      }
    ]
  },
  
  area2: { // Financial Operations & Management
    name: "Financial Operations & Management",
    resources: [
      {
        title: "IRS Small Business Tax Center",
        url: "https://www.irs.gov/businesses/small-businesses-self-employed",
        description: "Tax information and resources for small businesses",
        type: "Federal",
        location: "National"
      },
      {
        title: "San Antonio Economic Development - Financial Resources",
        url: "https://www.sanantonio.gov/economic-development/BusinessResources",
        description: "Local financial assistance and loan programs",
        type: "Municipal", 
        location: "San Antonio, TX"
      },
      {
        title: "UTSA SBDC - Financial Management Training",
        url: "https://www.utsa.edu/business/sbdc/services/training/",
        description: "Free workshops on financial management and accounting",
        type: "Educational",
        location: "San Antonio, TX"
      },
      {
        title: "Texas State Small Business Credit Initiative",
        url: "https://www.texassbci.org/",
        description: "State-backed loan programs for small businesses",
        type: "State",
        location: "Texas Statewide"
      },
      {
        title: "Women's Business Center of South Texas",
        url: "https://www.wbcst.org/",
        description: "Financial literacy and business counseling services",
        type: "Nonprofit",
        location: "San Antonio, TX"
      }
    ]
  },
  
  area3: { // Legal & Contracting Compliance
    name: "Legal & Contracting Compliance", 
    resources: [
      {
        title: "Texas State Bar - LegalLine",
        url: "https://www.texasbar.com/legalline",
        description: "Free legal advice hotline for qualifying businesses",
        type: "Professional",
        location: "Texas Statewide"
      },
      {
        title: "San Antonio Bar Association - Pro Bono Legal Services",
        url: "https://www.sabar.org/",
        description: "Reduced-cost legal services for small businesses",
        type: "Professional",
        location: "San Antonio, TX"
      },
      {
        title: "SBA Contracting - Certification Programs",
        url: "https://www.sba.gov/federal-contracting/contracting-assistance-programs",
        description: "Federal contracting certification assistance",
        type: "Federal",
        location: "National"
      },
      {
        title: "PTAC Texas - Procurement Technical Assistance",
        url: "https://www.texasptac.org/",
        description: "Free government contracting assistance and training",
        type: "Nonprofit",
        location: "Texas Statewide"
      },
      {
        title: "City of San Antonio Vendor Registration",
        url: "https://www.sanantonio.gov/Purchasing/VendorInformation",
        description: "Register to do business with the City of San Antonio",
        type: "Municipal",
        location: "San Antonio, TX"
      }
    ]
  },
  
  area4: { // Quality Management & Standards
    name: "Quality Management & Standards",
    resources: [
      {
        title: "Texas Manufacturing Assistance Center (TMAC)",
        url: "https://www.tmac.org/",
        description: "Free manufacturing and quality system consulting",
        type: "Nonprofit",
        location: "Texas Statewide"
      },
      {
        title: "ISO 9001 Training - San Antonio College",
        url: "https://www.alamo.edu/sac/academics/workforce-development/",
        description: "Quality management system training and certification",
        type: "Educational", 
        location: "San Antonio, TX"
      },
      {
        title: "Better Business Bureau South Central Texas",
        url: "https://www.bbb.org/south-central-texas",
        description: "Business accreditation and reputation management",
        type: "Nonprofit",
        location: "San Antonio, TX"
      },
      {
        title: "NIST Manufacturing Extension Partnership",
        url: "https://www.nist.gov/mep",
        description: "Manufacturing process improvement and quality systems",
        type: "Federal",
        location: "National"
      },
      {
        title: "Texas Economic Development Corporation - Quality Programs",
        url: "https://gov.texas.gov/business/page/texas-economic-development",
        description: "State quality and certification assistance programs",
        type: "State", 
        location: "Texas Statewide"
      }
    ]
  },
  
  area5: { // Technology & Security Infrastructure
    name: "Technology & Security Infrastructure",
    resources: [
      {
        title: "CISA Cybersecurity Resources for Small Business",
        url: "https://www.cisa.gov/cybersecurity-small-and-medium-businesses",
        description: "Federal cybersecurity guidance and tools",
        type: "Federal",
        location: "National"
      },
      {
        title: "San Antonio CyberSecurity Framework Initiative",
        url: "https://www.sanantonio.gov/ITServices/Security",
        description: "Local cybersecurity resources and training",
        type: "Municipal",
        location: "San Antonio, TX"
      },
      {
        title: "Texas A&M Cybersecurity Center - Small Business Program",
        url: "https://cybersecurity.tamu.edu/",
        description: "Cybersecurity training and assessment services",
        type: "Educational",
        location: "Texas Statewide"
      },
      {
        title: "SCORE - Technology and Digital Marketing Workshops", 
        url: "https://sanantonio.score.org/content/technology-workshops",
        description: "Free technology training for small businesses",
        type: "Nonprofit",
        location: "San Antonio, TX"
      },
      {
        title: "TechBloc San Antonio - Technology Resources",
        url: "https://techbloc.org/",
        description: "Local tech community resources and networking",
        type: "Nonprofit",
        location: "San Antonio, TX"
      }
    ]
  },
  
  area6: { // Human Resources & Capacity
    name: "Human Resources & Capacity",
    resources: [
      {
        title: "Texas Workforce Commission - Employer Services",
        url: "https://www.twc.texas.gov/employers",
        description: "Employment services, training grants, and HR resources",
        type: "State",
        location: "Texas Statewide"
      },
      {
        title: "Department of Labor - Small Business Resources",
        url: "https://www.dol.gov/agencies/whd/small-business",
        description: "Federal employment law guidance for small businesses",
        type: "Federal",
        location: "National"
      },
      {
        title: "San Antonio WorkForce Development - Business Services",
        url: "https://www.workforcesolutionsalamo.org/employers/",
        description: "Local workforce development and training services",
        type: "Local",
        location: "San Antonio, TX"
      },
      {
        title: "SHRM San Antonio - HR Resources",
        url: "https://sanantonio.shrm.org/",
        description: "Professional HR development and compliance resources",
        type: "Professional",
        location: "San Antonio, TX"
      },
      {
        title: "UTSA SBDC - Human Resources Training",
        url: "https://www.utsa.edu/business/sbdc/services/training/human-resources/", 
        description: "Free HR management and compliance workshops",
        type: "Educational",
        location: "San Antonio, TX"
      }
    ]
  },
  
  area7: { // Performance Tracking & Reporting
    name: "Performance Tracking & Reporting",
    resources: [
      {
        title: "SBA Learning Center - Performance Management",
        url: "https://www.sba.gov/learning-center/",
        description: "Business performance measurement and improvement courses",
        type: "Federal",
        location: "National"
      },
      {
        title: "UTSA SBDC - Financial Analysis and Reporting",
        url: "https://www.utsa.edu/business/sbdc/services/counseling/",
        description: "Free business analysis and performance tracking counseling",
        type: "Educational",
        location: "San Antonio, TX"
      },
      {
        title: "SCORE - Business Performance Mentoring",
        url: "https://sanantonio.score.org/content/business-operations-performance",
        description: "One-on-one mentoring for performance improvement",
        type: "Nonprofit", 
        location: "San Antonio, TX"
      },
      {
        title: "Texas Economic Development - Business Analytics",
        url: "https://gov.texas.gov/business/page/business-resources",
        description: "State resources for business performance measurement",
        type: "State",
        location: "Texas Statewide"
      },
      {
        title: "San Antonio Hispanic Chamber - Performance Excellence Program",
        url: "https://sahcc.org/",
        description: "Business performance coaching and networking",
        type: "Chamber",
        location: "San Antonio, TX"
      }
    ]
  },
  
  area8: { // Risk Management & Business Continuity
    name: "Risk Management & Business Continuity",
    resources: [
      {
        title: "FEMA Business Emergency Planning",
        url: "https://www.ready.gov/business",
        description: "Federal emergency preparedness resources for businesses",
        type: "Federal",
        location: "National"
      },
      {
        title: "Texas Division of Emergency Management - Business Continuity",
        url: "https://tdem.texas.gov/business/",
        description: "State emergency management and continuity planning",
        type: "State",
        location: "Texas Statewide"
      },
      {
        title: "San Antonio Office of Emergency Management",
        url: "https://www.sanantonio.gov/OEM/",
        description: "Local emergency preparedness and business resilience",
        type: "Municipal",
        location: "San Antonio, TX"
      },
      {
        title: "SBA Disaster Assistance - Business Resilience",
        url: "https://www.sba.gov/funding-programs/disaster-assistance",
        description: "Disaster preparedness and recovery resources",
        type: "Federal",
        location: "National"
      },
      {
        title: "Texas Association of Business - Risk Management",
        url: "https://www.txbiz.org/",
        description: "Business risk management resources and advocacy",
        type: "Association",
        location: "Texas Statewide"  
      }
    ]
  }
};

// Knowledge Base Deliverables for Each Area
const KNOWLEDGE_BASE_DELIVERABLES = {
  area1: {
    templates: [
      "Business License Application Checklist",
      "Corporate Structure Decision Matrix",
      "Business Registration Timeline Template",
      "Permit and License Tracking Spreadsheet"
    ],
    guides: [
      "Complete Guide to Texas Business Formation", 
      "San Antonio Business License Requirements",
      "Federal Tax ID and Registration Process",
      "Professional License Requirements Guide"
    ],
    bestPractices: [
      "Choosing the Right Business Structure",
      "Maintaining Good Standing with State Agencies",
      "Annual Filing and Renewal Requirements",
      "Business Name and Trademark Protection"
    ]
  },
  
  area2: {
    templates: [
      "Financial Forecast and Budget Template",
      "Cash Flow Projection Spreadsheet", 
      "Expense Tracking and Categorization System",
      "Financial Controls and Procedures Checklist"
    ],
    guides: [
      "Small Business Accounting Best Practices",
      "Understanding Financial Statements",
      "Tax Planning and Compliance Guide", 
      "Business Banking and Credit Management"
    ],
    bestPractices: [
      "Monthly Financial Review Process",
      "Separating Business and Personal Finances",
      "Preparing for Tax Season",
      "Building Business Credit"
    ]
  },
  
  area3: {
    templates: [
      "Standard Service Agreement Template",
      "Government Contract Compliance Checklist",
      "Legal Document Review Process",
      "Contract Risk Assessment Matrix"
    ],
    guides: [
      "Understanding Government Contracting Requirements",
      "Intellectual Property Protection for Small Business",
      "Employment Law Compliance Guide",
      "Contract Negotiation Strategies"
    ],
    bestPractices: [
      "Due Diligence in Contract Review",
      "Maintaining Legal Compliance",
      "Working with Legal Counsel Effectively",
      "Document Retention and Management"
    ]
  },
  
  area4: {
    templates: [
      "Quality Management System Framework",
      "Process Documentation Templates", 
      "Customer Feedback Collection System",
      "Quality Metrics Dashboard Template"
    ],
    guides: [
      "ISO 9001 Implementation Guide for Small Business",
      "Quality Control Process Development",
      "Customer Satisfaction Measurement",
      "Continuous Improvement Methodologies"
    ],
    bestPractices: [
      "Building a Quality Culture",
      "Document Control and Version Management", 
      "Training and Competency Management",
      "Quality Audit and Review Processes"
    ]
  },
  
  area5: {
    templates: [
      "Cybersecurity Policy Template",
      "Technology Asset Inventory Spreadsheet",
      "Incident Response Plan Template",
      "Data Backup and Recovery Checklist"
    ],
    guides: [
      "Small Business Cybersecurity Framework",
      "NIST Cybersecurity Implementation Guide",
      "Cloud Security Best Practices",
      "Employee Security Training Program"
    ],
    bestPractices: [
      "Multi-Factor Authentication Implementation",
      "Regular Security Assessment Process",
      "Vendor Security Due Diligence",
      "Business Continuity Technology Planning"
    ]
  },
  
  area6: {
    templates: [
      "Employee Handbook Template",
      "Job Description and Requirements Framework",
      "Performance Review Process Template",
      "Training and Development Plan"
    ],
    guides: [
      "Employment Law Compliance for Small Business",
      "Recruitment and Hiring Best Practices", 
      "Employee Performance Management",
      "Workplace Safety and Health Requirements"
    ],
    bestPractices: [
      "Creating an Inclusive Workplace Culture",
      "Effective Communication and Feedback",
      "Professional Development Planning",
      "Managing Remote and Hybrid Teams"
    ]
  },
  
  area7: {
    templates: [
      "Key Performance Indicators (KPI) Dashboard",
      "Project Status Report Template",
      "Financial Performance Tracking Spreadsheet",
      "Client Deliverable Checklist"
    ],
    guides: [
      "Performance Measurement Framework Development",
      "Project Management for Small Business",
      "Client Reporting and Communication",
      "Data Analysis and Business Intelligence"
    ],
    bestPractices: [
      "Regular Performance Review Cycles",
      "Transparent Client Communication",
      "Proactive Issue Identification and Resolution",
      "Continuous Improvement Integration"
    ]
  },
  
  area8: {
    templates: [
      "Business Continuity Plan Template",
      "Risk Assessment Matrix",
      "Emergency Contact and Procedures List",
      "Insurance Coverage Review Checklist"
    ],
    guides: [
      "Business Risk Management Framework",
      "Emergency Preparedness Planning",
      "Insurance Requirements for Government Contracting",
      "Crisis Communication Planning"
    ],
    bestPractices: [
      "Regular Risk Assessment and Review",
      "Building Organizational Resilience",
      "Supplier and Vendor Risk Management",
      "Recovery and Lessons Learned Process"
    ]
  }
};

module.exports = {
  EXTERNAL_LOCAL_RESOURCES,
  KNOWLEDGE_BASE_DELIVERABLES
};