from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import httpx
import asyncio
import json
import os
from typing import Dict, Any, List
import uvicorn
from datetime import datetime

app = FastAPI(title="Microservices Test Dashboard", version="1.0.0")

# Service URLs
SERVICE1_URL = os.getenv("SERVICE1_URL", "http://localhost:8000")
SERVICE2_URL = os.getenv("SERVICE2_URL", "http://localhost:8001")
SERVICE_TIMEOUT = int(os.getenv("SERVICE_TIMEOUT", "10"))

# Template directory
template_dir = os.path.join(os.path.dirname(__file__), "templates")

# Mount static files (optional)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

class TestResult:
    def __init__(self, test_name: str, success: bool, message: str, data: Dict = None):
        self.test_name = test_name
        self.success = success
        self.message = message
        self.data = data or {}
        self.timestamp = datetime.now().strftime("%H:%M:%S")

async def check_service_health() -> List[TestResult]:
    """Check if both services are running"""
    results = []
    
    async with httpx.AsyncClient() as client:
        # Check Service 1
        try:
            response = await client.get(f"{SERVICE1_URL}/health", timeout=SERVICE_TIMEOUT)
            if response.status_code == 200:
                results.append(TestResult(
                    "Service 1 Health",
                    True,
                    f"Service 1 is running: {response.json()}",
                    response.json()
                ))
            else:
                results.append(TestResult(
                    "Service 1 Health",
                    False,
                    f"Service 1 returned status {response.status_code}"
                ))
        except Exception as e:
            results.append(TestResult(
                "Service 1 Health",
                False,
                f"Service 1 is not running: {str(e)}"
            ))
        
        # Check Service 2
        try:
            response = await client.get(f"{SERVICE2_URL}/health", timeout=SERVICE_TIMEOUT)
            if response.status_code == 200:
                results.append(TestResult(
                    "Service 2 Health",
                    True,
                    f"Service 2 is running: {response.json()}",
                    response.json()
                ))
            else:
                results.append(TestResult(
                    "Service 2 Health",
                    False,
                    f"Service 2 returned status {response.status_code}"
                ))
        except Exception as e:
            results.append(TestResult(
                "Service 2 Health",
                False,
                f"Service 2 is not running: {str(e)}"
            ))
    
    return results

async def create_test_users() -> List[TestResult]:
    """Create test users in Service 1"""
    results = []
    
    users_data = [
        {"name": "Alice Johnson", "email": "alice@example.com", "age": 25},
        {"name": "Bob Smith", "email": "bob@company.com", "age": 35},
        {"name": "Carol Davis", "email": "carol@university.edu", "age": 45},
        {"name": "David Wilson", "email": "david@startup.io", "age": 28}
    ]
    
    created_users = []
    
    async with httpx.AsyncClient() as client:
        for i, user_data in enumerate(users_data, 1):
            try:
                response = await client.post(f"{SERVICE1_URL}/users", json=user_data, timeout=SERVICE_TIMEOUT)
                if response.status_code == 200:
                    user = response.json()
                    created_users.append(user)
                    results.append(TestResult(
                        f"Create User {i}",
                        True,
                        f"Created user: {user['name']} (ID: {user['id']})",
                        user
                    ))
                else:
                    results.append(TestResult(
                        f"Create User {i}",
                        False,
                        f"Failed to create user: {response.text}"
                    ))
            except Exception as e:
                results.append(TestResult(
                    f"Create User {i}",
                    False,
                    f"Error creating user: {str(e)}"
                ))
    
    return results, created_users

