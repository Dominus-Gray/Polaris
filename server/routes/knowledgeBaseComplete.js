const express = require('express')
const axios = require('axios')
const { v4: uuidv4 } = require('uuid')
const { authenticateToken } = require('../middleware/auth')
const { formatResponse, formatErrorResponse } = require('../utils/helpers')
const logger = require('../utils/logger').logger

const router = express.Router()

/**
 * GET /api/knowledge-base/areas
 * Get all knowledge base areas
 */
router.get('/areas', authenticateToken, async (req, res, next) => {
  try {
    const areas = [
      {
        area_id: 'area1',
        area_name: 'Business Formation & Registration',
        description: 'Legal structure, registration, licenses, and permits',
        is_locked: false,
        resource_count: 12,
        templates_available: 3
      },
      {
        area_id: 'area2',
        area_name: 'Financial Operations & Management',
        description: 'Financial planning, accounting, and cash flow management',
        is_locked: false,
        resource_count: 18,
        templates_available: 5
      },
      {
        area_id: 'area3',
        area_name: 'Legal & Contracting Compliance',
        description: 'Legal requirements, contracts, and compliance standards',
        is_locked: false,
        resource_count: 15,
        templates_available: 4
      },
      {
        area_id: 'area4',
        area_name: 'Quality Management & Standards',
        description: 'Quality systems, certifications, and process standards',
        is_locked: false,
        resource_count: 10,
        templates_available: 3
      },
      {
        area_id: 'area5',
        area_name: 'Technology & Security Infrastructure',
        description: 'IT systems, cybersecurity, and data management',
        is_locked: !req.user.email?.includes('@polaris.example.com'),
        resource_count: 15,
        templates_available: 4
      },
      {
        area_id: 'area6',
        area_name: 'Human Resources & Capacity',
        description: 'Staffing, training, and organizational capacity',
        is_locked: false,
        resource_count: 8,
        templates_available: 2
      },
      {
        area_id: 'area7',
        area_name: 'Performance Tracking & Reporting',
        description: 'Metrics, reporting systems, and performance management',
        is_locked: false,
        resource_count: 12,
        templates_available: 3
      },
      {
        area_id: 'area8',
        area_name: 'Risk Management & Business Continuity',
        description: 'Risk assessment, mitigation, and business continuity planning',
        is_locked: false,
        resource_count: 9,
        templates_available: 2
      },
      {
        area_id: 'area9',
        area_name: 'Supply Chain Management & Vendor Relations',
        description: 'Supplier relationships, procurement, and supply chain optimization',
        is_locked: false,
        resource_count: 11,
        templates_available: 3
      },
      {
        area_id: 'area10',
        area_name: 'Competitive Advantage & Market Position',
        description: 'Competitive advantages, market capture processes, strategic partnerships',
        is_locked: false,
        resource_count: 7,
        templates_available: 2
      }
    ]

    res.json({
      success: true,
      data: areas
    })

  } catch (error) {
    logger.error('Get knowledge base areas error:', error)
    next(error)
  }
})

/**
 * POST /api/knowledge-base/ai-assistance
 * Get AI-powered assistance with real OpenAI integration
 */
