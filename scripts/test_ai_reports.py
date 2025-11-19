"""
Test script for AI Progress Reports feature.
Author: Autumn Erwin
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.features.ai_progress_reports.service import AIProgressReportService
from src.features.ai_progress_reports.repository import AIProgressReportRepository


def test_student_data_retrieval():
    """Test that we can retrieve student performance data."""
    print("\n" + "="*60)
    print("TEST 1: Student Performance Data Retrieval")
    print("="*60)

    repo = AIProgressReportRepository()

    # Get first student's data
    student_id = 1
    data = repo.get_student_performance_data(student_id)

    if data.get('has_data'):
        print(f"✅ Successfully retrieved data for: {data['student_name']}")
        print(f"   Course: {data['course_name']}")
        print(f"   Average: {data['current_average']:.1f}%")
        print(f"   Trend: {data['trend_description']}")
        print(f"   Assignments: {data['num_assignments']}")
        return True
    else:
        print(f"❌ No data found for student {student_id}")
        return False


def test_ai_report_generation():
    """Test AI report generation (requires API key)."""
    print("\n" + "="*60)
    print("TEST 2: AI Report Generation")
    print("="*60)

    # Check for API key
    if not os.getenv('GOOGLE_API_KEY'):
        print("⚠️  GOOGLE_API_KEY not set. Skipping AI generation test.")
        print("   To test AI generation, add your key to .env file")
        return None

    try:
        service = AIProgressReportService()
        print("✅ AI Service initialized successfully")

        # Generate report for student 1
        print("\n🤖 Generating AI report for student 1...")
        result = service.generate_progress_report(student_id=1, force_regenerate=True)

        if result['success']:
            print("✅ Report generated successfully!")
            print("\n" + "-"*60)
            print("REPORT PREVIEW:")
            print("-"*60)
            print(result['report_text'][:500] + "...")
            print("-"*60)
            return True
        else:
            print(f"❌ Report generation failed: {result['error']}")
            return False

    except Exception as e:
        print(f"❌ Error during AI generation: {str(e)}")
        return False


def test_report_storage():
    """Test that reports are properly stored in database."""
    print("\n" + "="*60)
    print("TEST 3: Report Storage and Retrieval")
    print("="*60)

    if not os.getenv('GOOGLE_API_KEY'):
        print("⚠️  Skipping (requires API key)")
        return None

    try:
        service = AIProgressReportService()

        # Get latest report
        repo = AIProgressReportRepository()
        report = repo.get_latest_report(student_id=1)

        if report:
            print(f"✅ Found stored report (ID: {report['report_id']})")
            print(f"   Generated: {report['generated_at']}")
            print(f"   Has strengths: {bool(report['strengths'])}")
            print(f"   Has improvements: {bool(report['improvements'])}")
            print(f"   Has next steps: {bool(report['next_steps'])}")
            return True
        else:
            print("ℹ️  No stored reports found (this is okay for first run)")
            return None

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🧪 AI PROGRESS REPORTS - TEST SUITE")
    print("="*60)

    results = []

    # Test 1: Data retrieval (always runs)
    results.append(("Data Retrieval", test_student_data_retrieval()))

    # Test 2: AI generation (requires API key)
    results.append(("AI Generation", test_ai_report_generation()))

    # Test 3: Storage (requires API key)
    results.append(("Report Storage", test_report_storage()))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result is True)
    failed = sum(1 for _, result in results if result is False)
    skipped = sum(1 for _, result in results if result is None)

    for test_name, result in results:
        status = "✅ PASS" if result is True else "❌ FAIL" if result is False else "⚠️  SKIP"
        print(f"{status} - {test_name}")

    print(f"\nResults: {passed} passed, {failed} failed, {skipped} skipped")

    if failed > 0:
        print("\n❌ Some tests failed. Please review the output above.")
        sys.exit(1)
    else:
        print("\n✅ All available tests passed!")
        if skipped > 0:
            print(f"   ({skipped} test(s) skipped - add GOOGLE_API_KEY to test AI features)")


if __name__ == "__main__":
    main()
