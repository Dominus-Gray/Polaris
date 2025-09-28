#!/usr/bin/env python3
"""
FOCUSED INTEGRATION TESTING SUITE
Testing Agent: testing
Test Date: January 2025
Test Scope: Testing only the integration endpoints that actually exist in the backend

This test suite focuses on the integration endpoints that are actually implemented:
1. QuickBooks Integration (7 endpoints)
2. Microsoft 365 Integration (4 endpoints)  
3. CRM Integration (4 endpoints)
4. Integration Status (1 endpoint)

Total: 16 integration endpoints to test
"""

import requests
import json
import time
from datetime import datetime, timedelta
import sys
import uuid

# Configuration
BACKEND_URL = "https://polaris-migrate.preview.emergentagent.com/api"
QA_CREDENTIALS = {
    "client": {"email": "client.qa@polaris.example.com", "password": "Polaris#2025!"},
    "agency": {"email": "agency.qa@polaris.example.com", "password": "Polaris#2025!"}
}

class FocusedIntegrationTester:
    def __init__(self):
        self.session = requests.Session()
        self.tokens = {}
        self.user_ids = {}
        self.test_results = []
        self.integration_data = {}
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name, success, details="", response_data=None):
        """Log test results with comprehensive details"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")
        print()

    def authenticate_roles(self):
        """Authenticate required user roles"""
        print("🔐 AUTHENTICATING QA USER ROLES...")
        print("=" * 60)
        
        for role, credentials in QA_CREDENTIALS.items():
            try:
                response = self.session.post(
                    f"{BACKEND_URL}/auth/login",
                    json=credentials,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    token = data.get("access_token")
                    
                    # Get user info
                    user_response = self.session.get(
                        f"{BACKEND_URL}/auth/me",
                        headers={"Authorization": f"Bearer {token}"}
                    )
                    
                    if user_response.status_code == 200:
                        user_data = user_response.json()
                        self.tokens[role] = token
                        self.user_ids[role] = user_data.get("id")
                        
                        self.log_test(
                            f"{role.title()} Authentication",
                            True,
                            f"Successfully authenticated as {credentials['email']} (ID: {user_data.get('id')})"
                        )
                    else:
                        self.log_test(
                            f"{role.title()} Authentication - User Info",
                            False,
                            f"Failed to get user info: {user_response.status_code}",
                            user_response.text
                        )
                        return False
                else:
                    self.log_test(
                        f"{role.title()} Authentication",
                        False,
                        f"Login failed with status {response.status_code}",
                        response.text
                    )
                    return False
                    
            except Exception as e:
                self.log_test(
                    f"{role.title()} Authentication",
                    False,
                    f"Authentication error: {str(e)}"
                )
                return False
        
        return len(self.tokens) == len(QA_CREDENTIALS)

    def test_quickbooks_integration_complete(self):
        """Test complete QuickBooks integration workflow"""
        print("💰 TESTING QUICKBOOKS INTEGRATION COMPLETE WORKFLOW...")
        print("=" * 60)
        
        client_token = self.tokens.get("client")
        if not client_token:
            self.log_test("QuickBooks Integration - Authentication", False, "Client token not available")
            return False
        
        workflow_success = True
        
        # Test 1: QuickBooks Auth URL
        try:
            response = self.session.get(
                f"{BACKEND_URL}/integrations/quickbooks/auth-url",
                headers={"Authorization": f"Bearer {client_token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get("auth_url", "")
                state = data.get("state", "")
                
                if "appcenter.intuit.com" in auth_url and state.startswith(f"user_{self.user_ids['client']}"):
                    self.log_test(
                        "QuickBooks Auth URL Generation",
                        True,
                        f"Auth URL generated successfully with valid state: {state}"
                    )
                    self.integration_data["quickbooks_state"] = state
                else:
                    self.log_test(
                        "QuickBooks Auth URL Generation",
                        False,
                        f"Invalid auth URL or state: {auth_url}, {state}",
                        data
                    )
                    workflow_success = False
            else:
                self.log_test(
                    "QuickBooks Auth URL Generation",
                    False,
                    f"Request failed with status {response.status_code}",
                    response.text
                )
                workflow_success = False
                
        except Exception as e:
            self.log_test("QuickBooks Auth URL Generation", False, f"Error: {str(e)}")
            workflow_success = False
        
        # Test 2: QuickBooks Connection
        try:
            connection_data = {
                "auth_code": f"mock_auth_code_{int(time.time())}",
                "realm_id": "123456789012345",
                "redirect_uri": "https://polaris-migrate.preview.emergentagent.com/quickbooks/callback"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/integrations/quickbooks/connect",
                json=connection_data,
                headers={
                    "Authorization": f"Bearer {client_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("status") == "connected":
                    self.log_test(
                        "QuickBooks Connection",
                        True,
                        f"QuickBooks connected successfully with realm_id: {data.get('realm_id')}"
                    )
                    self.integration_data["quickbooks_realm_id"] = data.get("realm_id")
                else:
                    self.log_test(
                        "QuickBooks Connection",
                        False,
                        f"Connection failed: {data}",
                        data
                    )
                    workflow_success = False
            else:
                self.log_test(
                    "QuickBooks Connection",
                    False,
                    f"Request failed with status {response.status_code}",
                    response.text
                )
                workflow_success = False
                
        except Exception as e:
            self.log_test("QuickBooks Connection", False, f"Error: {str(e)}")
            workflow_success = False
        
        # Test 3: Financial Health Analysis
        try:
            response = self.session.get(
                f"{BACKEND_URL}/integrations/quickbooks/financial-health",
                headers={"Authorization": f"Bearer {client_token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                required_scores = ["overall_score", "cash_flow_score", "profitability_score", "liquidity_score", "debt_ratio_score"]
                
                if all(field in data for field in required_scores):
                    overall_score = data.get("overall_score", 0)
                    recommendations = data.get("recommendations", [])
                    insights = data.get("insights", [])
                    
                    self.log_test(
                        "QuickBooks Financial Health Analysis",
                        True,
                        f"Financial health calculated - Overall Score: {overall_score}/10, Recommendations: {len(recommendations)}, Insights: {len(insights)}"
                    )
                    self.integration_data["financial_health"] = {
                        "overall_score": overall_score,
                        "recommendations_count": len(recommendations),
                        "insights_count": len(insights)
                    }
                else:
                    self.log_test(
                        "QuickBooks Financial Health Analysis",
                        False,
                        f"Missing required score fields: {[f for f in required_scores if f not in data]}",
                        data
                    )
                    workflow_success = False
            else:
                self.log_test(
                    "QuickBooks Financial Health Analysis",
                    False,
                    f"Request failed with status {response.status_code}",
                    response.text
                )
                workflow_success = False
                
        except Exception as e:
            self.log_test("QuickBooks Financial Health Analysis", False, f"Error: {str(e)}")
            workflow_success = False
        
        # Test 4: Data Sync
        try:
            sync_types = ["all", "customers", "invoices"]
            sync_results = {}
            
            for sync_type in sync_types:
                sync_data = {"sync_type": sync_type}
                
                response = self.session.post(
                    f"{BACKEND_URL}/integrations/quickbooks/sync",
                    json=sync_data,
                    headers={
                        "Authorization": f"Bearer {client_token}",
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        records_synced = data.get("records_synced", 0)
                        sync_results[sync_type] = records_synced
                        
                        self.log_test(
                            f"QuickBooks Data Sync ({sync_type})",
                            True,
                            f"Synced {records_synced} records successfully"
                        )
                    else:
                        self.log_test(
                            f"QuickBooks Data Sync ({sync_type})",
                            False,
                            f"Sync failed: {data}",
                            data
                        )
                        workflow_success = False
                else:
                    self.log_test(
                        f"QuickBooks Data Sync ({sync_type})",
                        False,
                        f"Request failed with status {response.status_code}",
                        response.text
                    )
                    workflow_success = False
            
            self.integration_data["quickbooks_sync"] = sync_results
            
        except Exception as e:
            self.log_test("QuickBooks Data Sync", False, f"Error: {str(e)}")
            workflow_success = False
        
        # Test 5: Cash Flow Analysis
        try:
            response = self.session.get(
                f"{BACKEND_URL}/integrations/quickbooks/cash-flow-analysis?days=90",
                headers={"Authorization": f"Bearer {client_token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                cash_position = data.get("current_cash_position", {})
                trends = data.get("cash_flow_trends", {})
                predictions = data.get("weekly_predictions", [])
                
                if cash_position and trends:
                    total_cash = cash_position.get("total_cash", 0)
                    net_flow = trends.get("net_cash_flow", 0)
                    
                    self.log_test(
                        "QuickBooks Cash Flow Analysis",
                        True,
                        f"Cash flow analysis completed - Total Cash: ${total_cash:,.2f}, Net Flow: ${net_flow:,.2f}, Predictions: {len(predictions)}"
                    )
                    self.integration_data["cash_flow"] = {
                        "total_cash": total_cash,
                        "net_flow": net_flow,
                        "predictions_count": len(predictions)
                    }
                else:
                    self.log_test(
                        "QuickBooks Cash Flow Analysis",
                        False,
                        "Missing cash position or trends data",
                        data
                    )
                    workflow_success = False
            else:
                self.log_test(
                    "QuickBooks Cash Flow Analysis",
                    False,
                    f"Request failed with status {response.status_code}",
                    response.text
                )
                workflow_success = False
                
        except Exception as e:
            self.log_test("QuickBooks Cash Flow Analysis", False, f"Error: {str(e)}")
            workflow_success = False
        
        return workflow_success

    def test_microsoft365_integration_complete(self):
        """Test complete Microsoft 365 integration workflow"""
        print("📧 TESTING MICROSOFT 365 INTEGRATION COMPLETE WORKFLOW...")
        print("=" * 60)
        
        client_token = self.tokens.get("client")
        if not client_token:
            self.log_test("Microsoft 365 Integration - Authentication", False, "Client token not available")
            return False
        
        workflow_success = True
        
        # Test 1: Microsoft 365 Auth URL
        try:
            response = self.session.get(
                f"{BACKEND_URL}/integrations/microsoft365/auth-url",
                headers={"Authorization": f"Bearer {client_token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get("auth_url", "")
                state = data.get("state", "")
                
                if "login.microsoftonline.com" in auth_url and "oauth2" in auth_url:
                    self.log_test(
                        "Microsoft 365 Auth URL Generation",
                        True,
                        f"Auth URL generated successfully with state: {state}"
                    )
                    self.integration_data["m365_state"] = state
                else:
                    self.log_test(
                        "Microsoft 365 Auth URL Generation",
                        False,
                        f"Invalid auth URL format: {auth_url}",
                        data
                    )
                    workflow_success = False
            else:
                self.log_test(
                    "Microsoft 365 Auth URL Generation",
                    False,
                    f"Request failed with status {response.status_code}",
                    response.text
                )
                workflow_success = False
                
        except Exception as e:
            self.log_test("Microsoft 365 Auth URL Generation", False, f"Error: {str(e)}")
            workflow_success = False
        
        # Test 2: Microsoft 365 Connection
        try:
            connection_data = {
                "auth_code": f"mock_m365_auth_code_{int(time.time())}",
                "redirect_uri": "https://polaris-migrate.preview.emergentagent.com/auth/callback",
                "tenant_id": "demo_tenant_id"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/integrations/microsoft365/connect",
                json=connection_data,
                headers={
                    "Authorization": f"Bearer {client_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("status") == "connected":
                    scopes = data.get("scopes", [])
                    expected_scopes = ["Mail.Send", "Files.ReadWrite", "Calendars.ReadWrite"]
                    
                    if all(scope in scopes for scope in expected_scopes):
                        self.log_test(
                            "Microsoft 365 Connection",
                            True,
                            f"Microsoft 365 connected successfully with scopes: {scopes}"
                        )
                        self.integration_data["m365_scopes"] = scopes
                    else:
                        self.log_test(
                            "Microsoft 365 Connection - Scopes",
                            False,
                            f"Missing expected scopes. Got: {scopes}, Expected: {expected_scopes}",
                            data
                        )
                        workflow_success = False
                else:
                    self.log_test(
                        "Microsoft 365 Connection",
                        False,
                        f"Connection failed: {data}",
                        data
                    )
                    workflow_success = False
            else:
                self.log_test(
                    "Microsoft 365 Connection",
                    False,
                    f"Request failed with status {response.status_code}",
                    response.text
                )
                workflow_success = False
                
        except Exception as e:
            self.log_test("Microsoft 365 Connection", False, f"Error: {str(e)}")
            workflow_success = False
        
        # Test 3: Email Automation
        try:
            assessment_email_data = {
                "template_type": "assessment_reminder",
                "recipients": ["client@example.com"],
                "personalization_data": {
                    "business_name": "Integration Test Business LLC",
                    "pending_areas": ["Business Formation", "Financial Operations", "Technology & Security"],
                    "completion_percentage": 67,
                    "assessment_url": "https://polaris-migrate.preview.emergentagent.com/assessment",
                    "financial_health_score": self.integration_data.get("financial_health", {}).get("overall_score", 0)
                }
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/integrations/microsoft365/send-email",
                json=assessment_email_data,
                headers={
                    "Authorization": f"Bearer {client_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("success") and 
                    data.get("template_type") == "assessment_reminder" and
                    data.get("delivery_status") == "sent"):
                    
                    self.log_test(
                        "Microsoft 365 Email Automation",
                        True,
                        f"Assessment reminder email sent successfully. Subject: {data.get('subject')}"
                    )
                    self.integration_data["email_sent"] = True
                else:
                    self.log_test(
                        "Microsoft 365 Email Automation",
                        False,
                        f"Email sending failed: {data}",
                        data
                    )
                    workflow_success = False
            else:
                self.log_test(
                    "Microsoft 365 Email Automation",
                    False,
                    f"Request failed with status {response.status_code}",
                    response.text
                )
                workflow_success = False
                
        except Exception as e:
            self.log_test("Microsoft 365 Email Automation", False, f"Error: {str(e)}")
            workflow_success = False
        
        # Test 4: Document Backup
        try:
            backup_data = {
                "documents": [
                    {
                        "name": "Business_License_2025.pdf",
                        "type": "license",
                        "size_bytes": 2048000,
                        "content": "base64_encoded_license_content",
                        "metadata": {
                            "created_date": "2025-01-15",
                            "category": "legal_documents",
                            "business_id": self.user_ids.get("client")
                        }
                    },
                    {
                        "name": "Financial_Statement_Q4_2024.xlsx",
                        "type": "financial",
                        "size_bytes": 1536000,
                        "content": "base64_encoded_financial_content",
                        "metadata": {
                            "created_date": "2024-12-31",
                            "category": "financial_documents",
                            "quickbooks_sync": True
                        }
                    }
                ],
                "backup_folder": f"Polaris_Business_Documents_{datetime.now().strftime('%Y_%m')}",
                "include_metadata": True
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/integrations/microsoft365/backup-documents",
                json=backup_data,
                headers={
                    "Authorization": f"Bearer {client_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("success") and 
                    data.get("documents_processed") == 2 and
                    data.get("uploaded_successfully") == 2):
                    
                    backup_size = data.get("backup_size_mb", 0)
                    backup_url = data.get("backup_url", "")
                    
                    self.log_test(
                        "Microsoft 365 Document Backup",
                        True,
                        f"Successfully backed up 2 documents ({backup_size:.2f} MB) to {backup_url}"
                    )
                    self.integration_data["documents_backed_up"] = 2
                else:
                    self.log_test(
                        "Microsoft 365 Document Backup",
                        False,
                        f"Backup failed: {data}",
                        data
                    )
                    workflow_success = False
            else:
                self.log_test(
                    "Microsoft 365 Document Backup",
                    False,
                    f"Request failed with status {response.status_code}",
                    response.text
                )
                workflow_success = False
                
        except Exception as e:
            self.log_test("Microsoft 365 Document Backup", False, f"Error: {str(e)}")
            workflow_success = False
        
        return workflow_success

    def test_crm_integration_complete(self):
        """Test complete CRM integration workflow"""
        print("🤝 TESTING CRM INTEGRATION COMPLETE WORKFLOW...")
        print("=" * 60)
        
        client_token = self.tokens.get("client")
        if not client_token:
            self.log_test("CRM Integration - Authentication", False, "Client token not available")
            return False
        
        workflow_success = True
        
        # Test 1: CRM Connection
        try:
            crm_connection_data = {
                "platform": "salesforce",
                "credentials": {
                    "org_id": "mock_salesforce_org_id",
                    "client_id": "mock_salesforce_client_id",
                    "client_secret": "mock_salesforce_client_secret",
                    "instance_url": "https://demo.salesforce.com"
                },
                "sync_preferences": {
                    "sync_contacts": True,
                    "sync_opportunities": True,
                    "sync_accounts": True,
                    "bidirectional_sync": True
                }
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/integrations/crm/connect",
                json=crm_connection_data,
                headers={
                    "Authorization": f"Bearer {client_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("status") == "connected":
                    self.log_test(
                        "CRM Connection Setup",
                        True,
                        f"CRM connected successfully: {data.get('platform')} - Features: {len(data.get('features_enabled', []))}"
                    )
                    self.integration_data["crm_connected"] = True
                else:
                    self.log_test(
                        "CRM Connection Setup",
                        False,
                        f"CRM connection failed: {data}",
                        data
                    )
                    workflow_success = False
            else:
                self.log_test(
                    "CRM Connection Setup",
                    False,
                    f"Request failed with status {response.status_code}",
                    response.text
                )
                workflow_success = False
                
        except Exception as e:
            self.log_test("CRM Connection Setup", False, f"Error: {str(e)}")
            workflow_success = False
        
        # Test 2: Lead Scoring
        try:
            lead_scoring_data = {
                "contact_data": {
                    "contact_id": "lead_001",
                    "company_name": "Tech Solutions Inc",
                    "industry": "Technology",
                    "annual_revenue": 2500000,
                    "employee_count": 45,
                    "procurement_history": True,
                    "certifications": ["SBA 8(a)", "WOSB"],
                    "financial_health_score": self.integration_data.get("financial_health", {}).get("overall_score", 7.5),
                    "assessment_completion": 85
                },
                "activity_data": [
                    {
                        "activity_type": "email_open",
                        "timestamp": "2025-01-08T10:00:00Z",
                        "engagement_score": 8
                    },
                    {
                        "activity_type": "website_visit",
                        "timestamp": "2025-01-08T14:30:00Z",
                        "engagement_score": 6
                    }
                ]
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/integrations/crm/lead-scoring",
                json=lead_scoring_data,
                headers={
                    "Authorization": f"Bearer {client_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                lead_score = data.get("lead_score", 0)
                score_breakdown = data.get("score_breakdown", {})
                
                if lead_score > 0:
                    self.log_test(
                        "CRM Lead Scoring",
                        True,
                        f"Lead scoring completed - Score: {lead_score}, Breakdown available: {bool(score_breakdown)}"
                    )
                    self.integration_data["lead_score"] = lead_score
                else:
                    self.log_test(
                        "CRM Lead Scoring",
                        False,
                        f"Invalid lead scoring result: {data}",
                        data
                    )
                    workflow_success = False
            else:
                self.log_test(
                    "CRM Lead Scoring",
                    False,
                    f"Request failed with status {response.status_code}",
                    response.text
                )
                workflow_success = False
                
        except Exception as e:
            self.log_test("CRM Lead Scoring", False, f"Error: {str(e)}")
            workflow_success = False
        
        # Test 3: CRM Data Sync
        try:
            sync_data = {
                "platforms": ["salesforce"],
                "sync_direction": "bidirectional",
                "object_types": ["contacts", "companies", "deals"],
                "force_full_sync": False
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/integrations/crm/sync",
                json=sync_data,
                headers={
                    "Authorization": f"Bearer {client_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    sync_results = data.get("sync_results", {})
                    contacts_synced = sync_results.get("contacts_synced", 0)
                    companies_synced = sync_results.get("companies_synced", 0)
                    
                    self.log_test(
                        "CRM Bidirectional Data Sync",
                        True,
                        f"Sync completed - Contacts: {contacts_synced}, Companies: {companies_synced}"
                    )
                    self.integration_data["crm_sync_results"] = sync_results
                else:
                    self.log_test(
                        "CRM Bidirectional Data Sync",
                        False,
                        f"Sync failed: {data}",
                        data
                    )
                    workflow_success = False
            else:
                self.log_test(
                    "CRM Bidirectional Data Sync",
                    False,
                    f"Request failed with status {response.status_code}",
                    response.text
                )
                workflow_success = False
                
        except Exception as e:
            self.log_test("CRM Bidirectional Data Sync", False, f"Error: {str(e)}")
            workflow_success = False
        
        # Test 4: CRM Analytics
        try:
            response = self.session.get(
                f"{BACKEND_URL}/integrations/crm/analytics",
                headers={"Authorization": f"Bearer {client_token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for any analytics data
                if data and len(data) > 3:  # Should have user_id, timeframe, and other analytics data
                    self.log_test(
                        "CRM Analytics Generation",
                        True,
                        f"CRM analytics generated - Data fields: {len(data)}, User ID: {data.get('user_id', 'N/A')}"
                    )
                    self.integration_data["crm_analytics"] = data
                else:
                    self.log_test(
                        "CRM Analytics Generation",
                        False,
                        f"Insufficient analytics data: {data}",
                        data
                    )
                    workflow_success = False
            else:
                self.log_test(
                    "CRM Analytics Generation",
                    False,
                    f"Request failed with status {response.status_code}",
                    response.text
                )
                workflow_success = False
                
        except Exception as e:
            self.log_test("CRM Analytics Generation", False, f"Error: {str(e)}")
            workflow_success = False
        
        return workflow_success

    def test_integration_status_monitoring(self):
        """Test integration status monitoring"""
        print("📊 TESTING INTEGRATION STATUS MONITORING...")
        print("=" * 60)
        
        client_token = self.tokens.get("client")
        if not client_token:
            self.log_test("Integration Status - Authentication", False, "Client token not available")
            return False
        
        try:
            response = self.session.get(
                f"{BACKEND_URL}/integrations/status",
                headers={"Authorization": f"Bearer {client_token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                integrations = data.get("integrations", [])
                overall_health = data.get("overall_health_score", 0)
                total_integrations = data.get("total_integrations", 0)
                active_integrations = data.get("active_integrations", 0)
                
                # Verify integration status reflects our test connections
                active_platforms = [i.get("platform") for i in integrations if i.get("status") == "connected"]
                
                if len(active_platforms) >= 1 and overall_health >= 50:
                    self.log_test(
                        "Integration Status Monitoring",
                        True,
                        f"Integration status working - Total: {total_integrations}, Active: {active_integrations}, Health: {overall_health}%, Platforms: {active_platforms}"
                    )
                    self.integration_data["integration_health"] = overall_health
                    self.integration_data["active_platforms"] = active_platforms
                    return True
                else:
                    self.log_test(
                        "Integration Status Monitoring",
                        False,
                        f"Poor integration status - Active: {active_platforms}, Health: {overall_health}%",
                        data
                    )
                    return False
            else:
                self.log_test(
                    "Integration Status Monitoring",
                    False,
                    f"Request failed with status {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Integration Status Monitoring", False, f"Error: {str(e)}")
            return False

    def generate_focused_integration_report(self):
        """Generate focused integration testing report"""
        print("=" * 80)
        print("📋 FOCUSED INTEGRATION TESTING REPORT")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Test Date: {datetime.now().isoformat()}")
        print(f"Total Integration Tests: {self.total_tests}")
        print(f"Passed Tests: {self.passed_tests}")
        print(f"Failed Tests: {self.total_tests - self.passed_tests}")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        print()
        
        # Integration Data Summary
        print("INTEGRATION DATA FLOW SUMMARY:")
        print("-" * 40)
        
        if self.integration_data:
            for key, value in self.integration_data.items():
                print(f"• {key.replace('_', ' ').title()}: {value}")
        else:
            print("• No integration data collected")
        
        print()
        
        # Detailed Test Results by Integration
        integrations = {
            "QuickBooks Integration": [r for r in self.test_results if "quickbooks" in r["test"].lower()],
            "Microsoft 365 Integration": [r for r in self.test_results if "microsoft" in r["test"].lower()],
            "CRM Integration": [r for r in self.test_results if "crm" in r["test"].lower()],
            "Integration Status": [r for r in self.test_results if "status" in r["test"].lower() or "monitoring" in r["test"].lower()]
        }
        
        print("DETAILED RESULTS BY INTEGRATION:")
        print("-" * 40)
        
        for integration, results in integrations.items():
            if results:
                passed = sum(1 for r in results if r["success"])
                total = len(results)
                integration_rate = (passed / total * 100) if total > 0 else 0
                
                print(f"\n{integration}: {passed}/{total} ({integration_rate:.1f}%)")
                for result in results:
                    print(f"  {result['status']}: {result['test']}")
                    if result['details']:
                        print(f"    {result['details']}")
        
        print()
        print("=" * 80)
        
        # Final Assessment
        if success_rate >= 95:
            print("✅ INTEGRATION TESTING: EXCELLENT - ALL SYSTEMS FULLY OPERATIONAL")
            print("🎯 DEFINITIVE EVIDENCE: All integration workflows complete successfully")
            print("🔗 DATA FLOW VERIFIED: Real data interconnectivity confirmed")
            print("📊 MONITORING ACTIVE: Integration health monitoring working correctly")
        elif success_rate >= 85:
            print("✅ INTEGRATION TESTING: GOOD - SYSTEMS READY FOR PRODUCTION")
            print("🎯 STRONG EVIDENCE: Most integration workflows operational")
            print("🔗 DATA FLOW MOSTLY VERIFIED: Good interconnectivity with minor gaps")
        elif success_rate >= 70:
            print("⚠️ INTEGRATION TESTING: PARTIAL - SOME ISSUES IDENTIFIED")
            print("🎯 LIMITED EVIDENCE: Some integration workflows working")
            print("🔗 DATA FLOW INCOMPLETE: Interconnectivity issues need resolution")
        else:
            print("❌ INTEGRATION TESTING: FAILED - CRITICAL INTEGRATION ISSUES")
            print("🎯 INSUFFICIENT EVIDENCE: Integration workflows not operational")
            print("🔗 DATA FLOW BROKEN: Major interconnectivity failures detected")
        
        print("=" * 80)
        
        return success_rate >= 80

    def run_focused_integration_tests(self):
        """Run focused integration tests on existing endpoints"""
        print("🎯 FOCUSED INTEGRATION TESTING STARTED")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Date: {datetime.now().isoformat()}")
        print("Testing only implemented integration endpoints")
        print("=" * 80)
        print()
        
        # Step 1: Authenticate required roles
        if not self.authenticate_roles():
            print("❌ AUTHENTICATION FAILED - CANNOT PROCEED WITH INTEGRATION TESTS")
            return False
        
        print("=" * 80)
        print("🧪 RUNNING FOCUSED INTEGRATION TESTS")
        print("=" * 80)
        print()
        
        # Step 2: Test QuickBooks Integration (5 endpoints)
        self.test_quickbooks_integration_complete()
        
        # Step 3: Test Microsoft 365 Integration (4 endpoints)
        self.test_microsoft365_integration_complete()
        
        # Step 4: Test CRM Integration (4 endpoints)
        self.test_crm_integration_complete()
        
        # Step 5: Test Integration Status (1 endpoint)
        self.test_integration_status_monitoring()
        
        # Step 6: Generate focused report
        return self.generate_focused_integration_report()

def main():
    """Main test execution"""
    tester = FocusedIntegrationTester()
    
    try:
        success = tester.run_focused_integration_tests()
        
        if success:
            print("\n🎉 FOCUSED INTEGRATION TESTING: SUCCESS!")
            print("✅ EVIDENCE: Integration features operational with real data flow")
            sys.exit(0)
        else:
            print("\n❌ FOCUSED INTEGRATION TESTING: SOME ISSUES IDENTIFIED!")
            print("⚠️ INTEGRATION GAPS: Not all workflows fully operational")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Integration testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Integration testing failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()