router.post('/ai-assistance', authenticateToken, async (req, res, next) => {
  try {
    const { question, context } = req.body
    const userId = req.user.id

    if (!question || question.trim().length === 0) {
      return res.status(400).json(
        formatErrorResponse('POL-4001', 'Question is required')
      )
    }

    // Check if user has access (paywall protection for non-QA users)
    if (!req.user.email?.includes('@polaris.example.com')) {
      return res.json({
        success: true,
        data: {
          response: "Thank you for your question. To access AI-powered assistance and get personalized guidance, please upgrade your account or contact your local agency partner. Our Knowledge Base articles and templates are available for your reference.",
          is_premium_feature: true,
          upgrade_required: true
        }
      })
    }

    try {
      // Real OpenAI integration
      const apiKey = process.env.EMERGENT_LLM_KEY
      
      if (!apiKey) {
        throw new Error('EMERGENT_LLM_KEY not configured')
      }

      const systemMessage = `You are a professional business compliance and procurement readiness AI assistant for the Polaris platform.

EXPERTISE: You help small businesses with:
- Business formation and registration requirements
- Financial operations and compliance
- Legal and contracting requirements  
- Quality management systems
- Technology and security infrastructure
- Human resources and capacity building
- Performance tracking and reporting
- Risk management and business continuity
- Supply chain and vendor relations
- Competitive advantage and market positioning

CONTEXT: ${context?.area_id ? `User is asking about ${context.area_id}` : 'General business question'}

RESPONSE STYLE:
- Provide actionable, specific advice (under 250 words)
- Use numbered steps for complex processes
- Reference relevant business areas when applicable
- Suggest next steps and resources
- Maintain a professional, supportive tone
- Focus on procurement readiness requirements`

      const messages = [
        { role: 'system', content: systemMessage },
        { role: 'user', content: question }
      ]

      const response = await axios.post('https://api.openai.com/v1/chat/completions', {
        model: 'gpt-4o-mini',
        messages: messages,
        max_tokens: 400,
        temperature: 0.7
      }, {
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json'
        }
      })

      const aiResponse = response.data.choices[0].message.content

      logger.info(`AI assistance provided for user ${userId}`)

      res.json({
        success: true,
        data: {
          response: aiResponse,
          context_used: context || {},
          generated_at: new Date().toISOString(),
          model: 'gpt-4o-mini',
          provider: 'openai'
        }
      })

    } catch (aiError) {
      logger.error('OpenAI API error:', aiError.response?.data || aiError.message)
      
      // Fallback response
      res.json({
        success: true,
        data: {
          response: `Thank you for your question about "${question}". I'm here to help with procurement readiness and business compliance. For this topic, I recommend reviewing our knowledge base resources and connecting with a qualified service provider for personalized guidance.`,
          fallback: true,
          generated_at: new Date().toISOString()
        }
      })
    }

  } catch (error) {
    logger.error('AI assistance error:', error)
    next(error)
  }
})

/**
 * GET /api/knowledge-base/generate-template/:area_id/:template_type
 * Generate downloadable templates
 */
