"""
AI Progress Report Service - Groq API integration.
Author: Autumn Erwin
"""
import os
import re
import requests
from typing import Dict, Any, Optional
from src.features.ai_progress_reports.repository import AIProgressReportRepository
from src.features.ai_progress_reports.prompts import create_progress_report_prompt


class AIProgressReportService:
    """Handles AI-powered progress report generation using Groq free API."""

    def __init__(self):
        """
        Initialize the AI Progress Report Service.
        Uses Groq free API with user's API token.
        """
        self.repository = AIProgressReportRepository()

        # Get Groq API token from environment
        self.groq_token = os.getenv('GROQ_API_TOKEN')
        if not self.groq_token:
            raise ValueError(
                "Groq API token not found. Please set GROQ_API_TOKEN in your .env file. "
                "Get a free token at https://console.groq.com/keys"
            )

        # Groq API endpoint
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.timeout = 30

    def generate_progress_report(
        self,
        student_id: int,
        course_id: Optional[int] = None,
        force_regenerate: bool = False
    ) -> Dict[str, Any]:
        """
        Generate an AI progress report for a student.

        Args:
            student_id: Student's ID
            course_id: Optional course ID. If None, generates aggregate report.
            force_regenerate: If True, regenerates even if recent report exists

        Returns:
            Dictionary with report data and metadata
        """
        # Check for existing recent report (unless force regenerate)
        if not force_regenerate:
            existing_report = self.repository.get_latest_report(student_id, course_id)
            if existing_report:
                return {
                    'success': True,
                    'from_cache': True,
                    'report_id': existing_report['report_id'],
                    'generated_at': existing_report['generated_at'],
                    'report_text': existing_report['report_text'],
                    'strengths': existing_report['strengths'],
                    'improvements': existing_report['improvements'],
                    'next_steps': existing_report['next_steps'],
                }

        # Get student performance data
        performance_data = self.repository.get_student_performance_data(student_id, course_id)

        if not performance_data.get('has_data'):
            return {
                'success': False,
                'error': 'Insufficient data to generate report. Student needs grades first.'
            }

        # Create the prompt
        prompt = create_progress_report_prompt(
            student_name=performance_data['student_name'],
            course_name=performance_data['course_name'],
            grade_level=str(performance_data['grade_level']),
            current_average=performance_data['current_average'],
            num_assignments=performance_data['num_assignments'],
            trend_description=performance_data['trend_description'],
            recent_grades=performance_data['recent_grades'],
            teacher_comments=performance_data['teacher_comments'],
            class_average=performance_data['class_average'],
            performance_compared_to_class=performance_data['performance_compared_to_class'],
        )

        try:
            # Call Groq API with chat format
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.groq_token}"
            }
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt.template if hasattr(prompt, 'template') else str(prompt)
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 1024,
            }

            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )

            if response.status_code != 200:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', 'API request failed')
                return {
                    'success': False,
                    'error': f'Failed to generate report: {error_msg}'
                }

            result = response.json()

            # Extract text from Groq response
            report_text = result.get('choices', [{}])[0].get('message', {}).get('content', '')

            if not report_text:
                return {
                    'success': False,
                    'error': 'No report generated. Please try again.'
                }

            # Parse sections from the generated report
            sections = self._parse_report_sections(report_text)

            # Save to database
            report_id = self.repository.save_generated_report(
                student_id=student_id,
                course_id=course_id,
                report_text=report_text,
                strengths=sections['strengths'],
                improvements=sections['improvements'],
                next_steps=sections['next_steps'],
            )

            return {
                'success': True,
                'from_cache': False,
                'report_id': report_id,
                'generated_at': 'just now',
                'report_text': report_text,
                'strengths': sections['strengths'],
                'improvements': sections['improvements'],
                'next_steps': sections['next_steps'],
                'performance_data': performance_data,  # Include for context
            }

        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'AI report generation timed out. Please try again or check your internet connection.'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to generate report: {str(e)}'
            }

    def _parse_report_sections(self, report_text: str) -> Dict[str, str]:
        """
        Parse the generated report into sections.

        Args:
            report_text: The full generated report

        Returns:
            Dictionary with strengths, improvements, and next_steps
        """
        sections = {
            'strengths': '',
            'improvements': '',
            'next_steps': ''
        }

        # Use regex to extract sections
        strengths_match = re.search(r'STRENGTHS:\s*(.*?)(?=AREAS FOR IMPROVEMENT:|$)', report_text, re.DOTALL | re.IGNORECASE)
        if strengths_match:
            sections['strengths'] = strengths_match.group(1).strip()

        improvements_match = re.search(r'AREAS FOR IMPROVEMENT:\s*(.*?)(?=NEXT STEPS:|$)', report_text, re.DOTALL | re.IGNORECASE)
        if improvements_match:
            sections['improvements'] = improvements_match.group(1).strip()

        next_steps_match = re.search(r'NEXT STEPS:\s*(.*?)$', report_text, re.DOTALL | re.IGNORECASE)
        if next_steps_match:
            sections['next_steps'] = next_steps_match.group(1).strip()

        return sections

    def get_student_reports_history(self, student_id: int) -> list:
        """
        Get all historical reports for a student.

        Args:
            student_id: Student's ID

        Returns:
            List of report dictionaries
        """
        query = """
            SELECT
                r.report_id,
                r.generated_at,
                r.strengths,
                r.improvements,
                r.next_steps,
                c.course_name
            FROM AIReports r
            LEFT JOIN Courses c ON r.course_id = c.course_id
            WHERE r.student_id = ?
            ORDER BY r.generated_at DESC
        """

        from config.database import db_manager
        import pandas as pd

        with db_manager.get_connection() as conn:
            df = pd.read_sql_query(query, conn, params=(student_id,))

        return df.to_dict('records') if not df.empty else []
