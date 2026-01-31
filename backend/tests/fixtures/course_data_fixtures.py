"""Fixtures for course data and test samples"""

import pytest
from models import Course, CourseChunk, Lesson, Source


@pytest.fixture
def sample_lesson():
    """Create a single sample lesson"""
    return Lesson(
        lesson_number=1,
        title="Introduction to Testing",
        lesson_link="https://example.com/course/lesson1",
    )


@pytest.fixture
def sample_lessons():
    """Create a list of sample lessons"""
    return [
        Lesson(
            lesson_number=1,
            title="Introduction to Testing",
            lesson_link="https://example.com/course/lesson1",
        ),
        Lesson(
            lesson_number=2,
            title="Unit Testing Basics",
            lesson_link="https://example.com/course/lesson2",
        ),
        Lesson(
            lesson_number=3,
            title="Integration Testing",
            lesson_link="https://example.com/course/lesson3",
        ),
    ]


@pytest.fixture
def sample_course(sample_lessons):
    """Create a complete sample course with lessons"""
    return Course(
        title="Python Testing Course",
        course_link="https://example.com/course",
        instructor="Test Instructor",
        lessons=sample_lessons,
    )


@pytest.fixture
def course_without_lessons():
    """Create a course without lessons for edge case testing"""
    return Course(
        title="Empty Course",
        course_link="https://example.com/empty",
        instructor="Test Instructor",
        lessons=[],
    )


@pytest.fixture
def sample_course_chunks():
    """Create sample course chunks for vector operations"""
    return [
        CourseChunk(
            content="This is the first chunk of content about testing basics.",
            course_title="Python Testing Course",
            lesson_number=1,
            chunk_index=0,
        ),
        CourseChunk(
            content="This is the second chunk covering unit test fundamentals.",
            course_title="Python Testing Course",
            lesson_number=1,
            chunk_index=1,
        ),
        CourseChunk(
            content="Integration testing requires multiple components working together.",
            course_title="Python Testing Course",
            lesson_number=2,
            chunk_index=0,
        ),
    ]


@pytest.fixture
def sample_course_document_content():
    """Create sample document text for processor testing"""
    return """Course: Python Testing Course
Link: https://example.com/course
Instructor: Test Instructor

Lesson 1: Introduction to Testing
Link: https://example.com/course/lesson1

This is the introduction to testing. Testing is essential for software quality.
We will cover various testing approaches and methodologies.

Lesson 2: Unit Testing Basics
Link: https://example.com/course/lesson2

Unit testing focuses on testing individual components in isolation.
Each test should be independent and fast.
"""


@pytest.fixture
def sample_sources():
    """Create sample Source objects for UI"""
    return [
        Source(
            text="Python Testing Course - Lesson 1",
            url="https://example.com/course/lesson1",
        ),
        Source(
            text="Python Testing Course - Lesson 2",
            url="https://example.com/course/lesson2",
        ),
    ]


@pytest.fixture
def multiple_courses():
    """Create multiple courses for search testing"""
    return [
        Course(
            title="Python Testing Course",
            course_link="https://example.com/python",
            instructor="Test Instructor",
            lessons=[
                Lesson(
                    lesson_number=1,
                    title="Intro",
                    lesson_link="https://example.com/python/1",
                ),
                Lesson(
                    lesson_number=2,
                    title="Advanced",
                    lesson_link="https://example.com/python/2",
                ),
            ],
        ),
        Course(
            title="MCP Introduction",
            course_link="https://example.com/mcp",
            instructor="MCP Instructor",
            lessons=[
                Lesson(
                    lesson_number=1,
                    title="Getting Started",
                    lesson_link="https://example.com/mcp/1",
                ),
                Lesson(
                    lesson_number=2,
                    title="Deep Dive",
                    lesson_link="https://example.com/mcp/2",
                ),
            ],
        ),
    ]