async def get_users_test() -> TestResult:
    """Get all users from Service 1"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{SERVICE1_URL}/users", timeout=SERVICE_TIMEOUT)
            if response.status_code == 200:
                users = response.json()
                return TestResult(
                    "Get All Users",
                    True,
                    f"Found {len(users)} users in Service 1",
                    {"users": users, "count": len(users)}
                )
            else:
                return TestResult(
                    "Get All Users",
                    False,
                    f"Failed to get users: {response.text}"
                )
        except Exception as e:
            return TestResult(
                "Get All Users",
                False,
                f"Error getting users: {str(e)}"
            )

async def get_processed_data_test(users: List[Dict]) -> List[TestResult]:
    """Get processed user data from Service 2"""
    results = []
    
    async with httpx.AsyncClient() as client:
        for user in users:
            try:
                response = await client.get(f"{SERVICE1_URL}/users/{user['id']}/processed", timeout=SERVICE_TIMEOUT)
                if response.status_code == 200:
                    processed_data = response.json()
                    results.append(TestResult(
                        f"Processed Data - {user['name']}",
                        True,
                        f"Service 2 status: {processed_data['service2_status']}",
                        processed_data
                    ))
                else:
                    results.append(TestResult(
                        f"Processed Data - {user['name']}",
                        False,
                        f"Failed to get processed data: {response.text}"
                    ))
            except Exception as e:
                results.append(TestResult(
                    f"Processed Data - {user['name']}",
                    False,
                    f"Error getting processed data: {str(e)}"
                ))
    
    return results

async def get_analytics_test() -> TestResult:
    """Get analytics from Service 2"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{SERVICE2_URL}/analytics", timeout=SERVICE_TIMEOUT)
            if response.status_code == 200:
                analytics = response.json()
                return TestResult(
                    "Get Analytics",
                    True,
                    f"Analytics retrieved successfully",
                    analytics
                )
            else:
                return TestResult(
                    "Get Analytics",
                    False,
                    f"Failed to get analytics: {response.text}"
                )
        except Exception as e:
            return TestResult(
                "Get Analytics",
                False,
                f"Error getting analytics: {str(e)}"
            )

async def cross_service_test() -> TestResult:
    """Test cross-service communication"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{SERVICE2_URL}/cross-service-test", timeout=SERVICE_TIMEOUT)
            if response.status_code == 200:
                test_results = response.json()
                return TestResult(
                    "Cross-Service Test",
                    True,
                    "Cross-service communication successful",
                    test_results
                )
            else:
                return TestResult(
                    "Cross-Service Test",
                    False,
                    f"Failed to test cross-service communication: {response.text}"
                )
        except Exception as e:
            return TestResult(
                "Cross-Service Test",
                False,
                f"Error testing cross-service communication: {str(e)}"
            )

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    # Read the HTML file directly to avoid Jinja2 conflicts with Vue.js
    import aiofiles
    template_path = os.path.join(template_dir, "dashboard.html")
    async with aiofiles.open(template_path, 'r') as f:
        content = await f.read()
    return HTMLResponse(content=content)

@app.post("/api/run-tests")
async def run_tests():
    """Run all tests and return results"""
    all_results = []
    
    # Test 1: Check service health
    health_results = await check_service_health()
    all_results.extend(health_results)
    
    # Check if services are running before proceeding
    services_running = all(all_results[i].success for i in range(2))
    
    if not services_running:
        return {
            "success": False,
            "message": "Services are not running. Please start both services first.",
            "results": all_results
        }
    
    # Test 2: Create users
    create_results, created_users = await create_test_users()
    all_results.extend(create_results)
    
    # Test 3: Get all users
    get_users_result = await get_users_test()
    all_results.append(get_users_result)
    
    # Test 4: Get processed data
    if created_users:
        processed_results = await get_processed_data_test(created_users)
        all_results.extend(processed_results)
    
    # Test 5: Get analytics
    analytics_result = await get_analytics_test()
    all_results.append(analytics_result)
    
    # Test 6: Cross-service test
    cross_service_result = await cross_service_test()
    all_results.append(cross_service_result)
    
    # Calculate summary
    successful_tests = sum(1 for result in all_results if result.success)
    total_tests = len(all_results)
    
    return {
        "success": True,
        "message": f"Tests completed: {successful_tests}/{total_tests} successful",
        "results": [
            {
                "test_name": result.test_name,
                "success": result.success,
                "message": result.message,
                "data": result.data,
                "timestamp": result.timestamp
            }
            for result in all_results
        ],
        "summary": {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": total_tests - successful_tests
        }
    }

@app.get("/api/health")
async def health_check():
    """Quick health check of both services"""
    results = await check_service_health()
    return {
        "services": [
            {
                "name": result.test_name,
                "status": "healthy" if result.success else "unhealthy",
                "message": result.message
            }
            for result in results
        ]
    }

@app.get("/api/users")
async def get_users():
    """Get all users from Service 1"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{SERVICE1_URL}/users", timeout=SERVICE_TIMEOUT)
            if response.status_code == 200:
                return {"success": True, "users": response.json()}
            else:
                return {"success": False, "error": response.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

@app.get("/api/analytics")
async def get_analytics():
    """Get analytics from Service 2"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{SERVICE2_URL}/analytics", timeout=SERVICE_TIMEOUT)
            if response.status_code == 200:
                return {"success": True, "analytics": response.json()}
            else:
                return {"success": False, "error": response.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
