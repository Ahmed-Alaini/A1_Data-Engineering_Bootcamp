# main.py

import os
from models.student import Student
from models.classroom import Classroom
from analytics import *
from utils import *

DATA_FILE = "data.csv"


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(header_name):
    width = 80
    print("\n" + "=" * width)
    print(f"{header_name}".center(width))
    print("=" * width + "\n")


def display_menu():
    print_header("Student Performance Analyzer System")
    print("    1- Add New Student")
    print("    2- Delete Student")
    print("    3- Search Student by ID")
    print("    4- View Top Performing Student")
    print("    5- View Lowest Performing Student")
    print("    6- View Student Rankings")
    print("    7- View Grade Distribution")
    print("    8- View Classroom Average")
    print("    9- Exit")


def main():
    classroom = Classroom()

    # Load data
    students_data = load_students(DATA_FILE)
    for s in students_data:
        try:
            classroom.add_student(s)
        except ValueError:
            pass # Skip duplicates if any in file

    while True:
        clear_screen()
        display_menu()
        
        choice = input("\nSelect an Option (1-9): ")

        match choice:
            case '1':
                clear_screen()
                print_header("Add New Student")
                try:
                    name = input("Enter name: ")
                    student_id = input("Enter ID: ")
                    
                    grades = []
                    for i in range(1, 5):
                        while True:
                            val = input(f"Enter grade for Year {i}: ")
                            # Use utility to validate and convert to float
                            grade = validate_number(val)
                            if grade is not None and 0 <= grade <= 100:
                                grades.append(grade)
                                break
                            else:
                                print("\n Invalid input. Please enter a number between 0 and 100.")

                    student = Student(name, student_id, grades)
                    classroom.add_student(student)
                    save_students(DATA_FILE, classroom.students)
                    print("\nStudent added successfully and saved.")
                except Exception as e:
                    print(f"\n [!] Error: {e}")
                input("\nPress Enter to continue...")

            case '2':
                clear_screen()
                print_header("Delete Student")
                student_id = input("Enter student ID to remove: ")
                student = classroom.search_student_by_id(student_id)
                
                if student:
                    print(f"\nStudent Found: {student.name} (ID: {student.student_id})")
                    confirm = input("Are you sure you want to delete this student? (y/n): ").lower()
                    
                    if confirm == 'y':
                        classroom.remove_student(student_id)
                        save_students(DATA_FILE, classroom.students)
                        print("\n [+] Student removed successfully and saved.")
                    else:
                        print("\n [-] Deletion cancelled.")
                else:
                    print("\n [!] Student not found.")
                input("\nPress Enter to continue...")

            case '3':
                clear_screen()
                print_header("Search Student")
                student_id = input("Enter student ID to search: ")
                student = classroom.search_student_by_id(student_id)
                if student:
                    # Convert grades to integers for display as requested
                    int_grades = [int(g) for g in student.grades]
                    print(f"\nFound: {student.name}")
                    print(f"ID: {student.student_id}")
                    print(f"Grades: {int_grades}")
                    print(f"Average: {student.calculate_average():.2f}")
                    print(f"Category: {student.grade_category()}")
                else:
                    print("\n Student not found.")
                input("\nPress Enter to continue...")

            case '4':
                clear_screen()
                print_header("Top Performing Student")
                student = get_top_performing(classroom.students)
                if student:
                    print(f"\nTop Student: {student.name}")
                    print(f"Average: {student.calculate_average():.2f}")
                else:
                    print("\nNo students found.")
                input("\nPress Enter to continue...")

            case '5':
                clear_screen()
                print_header("Lowest Performing Student")
                student = get_lowest_performing(classroom.students)
                if student:
                    print(f"\nLowest Student: {student.name}")
                    print(f"Average: {student.calculate_average():.2f}")
                else:
                    print("\n No students found.")
                input("\nPress Enter to continue...")

            case '6':
                clear_screen()
                print_header("Student Rankings")
                ranked = get_student_rankings(classroom.students)
                if ranked:
                    print("\nRankings:")
                    for i, s in enumerate(ranked, 1):
                        print(f"{i}. {s.name:<15} | Average: {s.calculate_average():.2f}")
                else:
                    print("\nNo students found.")
                input("\nPress Enter to continue...")

            case '7':
                clear_screen()
                print_header("Grade Distribution")
                dist = get_grade_distribution(classroom.students)
                print("\nDistribution:")
                for category, count in dist.items():
                    print(f"{category:<12}: {count}")
                input("\nPress Enter to continue...")

            case '8':
                clear_screen()
                print_header("Classroom Average")
                avg = classroom.calculate_classroom_average()
                print(f"\nTotal Classroom Average: {avg:.2f}")
                input("\nPress Enter to continue...")

            case '9':
                save_students(DATA_FILE, classroom.students)
                print("\n Goodbye!")
                break

            case _:
                print("\n Invalid choice. Please try again.")
                input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