router.get('/generate-template/:area_id/:template_type', authenticateToken, async (req, res, next) => {
  try {
    const { area_id, template_type } = req.params

    const areaNames = {
      'area1': 'Business Formation & Registration',
      'area2': 'Financial Operations & Management',
      'area3': 'Legal & Contracting Compliance',
      'area4': 'Quality Management & Standards',
      'area5': 'Technology & Security Infrastructure',
      'area6': 'Human Resources & Capacity',
      'area7': 'Performance Tracking & Reporting',
      'area8': 'Risk Management & Business Continuity',
      'area9': 'Supply Chain Management & Vendor Relations',
      'area10': 'Competitive Advantage & Market Position'
    }

    const areaName = areaNames[area_id] || 'Business Area'

    // Generate comprehensive template content
    const templateContent = `# ${areaName.toUpperCase()} ${template_type.toUpperCase()} - POLARIS FRAMEWORK

## Procurement Readiness Assessment & Implementation Guide
### ${areaName}

**Generated on:** ${new Date().toLocaleDateString()}
**Framework Version:** Polaris 2025

---

## EXECUTIVE SUMMARY

This ${template_type} provides comprehensive guidance for achieving procurement readiness in ${areaName}. Use this framework to systematically evaluate and improve your business capabilities.

## TIER-BASED ASSESSMENT FRAMEWORK

### TIER 1 - FOUNDATIONAL COMPLIANCE (3 Requirements)
**Self-Assessment Level - Basic Business Readiness**

#### Requirement 1: Core Infrastructure
- [ ] Establish fundamental business processes
- [ ] Document basic operational procedures
- [ ] Implement minimum compliance standards

#### Requirement 2: Basic Documentation
- [ ] Create essential business documentation
- [ ] Maintain required record-keeping systems
- [ ] Establish basic reporting mechanisms

#### Requirement 3: Compliance Foundation
- [ ] Meet fundamental regulatory requirements
- [ ] Implement basic quality controls
- [ ] Establish accountability measures

### TIER 2 - ENHANCED COMPLIANCE (6 Requirements)
**Evidence Required Level - Intermediate Business Assurance**

*Includes all Tier 1 requirements plus:*

#### Requirement 4: Advanced Processes
- [ ] Develop intermediate capability systems
- [ ] Create detailed process documentation
- [ ] Implement monitoring and control systems
- **Evidence Required:** Process documentation, training records

#### Requirement 5: System Integration
- [ ] Establish integrated business systems
- [ ] Implement cross-functional workflows
- [ ] Create performance measurement systems
- **Evidence Required:** System documentation, integration proof

#### Requirement 6: Continuous Improvement
- [ ] Develop improvement identification processes
- [ ] Implement feedback and correction systems
- [ ] Establish regular review mechanisms
- **Evidence Required:** Improvement records, review documentation

### TIER 3 - VERIFICATION LEVEL (9 Requirements)
**Navigator Validation Level - High Effort Business Assurance**

*Includes all Tier 1 and Tier 2 requirements plus:*

#### Requirement 7: Industry Best Practices
- [ ] Achieve industry-leading standards
- [ ] Implement advanced quality systems
- [ ] Establish competitive advantages
- **Evidence Required:** Certifications, benchmarking data, third-party validation

#### Requirement 8: Strategic Excellence
- [ ] Develop strategic planning capabilities
- [ ] Implement advanced analytics and forecasting
- [ ] Establish thought leadership positioning
- **Evidence Required:** Strategic plans, analytics reports, industry recognition

#### Requirement 9: Ecosystem Leadership
- [ ] Build strategic partnerships and alliances
- [ ] Contribute to industry standards development
- [ ] Mentor other businesses in the ecosystem
- **Evidence Required:** Partnership agreements, industry contributions, mentorship records

## IMPLEMENTATION ROADMAP

### Phase 1: Foundation (Weeks 1-4)
1. **Assessment Completion**
   - Complete Polaris tier-based assessment for ${areaName}
   - Identify current capability gaps and strengths
   - Prioritize improvement areas based on procurement requirements

2. **Gap Analysis**
   - Document specific deficiencies
   - Estimate remediation timelines and resources
   - Develop action plan for addressing gaps

### Phase 2: Development (Weeks 5-12)
1. **Capability Building**
   - Address critical gaps identified in assessment
   - Implement required processes and systems
   - Create supporting documentation and evidence

2. **Evidence Preparation**
   - Gather supporting documentation for compliance claims
   - Prepare evidence packages for navigator review
   - Ensure all documentation meets verification standards

### Phase 3: Validation (Weeks 13-16)
1. **Navigator Review**
   - Submit evidence packages to digital navigators
   - Address any remediation requirements promptly
   - Achieve validated compliance certification

2. **Ecosystem Integration**
   - Connect with local agency partner for ongoing support
   - Join procurement-ready business network
   - Access procurement opportunities and partnerships

## RESOURCES & SUPPORT SYSTEMS

### Polaris Platform Resources
- **AI Assistant:** Real-time guidance and question answering
- **Knowledge Base:** Comprehensive resource library and templates
- **Service Marketplace:** Connect with qualified improvement specialists
- **Progress Tracking:** Monitor advancement through assessment tiers

### External Resources
- **SBA Resources:** Small Business Administration guidance and support
- **APEX Accelerators:** Procurement technical assistance programs
- **Local EDCs:** Economic development corporation partnerships
- **Industry Associations:** Sector-specific guidance and networking

### Professional Services Available
Through the Polaris platform, connect with verified specialists in:
- Business formation and legal structure optimization
- Financial systems implementation and compliance
- Quality management and certification assistance
- Technology infrastructure and security enhancement
- Strategic planning and competitive positioning

## SUCCESS METRICS & VALIDATION

### Tier 1 Success Indicators
- [ ] All foundational requirements documented and implemented
- [ ] Basic compliance standards achieved
- [ ] Fundamental business processes operational

### Tier 2 Success Indicators  
- [ ] Evidence packages approved by navigator review
- [ ] Advanced systems functional and documented
- [ ] Intermediate compliance standards achieved

### Tier 3 Success Indicators
- [ ] Industry best practices implemented and validated
- [ ] Strategic competitive advantages established
- [ ] Procurement readiness certification achieved

## NEXT STEPS

1. **Complete Assessment:** Use this framework to guide your Polaris assessment
2. **Gap Remediation:** Address identified deficiencies systematically
3. **Evidence Gathering:** Prepare comprehensive documentation packages
4. **Navigator Validation:** Submit for professional review and certification
5. **Ecosystem Integration:** Join your local procurement-ready business network

---

**Generated by Polaris Platform - Procurement Readiness Made Simple**
**${areaName} Assessment Framework**

For additional support:
- Access the Polaris AI Assistant for specific questions
- Connect with local service providers through the marketplace
- Contact your agency partner for guidance and support
- Download additional templates and resources from the knowledge base

**Framework ID:** polaris-${area_id}-${template_type}-${Date.now()}
`

    res.json({
      success: true,
      data: {
        content: templateContent,
        filename: `polaris_${area_id}_${template_type}_framework.md`,
        content_type: 'text/markdown'
      }
    })

  } catch (error) {
    logger.error('Template generation error:', error)
    next(error)
  }
})

module.exports = router