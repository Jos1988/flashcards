import csv
import json
import jsonpickle
from os import listdir, path
from typing import List


class Question:
    def __init__(self, question: str, correct_answer: str) -> None:
        self.question = question
        self.correct_answer = correct_answer
        self.num_correct = 0
        self.num_incorrect = 0

    def check_answer(self, user_answer: str) -> bool:
        if user_answer.lower() == self.correct_answer.lower():
            self.num_correct += 1
            return True
        self.num_incorrect += 1
        return False


class QuestionsSaver:
    def __init__(self, save_file: str):
        self.save_file = save_file

    def is_saved(self) -> bool:
        return path.exists(self.save_file)

    def load_save(self) -> List[Question]:
        if not self.is_saved():
            print('Quiz has no save.')
            return []

        with open(self.save_file, 'r') as file:
            return jsonpickle.decode(json.load(file), classes=Question)

    def save(self, questions: List[Question]):
        with open(self.save_file, 'w') as file:
            json.dump(jsonpickle.encode(questions), file)


class Quiz:
    """ Quiz object for taking the quiz, and persisting results. """

    def __init__(self, questions: List[Question], saver: QuestionsSaver, min_correct: int = 1) -> None:
        """
        Args:
             questions: list of questions.
             saver: saver object for loading and saving quiz.
             min_correct: Minimum number of times an answer has to be answered correctly for the question to be considered learned. This will prevent the
             question from being asked again.
        """
        self.questions = questions
        self.saver = saver
        self.min_correct = min_correct
        if self.saver.is_saved():
            self.questions = self.saver.load_save()

    def ask_question(self, question: Question):
        print(question.question)
        user_answer = input("Enter your answer: ")
        is_correct = question.check_answer(user_answer)
        if is_correct:
            print("Correct!")
            return

        print(f"Incorrect, the answer was: {question.correct_answer}.")

    def get_incorrect_questions(self) -> list[Question | None]:
        return [question for question in self.questions if question.num_correct < self.min_correct]

    def get_quiz_score(self):
        return sum([int(question.num_correct >= self.min_correct) for question in self.questions])

    def print_score(self):
        score = self.get_quiz_score()
        print(f'{score} correct questions out of {len(self.questions)}')

    def take_quiz(self) -> None:
        while True:
            incorrect_questions = self.get_incorrect_questions()
            if len(incorrect_questions) == 0:
                break

            for question in incorrect_questions:
                self.saver.save(self.questions)
                self.ask_question(question)
                self.print_score()

        self.saver.save(self.questions)
        print(f'-- finished. --')
        self.print_score()

    def write_results(self, filename: str) -> None:
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


def ask_quiz():
    print('Quizzes available:')
    available_quizzes = {i: quiz for i, quiz in enumerate(listdir('data/questions')) if '.csv' in quiz}

    print("Available quizzes:")
    for i, quiz in available_quizzes.items():
        print(f"{i + 1}: {quiz.replace('.csv', '')}")
    while True:
        choice = int(input("Enter the number of the file you want to choose: "))
        if choice not in available_quizzes.keys():
            chosen_quiz = available_quizzes[choice - 1]
            break

        print(f"Invalid choice. Please enter a number between 1 and {max(available_quizzes.keys())}")
    return chosen_quiz


def main() -> None:
    username = input('Player name: ')

    chosen_quiz_file = ask_quiz()

    questions = load_questions('data/questions/' + chosen_quiz_file)
    saver = QuestionsSaver(save_file=f"data/saves/{username}_{chosen_quiz_file.replace('.csv', '')}_save.json")
    quiz = Quiz(questions, saver,  min_correct=2)
    quiz.take_quiz()


if __name__ == "__main__":
    main()
