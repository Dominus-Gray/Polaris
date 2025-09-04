#!/usr/bin/env python3
"""
Evidence Upload System and Navigator Review Testing
Testing the newly implemented evidence upload system and navigator review functionality
"""

import requests
import json
import os
import tempfile
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://agencydash.preview.emergentagent.com/api"

# QA Credentials
CLIENT_CREDENTIALS = {
    "email": "client.qa@polaris.example.com",
    "password": "Polaris#2025!"
}

NAVIGATOR_CREDENTIALS = {
    "email": "navigator.qa@polaris.example.com", 
    "password": "Polaris#2025!"
}

class EvidenceUploadSystemTester:
    def __init__(self):
        self.client_token = None
        self.navigator_token = None
        self.session_id = None
        self.evidence_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, details):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()

    def authenticate_client(self):
        """Authenticate as client user"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=CLIENT_CREDENTIALS)
            
            if response.status_code == 200:
                data = response.json()
                self.client_token = data["access_token"]
                self.log_test("Client Authentication", True, f"Successfully authenticated as {CLIENT_CREDENTIALS['email']}")
                return True
            else:
                self.log_test("Client Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Client Authentication", False, f"Exception: {str(e)}")
            return False

    def authenticate_navigator(self):
        """Authenticate as navigator user"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=NAVIGATOR_CREDENTIALS)
            
            if response.status_code == 200:
                data = response.json()
                self.navigator_token = data["access_token"]
                self.log_test("Navigator Authentication", True, f"Successfully authenticated as {NAVIGATOR_CREDENTIALS['email']}")
                return True
            else:
                self.log_test("Navigator Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Navigator Authentication", False, f"Exception: {str(e)}")
            return False

    def create_tier_session(self):
        """Create a tier-based assessment session for evidence upload"""
        try:
            headers = {"Authorization": f"Bearer {self.client_token}"}
            
            # Create Tier 2 session (evidence required) - using Form data
            session_data = {
                "area_id": "area1",
                "tier_level": "2"
            }
            
            response = requests.post(f"{BACKEND_URL}/assessment/tier-session", 
                                   data=session_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.session_id = data["session_id"]
                self.log_test("Tier Session Creation", True, 
                            f"Created Tier 2 session: {self.session_id} for area1 (Business Formation)")
                return True
            else:
                self.log_test("Tier Session Creation", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Tier Session Creation", False, f"Exception: {str(e)}")
            return False

    def create_mock_files(self):
        """Create mock files for evidence upload testing"""
        try:
            # Create temporary files for testing
            self.temp_files = []
            
            # Create a PDF file
            pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000074 00000 n \n0000000120 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n179\n%%EOF"
            pdf_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
            pdf_file.write(pdf_content)
            pdf_file.close()
            self.temp_files.append(pdf_file.name)
            
            # Create a DOCX file (simple)
            docx_content = b"PK\x03\x04\x14\x00\x00\x00\x08\x00"  # Basic ZIP header for DOCX
            docx_file = tempfile.NamedTemporaryFile(suffix='.docx', delete=False)
            docx_file.write(docx_content)
            docx_file.close()
            self.temp_files.append(docx_file.name)
            
            # Create a JPG file (minimal JPEG header)
            jpg_content = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9"
            jpg_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            jpg_file.write(jpg_content)
            jpg_file.close()
            self.temp_files.append(jpg_file.name)
            
            self.log_test("Mock File Creation", True, 
                        f"Created {len(self.temp_files)} mock files: PDF, DOCX, JPG")
            return True
            
        except Exception as e:
            self.log_test("Mock File Creation", False, f"Exception: {str(e)}")
            return False

    def test_evidence_upload(self):
        """Test evidence upload endpoint"""
        try:
            headers = {"Authorization": f"Bearer {self.client_token}"}
            
            # Prepare files for upload
            files = []
            for i, file_path in enumerate(self.temp_files):
                files.append(('files', (f'evidence_{i+1}{os.path.splitext(file_path)[1]}', 
                                      open(file_path, 'rb'), 'application/octet-stream')))
            
            # Prepare form data
            data = {
                'session_id': self.session_id,
                'question_id': 'q1_4_t2',  # Tier 2 evidence required question
                'evidence_description': 'Business license documentation and compliance certificates'
            }
            
            response = requests.post(f"{BACKEND_URL}/assessment/evidence/upload", 
                                   data=data, files=files, headers=headers)
            
            # Close file handles
            for _, file_tuple in files:
                file_tuple[1].close()
            
            if response.status_code == 200:
                data = response.json()
                self.evidence_id = data["evidence_id"]
                self.log_test("Evidence Upload", True, 
                            f"Successfully uploaded {data['uploaded_files']} files. Evidence ID: {self.evidence_id}")
                return True
            else:
                self.log_test("Evidence Upload", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Evidence Upload", False, f"Exception: {str(e)}")
            return False

    def test_file_storage_verification(self):
        """Verify evidence files are stored correctly in /app/evidence/"""
        try:
            if not self.session_id:
                self.log_test("File Storage Verification", False, "No session ID available")
                return False
                
            # Check if evidence directory exists
            evidence_dir = f"/app/evidence/{self.session_id}/q1_4_t2"
            
            if os.path.exists(evidence_dir):
                files = os.listdir(evidence_dir)
                if len(files) > 0:
                    self.log_test("File Storage Verification", True, 
                                f"Found {len(files)} files in evidence directory: {evidence_dir}")
                    return True
                else:
                    self.log_test("File Storage Verification", False, 
                                f"Evidence directory exists but is empty: {evidence_dir}")
                    return False
            else:
                self.log_test("File Storage Verification", False, 
                            f"Evidence directory not found: {evidence_dir}")
                return False
                
        except Exception as e:
            self.log_test("File Storage Verification", False, f"Exception: {str(e)}")
            return False

    def test_navigator_pending_evidence(self):
        """Test navigator endpoint to retrieve pending evidence"""
        try:
            headers = {"Authorization": f"Bearer {self.navigator_token}"}
            
            response = requests.get(f"{BACKEND_URL}/navigator/evidence/pending", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                pending_count = data.get("total_count", 0)
                evidence_list = data.get("pending_evidence", [])
                
                # Check if our uploaded evidence is in the list
                our_evidence_found = False
                if self.evidence_id:
                    for evidence in evidence_list:
                        if evidence.get("id") == self.evidence_id:
                            our_evidence_found = True
                            break
                
                self.log_test("Navigator Pending Evidence Retrieval", True, 
                            f"Retrieved {pending_count} pending evidence submissions. Our evidence found: {our_evidence_found}")
                return True
            else:
                self.log_test("Navigator Pending Evidence Retrieval", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Navigator Pending Evidence Retrieval", False, f"Exception: {str(e)}")
            return False

    def test_evidence_review_approval(self):
        """Test navigator evidence review functionality - approval"""
        try:
            if not self.evidence_id:
                self.log_test("Evidence Review - Approval", False, "No evidence ID available")
                return False
                
            headers = {"Authorization": f"Bearer {self.navigator_token}"}
            
            review_data = {
                "review_status": "approved",
                "review_comments": "Evidence documentation is complete and meets requirements. Business license and compliance certificates are valid.",
                "follow_up_required": False
            }
            
            response = requests.post(f"{BACKEND_URL}/navigator/evidence/{self.evidence_id}/review", 
                                   json=review_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Evidence Review - Approval", True, 
                            f"Successfully approved evidence. Status: {data.get('review_status')}")
                return True
            else:
                self.log_test("Evidence Review - Approval", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Evidence Review - Approval", False, f"Exception: {str(e)}")
            return False

    def test_evidence_review_rejection(self):
        """Test navigator evidence review functionality - rejection"""
        try:
            # First upload another evidence for rejection testing
            headers = {"Authorization": f"Bearer {self.client_token}"}
            
            # Create a simple text file for rejection test
            text_file = tempfile.NamedTemporaryFile(suffix='.txt', delete=False, mode='w')
            text_file.write("This is insufficient evidence for testing rejection")
            text_file.close()
            
            files = [('files', ('insufficient_evidence.txt', open(text_file.name, 'rb'), 'text/plain'))]
            
            data = {
                'session_id': self.session_id,
                'question_id': 'q1_5_t2',  # Different question for rejection test
                'evidence_description': 'Insufficient documentation for testing'
            }
            
            response = requests.post(f"{BACKEND_URL}/assessment/evidence/upload", 
                                   data=data, files=files, headers=headers)
            
            files[0][1][1].close()  # Close file handle
            os.unlink(text_file.name)  # Clean up temp file
            
            if response.status_code != 200:
                self.log_test("Evidence Review - Rejection Setup", False, 
                            f"Failed to upload evidence for rejection test: {response.status_code}")
                return False
            
            rejection_evidence_id = response.json()["evidence_id"]
            
            # Now test rejection
            navigator_headers = {"Authorization": f"Bearer {self.navigator_token}"}
            
            review_data = {
                "review_status": "rejected",
                "review_comments": "Evidence is insufficient. Please provide official business license documents and compliance certificates.",
                "follow_up_required": True
            }
            
            response = requests.post(f"{BACKEND_URL}/navigator/evidence/{rejection_evidence_id}/review", 
                                   json=review_data, headers=navigator_headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Evidence Review - Rejection", True, 
                            f"Successfully rejected evidence. Status: {data.get('review_status')}")
                return True
            else:
                self.log_test("Evidence Review - Rejection", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Evidence Review - Rejection", False, f"Exception: {str(e)}")
            return False

    def test_file_download_capability(self):
        """Test navigator file download capability"""
        try:
            if not self.evidence_id:
                self.log_test("File Download Capability", False, "No evidence ID available")
                return False
                
            # First get the evidence details to find file names
            headers = {"Authorization": f"Bearer {self.navigator_token}"}
            
            # Get pending evidence to find file names
            response = requests.get(f"{BACKEND_URL}/navigator/evidence/pending", headers=headers)
            
            if response.status_code != 200:
                self.log_test("File Download Capability", False, "Could not retrieve evidence details")
                return False
            
            evidence_list = response.json().get("pending_evidence", [])
            our_evidence = None
            
            for evidence in evidence_list:
                if evidence.get("id") == self.evidence_id:
                    our_evidence = evidence
                    break
            
            # Debug: Print evidence details
            print(f"DEBUG: Looking for evidence ID: {self.evidence_id}")
            print(f"DEBUG: Found {len(evidence_list)} evidence records")
            if our_evidence:
                print(f"DEBUG: Found our evidence with {len(our_evidence.get('files', []))} files")
                if our_evidence.get("files"):
                    print(f"DEBUG: First file: {our_evidence['files'][0]}")
            else:
                print("DEBUG: Our evidence not found in pending list")
                # Try to find it in all evidence (it might have been approved)
                for evidence in evidence_list:
                    print(f"DEBUG: Evidence ID: {evidence.get('id')}, Status: {evidence.get('review_status')}")
            
            if not our_evidence or not our_evidence.get("files"):
                # The evidence might have been approved and no longer in pending list
                # Let's try to download anyway using a known file pattern
                # Since we uploaded 3 files, let's try to find them in the file system
                evidence_dir = f"/app/evidence/{self.session_id}/q1_4_t2"
                if os.path.exists(evidence_dir):
                    files = os.listdir(evidence_dir)
                    if files:
                        file_name = files[0]  # Use first file found
                        download_response = requests.get(
                            f"{BACKEND_URL}/navigator/evidence/{self.evidence_id}/files/{file_name}", 
                            headers=headers
                        )
                        
                        if download_response.status_code == 200:
                            file_size = len(download_response.content)
                            self.log_test("File Download Capability", True, 
                                        f"Successfully downloaded file: {file_name} ({file_size} bytes)")
                            return True
                        else:
                            self.log_test("File Download Capability", False, 
                                        f"Download failed. Status: {download_response.status_code}, Response: {download_response.text}")
                            return False
                    else:
                        self.log_test("File Download Capability", False, "No files found in evidence directory")
                        return False
                else:
                    self.log_test("File Download Capability", False, "Evidence directory not found")
                    return False
            
            # Test downloading the first file
            first_file = our_evidence["files"][0]
            file_name = first_file["stored_name"]
            
            download_response = requests.get(
                f"{BACKEND_URL}/navigator/evidence/{self.evidence_id}/files/{file_name}", 
                headers=headers
            )
            
            if download_response.status_code == 200:
                file_size = len(download_response.content)
                self.log_test("File Download Capability", True, 
                            f"Successfully downloaded file: {file_name} ({file_size} bytes)")
                return True
            else:
                self.log_test("File Download Capability", False, 
                            f"Download failed. Status: {download_response.status_code}, Response: {download_response.text}")
                return False
                
        except Exception as e:
            self.log_test("File Download Capability", False, f"Exception: {str(e)}")
            return False

    def test_notification_system(self):
        """Test notification system after evidence review"""
        try:
            # Wait a moment for notification to be created
            time.sleep(2)
            
            headers = {"Authorization": f"Bearer {self.client_token}"}
            
            response = requests.get(f"{BACKEND_URL}/notifications/my", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                notifications = data.get("notifications", [])
                
                # Look for evidence review notifications
                evidence_notifications = []
                for notification in notifications:
                    if "evidence" in notification.get("title", "").lower() or \
                       "evidence" in notification.get("message", "").lower():
                        evidence_notifications.append(notification)
                
                if evidence_notifications:
                    self.log_test("Notification System", True, 
                                f"Found {len(evidence_notifications)} evidence-related notifications")
                    return True
                else:
                    self.log_test("Notification System", False, 
                                f"No evidence notifications found. Total notifications: {len(notifications)}")
                    return False
            else:
                self.log_test("Notification System", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Notification System", False, f"Exception: {str(e)}")
            return False

    def cleanup_temp_files(self):
        """Clean up temporary files"""
        try:
            if hasattr(self, 'temp_files'):
                for file_path in self.temp_files:
                    if os.path.exists(file_path):
                        os.unlink(file_path)
                self.log_test("Cleanup Temporary Files", True, f"Cleaned up {len(self.temp_files)} temporary files")
            else:
                self.log_test("Cleanup Temporary Files", True, "No temporary files to clean up")
        except Exception as e:
            self.log_test("Cleanup Temporary Files", False, f"Exception: {str(e)}")

    def run_comprehensive_test(self):
        """Run comprehensive evidence upload system test"""
        print("🎯 EVIDENCE UPLOAD SYSTEM AND NAVIGATOR REVIEW TESTING")
        print("=" * 70)
        print()
        
        # Test sequence
        tests = [
            ("Client Authentication", self.authenticate_client),
            ("Navigator Authentication", self.authenticate_navigator),
            ("Tier Session Creation", self.create_tier_session),
            ("Mock File Creation", self.create_mock_files),
            ("Evidence Upload", self.test_evidence_upload),
            ("File Storage Verification", self.test_file_storage_verification),
            ("Navigator Pending Evidence", self.test_navigator_pending_evidence),
            ("Evidence Review - Approval", self.test_evidence_review_approval),
            ("Evidence Review - Rejection", self.test_evidence_review_rejection),
            ("File Download Capability", self.test_file_download_capability),
            ("Notification System", self.test_notification_system),
            ("Cleanup", self.cleanup_temp_files)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            if test_func():
                passed += 1
        
        # Summary
        print("\n" + "=" * 70)
        print("🎯 EVIDENCE UPLOAD SYSTEM TEST SUMMARY")
        print("=" * 70)
        
        success_rate = (passed / total) * 100
        print(f"Overall Success Rate: {passed}/{total} ({success_rate:.1f}%)")
        print()
        
        # Categorize results
        critical_tests = [
            "Client Authentication", "Navigator Authentication", 
            "Evidence Upload", "Navigator Pending Evidence", 
            "Evidence Review - Approval", "File Download Capability"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result["test"] in critical_tests and result["success"])
        critical_total = len(critical_tests)
        
        print(f"Critical Features: {critical_passed}/{critical_total} ({(critical_passed/critical_total)*100:.1f}%)")
        
        # Feature breakdown
        print("\n📋 FEATURE BREAKDOWN:")
        feature_groups = {
            "Authentication": ["Client Authentication", "Navigator Authentication"],
            "Evidence Upload": ["Tier Session Creation", "Mock File Creation", "Evidence Upload"],
            "File Storage": ["File Storage Verification"],
            "Navigator Review": ["Navigator Pending Evidence", "Evidence Review - Approval", "Evidence Review - Rejection"],
            "File Management": ["File Download Capability"],
            "Notifications": ["Notification System"],
            "Cleanup": ["Cleanup"]
        }
        
        for feature, tests in feature_groups.items():
            feature_passed = sum(1 for result in self.test_results 
                               if result["test"] in tests and result["success"])
            feature_total = len(tests)
            status = "✅" if feature_passed == feature_total else "⚠️" if feature_passed > 0 else "❌"
            print(f"{status} {feature}: {feature_passed}/{feature_total}")
        
        # Failed tests
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for result in failed_tests:
                print(f"   • {result['test']}: {result['details']}")
        
        # Production readiness assessment
        print(f"\n🎯 PRODUCTION READINESS ASSESSMENT:")
        if success_rate >= 90:
            print("✅ EXCELLENT - Evidence upload system ready for production")
        elif success_rate >= 75:
            print("🟡 GOOD - Evidence upload system mostly ready, minor issues to address")
        elif success_rate >= 50:
            print("⚠️ NEEDS WORK - Evidence upload system has significant issues")
        else:
            print("❌ NOT READY - Evidence upload system requires major fixes")
        
        return success_rate >= 75

if __name__ == "__main__":
    tester = EvidenceUploadSystemTester()
    tester.run_comprehensive_test()