from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class TestStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class TestCase(BaseModel):
    name: str
    content: str
    file_path: Optional[str] = None

class TestExecutionRequest(BaseModel):
    test_cases: List[TestCase]
    test_type: str = "python_unittest"

class TestResult(BaseModel):
    test_name: str
    status: str  # "passed", "failed", "error", "skipped"
    duration: float
    error_message: Optional[str] = None
    traceback: Optional[str] = None

class TestExecutionResult(BaseModel):
    execution_id: str
    status: TestStatus
    total_tests: int
    passed: int
    failed: int
    errors: int
    skipped: int
    duration: float
    test_results: List[TestResult]
    created_at: datetime
    completed_at: Optional[datetime] = None

class TestSuite(BaseModel):
    name: str
    description: Optional[str] = None
    test_cases: List[TestCase]