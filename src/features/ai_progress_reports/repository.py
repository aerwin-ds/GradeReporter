"""
Repository layer for AI progress reports - handles data retrieval.
Author: Autumn Erwin
"""
import pandas as pd
from typing import Dict, Any, Optional, List
from datetime import datetime
from config.database import db_manager


class AIProgressReportRepository:
    """Handles database operations for AI progress reports."""

    def get_student_performance_data(self, student_id: int, course_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get comprehensive performance data for a student.

        Args:
            student_id: Student's ID
            course_id: Optional specific course ID. If None, aggregates all courses.

        Returns:
            Dictionary with student performance metrics
        """
        # Get student basic info
        student_info = self._get_student_info(student_id)

        # Get grades data
        grades_df = self._get_student_grades(student_id, course_id)

        if grades_df.empty:
            return {
                'student_name': student_info['name'],
                'grade_level': student_info['grade_level'],
                'has_data': False,
            }

        # Calculate metrics
        current_average = grades_df['grade'].mean()
        num_assignments = len(grades_df)

        # Get trend analysis
        trend_info = self._calculate_trend(grades_df)

        # Get recent grades (last 5)
        recent_grades = self._format_recent_grades(grades_df.head(5))

        # Get teacher comments
        teacher_comments = self._get_teacher_comments(grades_df)

        # Get class average for comparison
        class_average = self._get_class_average(course_id) if course_id else current_average

        # Calculate performance comparison
        performance_comparison = self._compare_to_class(current_average, class_average)

        return {
            'student_id': student_id,
            'student_name': student_info['name'],
            'grade_level': student_info['grade_level'],
            'course_name': grades_df['course_name'].iloc[0] if course_id else "All Courses",
            'current_average': current_average,
            'num_assignments': num_assignments,
            'trend_description': trend_info['description'],
            'trend_slope': trend_info['slope'],
            'recent_grades': recent_grades,
            'teacher_comments': teacher_comments,
            'class_average': class_average,
            'performance_compared_to_class': performance_comparison,
            'has_data': True,
        }

    def _get_student_info(self, student_id: int) -> Dict[str, Any]:
        """Get basic student information."""
        query = """
            SELECT u.name, s.grade_level
            FROM Students s
            JOIN Users u ON s.user_id = u.user_id
            WHERE s.student_id = ?
        """
        with db_manager.get_connection() as conn:
            result = pd.read_sql_query(query, conn, params=(student_id,))
            if result.empty:
                return {'name': 'Unknown Student', 'grade_level': 'N/A'}
            return {
                'name': result['name'].iloc[0],
                'grade_level': result['grade_level'].iloc[0] if pd.notna(result['grade_level'].iloc[0]) else 'N/A'
            }

    def _get_student_grades(self, student_id: int, course_id: Optional[int] = None) -> pd.DataFrame:
        """Get student's grades with optional course filter."""
        if course_id:
            query = """
                SELECT
                    g.grade,
                    g.assignment_name,
                    g.date_assigned,
                    c.course_name
                FROM Grades g
                JOIN Courses c ON g.course_id = c.course_id
                WHERE g.student_id = ? AND g.course_id = ?
                ORDER BY g.date_assigned DESC
            """
            params = (student_id, course_id)
        else:
            query = """
                SELECT
                    g.grade,
                    g.assignment_name,
                    g.date_assigned,
                    c.course_name
                FROM Grades g
                JOIN Courses c ON g.course_id = c.course_id
                WHERE g.student_id = ?
                ORDER BY g.date_assigned DESC
            """
            params = (student_id,)

        with db_manager.get_connection() as conn:
            df = pd.read_sql_query(query, conn, params=params)
            # Add empty comments column for compatibility
            df['comments'] = None
            return df

    def _calculate_trend(self, grades_df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate grade trend (improving, stable, declining)."""
        if len(grades_df) < 3:
            return {'description': 'insufficient data for trend analysis', 'slope': 0}

        # Sort by date (oldest to newest) for trend calculation
        sorted_df = grades_df.sort_values('date_assigned')

        # Simple linear regression on recent grades (last 5)
        recent = sorted_df.tail(5)
        x = list(range(len(recent)))
        y = recent['grade'].tolist()

        # Calculate slope
        n = len(x)
        slope = (n * sum(x[i] * y[i] for i in range(n)) - sum(x) * sum(y)) / (n * sum(x[i]**2 for i in range(n)) - sum(x)**2)

        # Categorize trend
        if slope > 2:
            description = "improving steadily"
        elif slope > 0.5:
            description = "slightly improving"
        elif slope < -2:
            description = "declining"
        elif slope < -0.5:
            description = "slightly declining"
        else:
            description = "stable"

        return {'description': description, 'slope': slope}

    def _format_recent_grades(self, recent_df: pd.DataFrame) -> str:
        """Format recent grades as a readable string."""
        if recent_df.empty:
            return "No recent grades available."

        grades_list = []
        for _, row in recent_df.iterrows():
            grades_list.append(f"{row['assignment_name']}: {row['grade']:.1f}%")

        return ", ".join(grades_list)

    def _get_teacher_comments(self, grades_df: pd.DataFrame) -> str:
        """Extract and combine teacher comments."""
        comments = grades_df['comments'].dropna()
        if comments.empty:
            return "No teacher comments available."

        # Take the most recent 3 comments
        recent_comments = comments.head(3).tolist()
        return " | ".join(recent_comments)

    def _get_class_average(self, course_id: int) -> float:
        """Get the class average for a specific course."""
        query = """
            SELECT AVG(g.grade) as class_avg
            FROM Grades g
            WHERE g.course_id = ?
        """
        with db_manager.get_connection() as conn:
            result = pd.read_sql_query(query, conn, params=(course_id,))
            if result.empty or pd.isna(result['class_avg'].iloc[0]):
                return 0.0
            return float(result['class_avg'].iloc[0])

    def _compare_to_class(self, student_avg: float, class_avg: float) -> str:
        """Generate a comparison description."""
        diff = student_avg - class_avg

        if diff > 10:
            return "performing well above class average"
        elif diff > 5:
            return "performing above class average"
        elif diff > -5:
            return "performing at class average"
        elif diff > -10:
            return "performing below class average"
        else:
            return "performing well below class average"

    def save_generated_report(
        self,
        student_id: int,
        course_id: Optional[int],
        report_text: str,
        strengths: str,
        improvements: str,
        next_steps: str,
    ) -> int:
        """
        Save a generated AI report to the database.

        Args:
            student_id: Student's ID
            course_id: Course ID (None for aggregate report)
            report_text: Full generated report text
            strengths: Extracted strengths section
            improvements: Extracted improvements section
            next_steps: Extracted next steps section

        Returns:
            report_id of the saved report
        """
        query = """
            INSERT INTO AIReports (
                student_id, course_id, generated_at, report_text,
                strengths, improvements, next_steps
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                query,
                (
                    student_id,
                    course_id,
                    datetime.now().isoformat(),
                    report_text,
                    strengths,
                    improvements,
                    next_steps,
                )
            )
            conn.commit()
            return cursor.lastrowid

    def get_latest_report(self, student_id: int, course_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Get the most recent AI report for a student.

        Args:
            student_id: Student's ID
            course_id: Optional course ID

        Returns:
            Report dictionary or None if no report exists
        """
        if course_id:
            query = """
                SELECT * FROM AIReports
                WHERE student_id = ? AND course_id = ?
                ORDER BY generated_at DESC
                LIMIT 1
            """
            params = (student_id, course_id)
        else:
            query = """
                SELECT * FROM AIReports
                WHERE student_id = ? AND course_id IS NULL
                ORDER BY generated_at DESC
                LIMIT 1
            """
            params = (student_id,)

        with db_manager.get_connection() as conn:
            result = pd.read_sql_query(query, conn, params=params)
            if result.empty:
                return None
            return result.iloc[0].to_dict()
