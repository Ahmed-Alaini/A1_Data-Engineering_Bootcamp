
import csv
from models.student import Student


def load_students(filename):
    students = []

    try:
        with open(filename, "r") as file:
            reader = csv.reader(file)
            for row in reader:
                student = Student.from_csv(row)
                students.append(student)
    except FileNotFoundError:
        print("File not found. Starting with empty data")

    return students


def save_students(filename, students):
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)

        for s in students:
            grades_str = "|".join(map(str, s.grades))
            writer.writerow([s.name, s.student_id, grades_str])


def validate_number(value):
    try:
        return float(value)
    except ValueError:
        return None