
from .student import Student

class Classroom:
    def __init__(self):
        self.__students = []

    @property
    def students(self):
        return self.__students

    def search_student_by_id(self, student_id: str):
        for student in self.__students:
            if student.student_id == student_id:
                return student
        return None

    def add_student(self, student: Student): # Type hint of Student object
        if self.search_student_by_id(student.student_id):
            raise ValueError(
                f"A student with ID '{student.student_id}' already exists."
            )
        self.__students.append(student)

    def remove_student(self, student_id):
        student = self.search_student_by_id(student_id)

        if student:
            self.__students.remove(student)
            return True
        return False

    def calculate_classroom_average(self):
        if not self.__students:
            return 0.0

        total = sum(student.calculate_average() for student in self.__students)
        return total / len(self.__students)