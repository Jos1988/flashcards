import csv
from typing import List, Tuple


class Question:
    def __init__(self, question: str, correct_answer: str) -> None:
        self.question = question
        self.correct_answer = correct_answer
        self.num_correct = 0
        self.num_incorrect = 0

    def check_answer(self, user_answer: str) -> bool:
        if user_answer == self.correct_answer:
            self.num_correct += 1
            return True
        self.num_incorrect += 1
        return False


class Quiz:
    def __init__(self, questions: List[Question]) -> None:
        self.questions = questions

    def take_quiz(self) -> None:
        for q in self.questions:
            print(q.question)
            user_answer = input("Enter your answer: ")
            result = q.check_answer(user_answer)
            if result:
                print("Correct!")
            else:
                print("Incorrect.")

    def save_results(self, filename: str) -> None:
        with open(filename, "w") as f:
            for q in self.questions:
                f.write(f"{q.question}: {q.num_correct} correct, {q.num_incorrect} incorrect\n")


def load_questions(filename: str) -> List[Question]:
    questions = []
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            question = row[0]
            correct_answer = row[1]
            q = Question(question, correct_answer)
            questions.append(q)
    return questions


def main() -> None:
    questions = load_questions("questions.csv")
    quiz = Quiz(questions)
    quiz.take_quiz()
    quiz.save_results("results.txt")


if __name__ == "__main__":
    main()
