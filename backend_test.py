#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Drew Events
Tests all backend endpoints according to API requirements
"""

import requests
import json
import sys
from typing import Dict, Any, Optional

# Backend URL from frontend .env
BASE_URL = "https://drew-auth-service.preview.emergentagent.com/api"

class DrewAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.auth_token = None
        self.test_user_id = None
        self.test_org_id = None
        self.test_activity_id = None
        self.results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }
    
    def log_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        
        if success:
            self.results["passed"] += 1
        else:
            self.results["failed"] += 1
            self.results["errors"].append(f"{test_name}: {details}")
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, 
                    headers: Dict = None, params: Dict = None) -> tuple:
        """Make HTTP request and return (success, response, status_code)"""
        url = f"{self.base_url}{endpoint}"
        
        # Add auth header if token exists
        if self.auth_token and headers is None:
            headers = {}
        if self.auth_token:
            headers = headers or {}
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=headers, params=params)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=headers, params=params)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=headers, params=params)
            else:
                return False, None, 0
            
            return True, response, response.status_code
        except Exception as e:
            return False, str(e), 0

    def test_user_registration(self):
        """Test POST /api/user/register"""
        print("\n=== Testing User Registration ===")
        
        # Test successful registration
        user_data = {
            "username": "sarah_johnson",
            "email": "sarah.johnson@example.com",
            "password": "SecurePass123!"
        }
        
        success, response, status = self.make_request("POST", "/user/register", user_data)
        
        if success and status == 201:
            try:
                data = response.json()
                if "token" in data and "user" in data:
                    self.auth_token = data["token"]
                    self.test_user_id = data["user"]["id"]
                    self.log_result("User Registration - Success", True, 
                                  f"User ID: {self.test_user_id}")
                else:
                    self.log_result("User Registration - Response Format", False, 
                                  "Missing token or user in response")
            except Exception as e:
                self.log_result("User Registration - JSON Parse", False, str(e))
        else:
            self.log_result("User Registration - Request", False, 
                          f"Status: {status}, Response: {response.text if response else 'No response'}")
        
        # Test duplicate email (should return 409)
        success, response, status = self.make_request("POST", "/user/register", user_data)
        if success and status == 409:
            self.log_result("User Registration - Duplicate Email Check", True, 
                          "Correctly rejected duplicate email")
        else:
            self.log_result("User Registration - Duplicate Email Check", False, 
                          f"Expected 409, got {status}")

    def test_user_login(self):
        """Test POST /api/user/verify (login)"""
        print("\n=== Testing User Login ===")
        
        # Test successful login
        login_data = {
            "email": "sarah.johnson@example.com",
            "password": "SecurePass123!"
        }
        
        success, response, status = self.make_request("POST", "/user/verify", login_data)
        
        if success and status == 200:
            try:
                data = response.json()
                if "token" in data and "user" in data:
                    # Update token for subsequent tests
                    self.auth_token = data["token"]
                    self.log_result("User Login - Success", True, "Login successful with JWT token")
                else:
                    self.log_result("User Login - Response Format", False, 
                                  "Missing token or user in response")
            except Exception as e:
                self.log_result("User Login - JSON Parse", False, str(e))
        else:
            self.log_result("User Login - Request", False, 
                          f"Status: {status}, Response: {response.text if response else 'No response'}")
        
        # Test invalid credentials (should return 401)
        invalid_login = {
            "email": "sarah.johnson@example.com",
            "password": "WrongPassword"
        }
        
        success, response, status = self.make_request("POST", "/user/verify", invalid_login)
        if success and status == 401:
            self.log_result("User Login - Invalid Credentials Check", True, 
                          "Correctly rejected invalid credentials")
        else:
            self.log_result("User Login - Invalid Credentials Check", False, 
                          f"Expected 401, got {status}")

    def test_get_current_user(self):
        """Test GET /api/user/me"""
        print("\n=== Testing Get Current User ===")
        
        if not self.auth_token:
            self.log_result("Get Current User - No Token", False, "No auth token available")
            return
        
        # Test with valid token
        success, response, status = self.make_request("GET", "/user/me")
        
        if success and status == 200:
            try:
                data = response.json()
                if "id" in data and "email" in data:
                    self.log_result("Get Current User - Success", True, 
                                  f"Retrieved user: {data.get('email')}")
                else:
                    self.log_result("Get Current User - Response Format", False, 
                                  "Missing required fields in user response")
            except Exception as e:
                self.log_result("Get Current User - JSON Parse", False, str(e))
        else:
            self.log_result("Get Current User - Request", False, 
                          f"Status: {status}, Response: {response.text if response else 'No response'}")
        
        # Test without token (should return 401)
        success, response, status = self.make_request("GET", "/user/me", headers={})
        if success and status == 401:
            self.log_result("Get Current User - No Token Check", True, 
                          "Correctly rejected request without token")
        else:
            self.log_result("Get Current User - No Token Check", False, 
                          f"Expected 401, got {status}")

    def test_update_user(self):
        """Test PUT /api/user/{id}"""
        print("\n=== Testing Update User ===")
        
        if not self.auth_token or not self.test_user_id:
            self.log_result("Update User - Prerequisites", False, "No auth token or user ID")
            return
        
        # Test successful update
        update_data = {
            "firstName": "Sarah",
            "lastName": "Johnson",
            "role": "Event Coordinator"
        }
        
        success, response, status = self.make_request("PUT", f"/user/{self.test_user_id}", update_data)
        
        if success and status == 200:
            try:
                data = response.json()
                if data.get("firstName") == "Sarah" and data.get("lastName") == "Johnson":
                    self.log_result("Update User - Success", True, 
                                  "User profile updated successfully")
                else:
                    self.log_result("Update User - Data Verification", False, 
                                  "Updated data not reflected in response")
            except Exception as e:
                self.log_result("Update User - JSON Parse", False, str(e))
        else:
            self.log_result("Update User - Request", False, 
                          f"Status: {status}, Response: {response.text if response else 'No response'}")

    def test_organization_crud(self):
        """Test Organization CRUD operations"""
        print("\n=== Testing Organization CRUD ===")
        
        if not self.auth_token:
            self.log_result("Organization CRUD - No Token", False, "No auth token available")
            return
        
        # Test create organization
        org_data = {
            "name": "Creative Events Co.",
            "industry": "Event Management",
            "companySize": "11-50",
            "website": "https://creativeevents.com"
        }
        
        success, response, status = self.make_request("POST", "/organization", org_data)
        
        if success and status == 201:
            try:
                data = response.json()
                if "id" in data and data.get("name") == "Creative Events Co.":
                    self.test_org_id = data["id"]
                    self.log_result("Organization Create - Success", True, 
                                  f"Organization ID: {self.test_org_id}")
                else:
                    self.log_result("Organization Create - Response Format", False, 
                                  "Missing ID or incorrect data in response")
            except Exception as e:
                self.log_result("Organization Create - JSON Parse", False, str(e))
        else:
            self.log_result("Organization Create - Request", False, 
                          f"Status: {status}, Response: {response.text if response else 'No response'}")
        
        # Test get organization by ID
        if self.test_org_id:
            success, response, status = self.make_request("GET", f"/organization/{self.test_org_id}")
            
            if success and status == 200:
                try:
                    data = response.json()
                    if data.get("name") == "Creative Events Co.":
                        self.log_result("Organization Get - Success", True, 
                                      "Retrieved organization successfully")
                    else:
                        self.log_result("Organization Get - Data Verification", False, 
                                      "Retrieved data doesn't match")
                except Exception as e:
                    self.log_result("Organization Get - JSON Parse", False, str(e))
            else:
                self.log_result("Organization Get - Request", False, 
                              f"Status: {status}")
        
        # Test update organization
        if self.test_org_id:
            update_data = {
                "name": "Creative Events Co. Ltd.",
                "companySize": "51-100"
            }
            
            success, response, status = self.make_request("PUT", f"/organization/{self.test_org_id}", update_data)
            
            if success and status == 200:
                try:
                    data = response.json()
                    if data.get("name") == "Creative Events Co. Ltd.":
                        self.log_result("Organization Update - Success", True, 
                                      "Organization updated successfully")
                    else:
                        self.log_result("Organization Update - Data Verification", False, 
                                      "Updated data not reflected")
                except Exception as e:
                    self.log_result("Organization Update - JSON Parse", False, str(e))
            else:
                self.log_result("Organization Update - Request", False, 
                              f"Status: {status}")
        
        # Test list organizations
        success, response, status = self.make_request("GET", "/organization", params={"limit": 10})
        
        if success and status == 200:
            try:
                data = response.json()
                if "rows" in data and "total" in data and "limit" in data:
                    self.log_result("Organization List - Success", True, 
                                  f"Retrieved {len(data['rows'])} organizations")
                else:
                    self.log_result("Organization List - Response Format", False, 
                                  "Missing pagination fields in response")
            except Exception as e:
                self.log_result("Organization List - JSON Parse", False, str(e))
        else:
            self.log_result("Organization List - Request", False, 
                          f"Status: {status}")

    def test_activity_endpoints(self):
        """Test Activity/Event endpoints"""
        print("\n=== Testing Activity Endpoints ===")
        
        # Test list activities (no auth required)
        success, response, status = self.make_request("GET", "/activity", params={"limit": 10})
        
        if success and status == 200:
            try:
                data = response.json()
                if "rows" in data and "total" in data:
                    activities = data["rows"]
                    if len(activities) > 0:
                        self.test_activity_id = activities[0]["id"]
                        self.log_result("Activity List - Success", True, 
                                      f"Retrieved {len(activities)} activities, seeded data found")
                    else:
                        self.log_result("Activity List - No Data", False, 
                                      "No activities found (seeded data missing)")
                else:
                    self.log_result("Activity List - Response Format", False, 
                                  "Missing pagination fields")
            except Exception as e:
                self.log_result("Activity List - JSON Parse", False, str(e))
        else:
            self.log_result("Activity List - Request", False, 
                          f"Status: {status}, Response: {response.text if response else 'No response'}")
        
        # Test activity filters
        success, response, status = self.make_request("GET", "/activity", 
                                                    params={"location": "New York", "limit": 5})
        
        if success and status == 200:
            self.log_result("Activity List - Location Filter", True, 
                          "Location filter working")
        else:
            self.log_result("Activity List - Location Filter", False, 
                          f"Status: {status}")
        
        # Test get activity by ID
        if self.test_activity_id:
            success, response, status = self.make_request("GET", f"/activity/{self.test_activity_id}")
            
            if success and status == 200:
                try:
                    data = response.json()
                    if "id" in data and "title" in data:
                        self.log_result("Activity Get - Success", True, 
                                      f"Retrieved activity: {data.get('title', 'Unknown')}")
                    else:
                        self.log_result("Activity Get - Response Format", False, 
                                      "Missing required fields")
                except Exception as e:
                    self.log_result("Activity Get - JSON Parse", False, str(e))
            else:
                self.log_result("Activity Get - Request", False, 
                              f"Status: {status}")
            
            # Test expand parameter
            success, response, status = self.make_request("GET", f"/activity/{self.test_activity_id}", 
                                                        params={"expand": "offerings"})
            
            if success and status == 200:
                self.log_result("Activity Get - Expand Parameter", True, 
                              "Expand parameter working")
            else:
                self.log_result("Activity Get - Expand Parameter", False, 
                              f"Status: {status}")
        
        # Test create activity (requires auth)
        if self.auth_token:
            activity_data = {
                "title": "Wine Tasting Experience",
                "description": "Explore premium wines in a beautiful vineyard setting",
                "price": 85.0,
                "location": "Napa Valley Vineyard",
                "city": "Napa",
                "state": "California",
                "category": "Food & Drink",
                "images": ["https://example.com/wine1.jpg"],
                "freeCancellation": True
            }
            
            success, response, status = self.make_request("POST", "/activity", activity_data)
            
            if success and status == 201:
                try:
                    data = response.json()
                    if "id" in data and data.get("title") == "Wine Tasting Experience":
                        created_activity_id = data["id"]
                        self.log_result("Activity Create - Success", True, 
                                      f"Created activity ID: {created_activity_id}")
                        
                        # Test update activity
                        update_data = {
                            "price": 95.0,
                            "description": "Premium wine tasting experience with expert sommelier"
                        }
                        
                        success, response, status = self.make_request("PUT", f"/activity/{created_activity_id}", 
                                                                    update_data)
                        
                        if success and status == 200:
                            try:
                                updated_data = response.json()
                                if updated_data.get("price") == 95.0:
                                    self.log_result("Activity Update - Success", True, 
                                                  "Activity updated successfully")
                                else:
                                    self.log_result("Activity Update - Data Verification", False, 
                                                  "Updated data not reflected")
                            except Exception as e:
                                self.log_result("Activity Update - JSON Parse", False, str(e))
                        else:
                            self.log_result("Activity Update - Request", False, 
                                          f"Status: {status}")
                    else:
                        self.log_result("Activity Create - Response Format", False, 
                                      "Missing ID or incorrect data")
                except Exception as e:
                    self.log_result("Activity Create - JSON Parse", False, str(e))
            else:
                self.log_result("Activity Create - Request", False, 
                              f"Status: {status}, Response: {response.text if response else 'No response'}")

    def test_occasion_endpoints(self):
        """Test Occasion endpoints"""
        print("\n=== Testing Occasion Endpoints ===")
        
        if not self.auth_token:
            self.log_result("Occasion Endpoints - No Token", False, "No auth token available")
            return
        
        # Test list occasions
        success, response, status = self.make_request("GET", "/occasion", params={"limit": 10})
        
        if success and status == 200:
            try:
                data = response.json()
                if "rows" in data and "total" in data:
                    self.log_result("Occasion List - Success", True, 
                                  f"Retrieved occasions with pagination")
                else:
                    self.log_result("Occasion List - Response Format", False, 
                                  "Missing pagination fields")
            except Exception as e:
                self.log_result("Occasion List - JSON Parse", False, str(e))
        else:
            self.log_result("Occasion List - Request", False, 
                          f"Status: {status}")

    def test_offering_endpoints(self):
        """Test Offering endpoints"""
        print("\n=== Testing Offering Endpoints ===")
        
        if not self.auth_token:
            self.log_result("Offering Endpoints - No Token", False, "No auth token available")
            return
        
        # Test list offerings
        success, response, status = self.make_request("GET", "/offering", params={"limit": 10})
        
        if success and status == 200:
            try:
                data = response.json()
                if "rows" in data and "total" in data:
                    self.log_result("Offering List - Success", True, 
                                  f"Retrieved offerings with pagination")
                else:
                    self.log_result("Offering List - Response Format", False, 
                                  "Missing pagination fields")
            except Exception as e:
                self.log_result("Offering List - JSON Parse", False, str(e))
        else:
            self.log_result("Offering List - Request", False, 
                          f"Status: {status}")

    def test_onboarding_endpoint(self):
        """Test POST /api/onboarding"""
        print("\n=== Testing Onboarding Endpoint ===")
        
        if not self.auth_token:
            self.log_result("Onboarding - No Token", False, "No auth token available")
            return
        
        # Test onboarding with organization creation
        onboarding_data = {
            "firstName": "Sarah",
            "lastName": "Johnson",
            "role": "Event Manager",
            "organization": {
                "name": "Sarah's Event Planning",
                "industry": "Event Services",
                "companySize": "1-10",
                "website": "https://sarahevents.com"
            }
        }
        
        success, response, status = self.make_request("POST", "/onboarding", onboarding_data)
        
        if success and status == 200:
            try:
                data = response.json()
                if data.get("success") and "user" in data:
                    user = data["user"]
                    if user.get("hasCompletedOnboarding"):
                        self.log_result("Onboarding - Success", True, 
                                      "Onboarding completed with organization creation")
                    else:
                        self.log_result("Onboarding - Status Update", False, 
                                      "hasCompletedOnboarding not set to true")
                else:
                    self.log_result("Onboarding - Response Format", False, 
                                  "Missing success flag or user data")
            except Exception as e:
                self.log_result("Onboarding - JSON Parse", False, str(e))
        else:
            self.log_result("Onboarding - Request", False, 
                          f"Status: {status}, Response: {response.text if response else 'No response'}")

    def test_auth_additional_endpoints(self):
        """Test additional auth endpoints"""
        print("\n=== Testing Additional Auth Endpoints ===")
        
        # Test magic link (mock)
        magic_data = {"email": "sarah.johnson@example.com"}
        success, response, status = self.make_request("POST", "/auth/magic-link", magic_data)
        
        if success and status == 200:
            try:
                data = response.json()
                if data.get("success"):
                    self.log_result("Auth Magic Link - Success", True, "Mock magic link endpoint working")
                else:
                    self.log_result("Auth Magic Link - Response", False, "Success flag not set")
            except Exception as e:
                self.log_result("Auth Magic Link - JSON Parse", False, str(e))
        else:
            self.log_result("Auth Magic Link - Request", False, f"Status: {status}")
        
        # Test Google OAuth redirect (mock)
        success, response, status = self.make_request("GET", "/auth/google/redirect")
        
        if success and status == 200:
            try:
                data = response.json()
                if "message" in data:
                    self.log_result("Auth Google Redirect - Success", True, "Mock Google OAuth endpoint working")
                else:
                    self.log_result("Auth Google Redirect - Response", False, "Missing message field")
            except Exception as e:
                self.log_result("Auth Google Redirect - JSON Parse", False, str(e))
        else:
            self.log_result("Auth Google Redirect - Request", False, f"Status: {status}")
        
        # Test logout
        if self.auth_token:
            success, response, status = self.make_request("POST", "/auth/logout")
            
            if success and status == 200:
                try:
                    data = response.json()
                    if data.get("success"):
                        self.log_result("Auth Logout - Success", True, "Logout endpoint working")
                    else:
                        self.log_result("Auth Logout - Response", False, "Success flag not set")
                except Exception as e:
                    self.log_result("Auth Logout - JSON Parse", False, str(e))
            else:
                self.log_result("Auth Logout - Request", False, f"Status: {status}")

    def test_backward_compatibility(self):
        """Test backward compatibility endpoints"""
        print("\n=== Testing Backward Compatibility ===")
        
        # Test GET /api/events (should work like /api/activity)
        success, response, status = self.make_request("GET", "/events", params={"limit": 5})
        
        if success and status == 200:
            try:
                data = response.json()
                if "events" in data:
                    self.log_result("Backward Compatibility - Events List", True, 
                                  f"Legacy /events endpoint working")
                else:
                    self.log_result("Backward Compatibility - Events List Format", False, 
                                  "Missing 'events' field in response")
            except Exception as e:
                self.log_result("Backward Compatibility - Events List JSON", False, str(e))
        else:
            self.log_result("Backward Compatibility - Events List Request", False, 
                          f"Status: {status}")
        
        # Test GET /api/events/{id}
        if self.test_activity_id:
            success, response, status = self.make_request("GET", f"/events/{self.test_activity_id}")
            
            if success and status == 200:
                try:
                    data = response.json()
                    if "id" in data:
                        self.log_result("Backward Compatibility - Event Detail", True, 
                                      "Legacy /events/{id} endpoint working")
                    else:
                        self.log_result("Backward Compatibility - Event Detail Format", False, 
                                      "Missing ID in response")
                except Exception as e:
                    self.log_result("Backward Compatibility - Event Detail JSON", False, str(e))
            else:
                self.log_result("Backward Compatibility - Event Detail Request", False, 
                              f"Status: {status}")

    def test_api_health(self):
        """Test API health check"""
        print("\n=== Testing API Health ===")
        
        success, response, status = self.make_request("GET", "/")
        
        if success and status == 200:
            try:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_result("API Health Check - Success", True, 
                                  f"API version: {data.get('version', 'Unknown')}")
                else:
                    self.log_result("API Health Check - Status", False, 
                                  f"Status: {data.get('status', 'Unknown')}")
            except Exception as e:
                self.log_result("API Health Check - JSON Parse", False, str(e))
        else:
            self.log_result("API Health Check - Request", False, 
                          f"Status: {status}")

    def run_all_tests(self):
        """Run all tests in sequence"""
        print(f"🚀 Starting Drew Events Backend API Tests")
        print(f"📍 Backend URL: {self.base_url}")
        print("=" * 60)
        
        # Run tests in logical order
        self.test_api_health()
        self.test_user_registration()
        self.test_user_login()
        self.test_get_current_user()
        self.test_update_user()
        self.test_organization_crud()
        self.test_activity_endpoints()
        self.test_occasion_endpoints()
        self.test_offering_endpoints()
        self.test_onboarding_endpoint()
        self.test_auth_additional_endpoints()
        self.test_backward_compatibility()
        
        # Print summary
        print("\n" + "=" * 60)
        print("🏁 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📊 Total: {self.results['passed'] + self.results['failed']}")
        
        if self.results['errors']:
            print(f"\n🔍 FAILED TESTS:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        return self.results['failed'] == 0

if __name__ == "__main__":
    tester = DrewAPITester()
    success = tester.run_all_tests()
    
    if success:
        print(f"\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print(f"\n⚠️  Some tests failed. Check the details above.")
        sys.exit(1)