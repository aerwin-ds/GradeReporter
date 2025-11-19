"""
Prompt templates for AI progress report generation.
Author: Autumn Erwin
"""
from langchain_core.prompts import ChatPromptTemplate

PROGRESS_REPORT_TEMPLATE = """You are an experienced educational advisor analyzing student performance data.
Your goal is to generate a personalized, encouraging, and actionable progress report.

**Student Information:**
- Name: {student_name}
- Course: {course_name}
- Grade Level: {grade_level}

**Performance Data:**
- Current Average: {current_average}%
- Number of Assignments: {num_assignments}
- Performance Trend: {trend_description}
- Recent Grades: {recent_grades}

**Teacher Comments:**
{teacher_comments}

**Class Context:**
- Class Average: {class_average}%
- Student's Ranking: {performance_compared_to_class}

---

Generate a comprehensive progress report with the following sections:

**1. STRENGTHS (2-3 sentences)**
Identify what the student is doing well. Be specific about achievements and positive patterns.

**2. AREAS FOR IMPROVEMENT (2-3 sentences)**
Identify risks or challenges the student is facing. Be constructive and specific about what needs attention.

**3. NEXT STEPS (3-5 actionable items)**
Provide concrete, specific recommendations for improvement. Each should be:
- Actionable (student can do it)
- Specific (clear what to do)
- Relevant to their current performance

**Guidelines:**
- Keep the tone encouraging and supportive
- Use specific data points from the performance data
- Make recommendations concrete and achievable
- Focus on growth mindset language
- Be honest about challenges while remaining constructive

Format your response as follows:

STRENGTHS:
[Your analysis here]

AREAS FOR IMPROVEMENT:
[Your analysis here]

NEXT STEPS:
1. [First actionable step]
2. [Second actionable step]
3. [Third actionable step]
4. [Fourth actionable step (if applicable)]
5. [Fifth actionable step (if applicable)]
"""

# Create the prompt template
progress_report_prompt = ChatPromptTemplate.from_template(PROGRESS_REPORT_TEMPLATE)


def create_progress_report_prompt(
    student_name: str,
    course_name: str,
    grade_level: str,
    current_average: float,
    num_assignments: int,
    trend_description: str,
    recent_grades: str,
    teacher_comments: str,
    class_average: float,
    performance_compared_to_class: str,
) -> ChatPromptTemplate:
    """
    Create a formatted progress report prompt with student data.

    Args:
        student_name: Student's full name
        course_name: Name of the course
        grade_level: Student's grade level
        current_average: Current grade average (0-100)
        num_assignments: Number of graded assignments
        trend_description: Description of grade trend (e.g., "improving", "declining", "stable")
        recent_grades: Formatted string of recent grades
        teacher_comments: Combined teacher comments
        class_average: Average grade for the class
        performance_compared_to_class: Description of how student compares to class

    Returns:
        Formatted ChatPromptTemplate ready for LLM
    """
    return progress_report_prompt.partial(
        student_name=student_name,
        course_name=course_name,
        grade_level=grade_level,
        current_average=f"{current_average:.1f}",
        num_assignments=num_assignments,
        trend_description=trend_description,
        recent_grades=recent_grades,
        teacher_comments=teacher_comments if teacher_comments else "No comments provided.",
        class_average=f"{class_average:.1f}",
        performance_compared_to_class=performance_compared_to_class,
    )
