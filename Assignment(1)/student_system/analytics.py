from models.student import Student

def get_top_performing(students):
    if not students:
        return None
    return max(students, key=lambda s: s.calculate_average())

def get_lowest_performing(students):
    if not students:
        return None
    return min(students, key=lambda s: s.calculate_average())

def get_student_rankings(students):
    return sorted(students, key=lambda s: s.calculate_average(), reverse=True)

def get_grade_distribution(students):
    distribution = {
        "Excellent": 0,
        "Very Good": 0,
        "Good": 0,
        "Pass": 0,
        "Fail": 0
    }
    
    for student in students:
        category = student.grade_category()
        if category in distribution:
            distribution[category] += 1
            
    return distribution