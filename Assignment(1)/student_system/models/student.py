
class Student:
    def __init__(self, name, student_id, grades: list):   
        self.__name = name
        self.__student_id = student_id
        self.__grades = grades  

    @property
    def name(self):
        return self.__name

    @property
    def student_id(self):
        return self.__student_id

    @property
    def grades(self):
        return self.__grades
    
    def calculate_average(self):    
        if not self.__grades:        # To check if grades empty to aviod division by zero
            return 0
        return sum(self.__grades) / len(self.__grades)
            
    def grade_category(self):
        avg = self.calculate_average()
        
        if avg >= 85:
            return "Excellent"
        elif avg >= 75:
            return "Very Good"
        elif avg >= 65:
            return "Good"
        elif avg >= 50:
            return "Pass"
       
        return "Fail"
        
    @classmethod
    def from_csv(cls, row):
        name, student_id, grades_str = row
        grades = list(map(float, grades_str.split("|")))
        return cls(name, student_id, grades)

    @staticmethod
    def validate_grades(grades):
        return all(0 <= g <= 100 for g in grades)
