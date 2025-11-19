"""
AI Progress Report Service - LangChain + Google Gemini integration.
Author: Autumn Erwin
"""
import os
import re
from typing import Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from src.features.ai_progress_reports.repository import AIProgressReportRepository
from src.features.ai_progress_reports.prompts import create_progress_report_prompt


class AIProgressReportService:
    """Handles AI-powered progress report generation using Google Gemini."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the AI Progress Report Service.

        Args:
            api_key: Google API key. If None, reads from GOOGLE_API_KEY env var.
        """
        self.repository = AIProgressReportRepository()

        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')

        if not self.api_key:
            raise ValueError(
                "Google API key not found. Please set GOOGLE_API_KEY environment variable "
                "or pass it to the constructor."
            )

        # Initialize Gemini model
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=self.api_key,
            temperature=0.7,  # Balanced creativity
            max_output_tokens=2048,
        )

        # Output parser
        self.output_parser = StrOutputParser()

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

        # Create the LangChain chain
        chain = prompt | self.llm | self.output_parser

        try:
            # Generate the report
            report_text = chain.invoke({})

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
