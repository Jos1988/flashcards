import csv
import json
import random
from os import listdir, path
from typing import List, Union

import jsonpickle
import Levenshtein as lev


class Question:
    """
    Class representing a single quiz question, including the correct answer, as well as the number of times the question has been answered correctly
    and incorrectly.
    """

    def __init__(self, question: str, correct_answer: str) -> None:
        """
        Args:
            question: The text of the question.
            correct_answer: The correct answer to the question.
        """
        self.question = question
        self.correct_answer = correct_answer
        self.num_correct = 0
        self.num_incorrect = 0

    def check_answer(self, user_answer: str) -> bool:
        """
        Check if the user's answer is correct and update the question's
        num_correct and num_incorrect values accordingly.

        Note: The given answer may deviate a little from the correct answer to allow for typing errors.

        Args:
            user_answer: The user's answer to the question.

        Returns:
            True if the user's answer is correct, False otherwise.
        """
        if lev.distance(user_answer.lower(), self.correct_answer.lower()) <= 1:
            self.num_correct += 1
            return True
        self.num_incorrect += 1
        return False


class QuestionsSaver:
    """
    Class for saving and loading a list of quiz questions to and from a file.
    """

    def __init__(self, save_file: str):
        """
        Args:
            save_file: The file path to save the questions to.
        """
        self.save_file = save_file

    def is_saved(self) -> bool:
        """
        Check if the save file exists.

        Returns:
            True if the save file exists, False otherwise.
        """
        return path.exists(self.save_file)

    def load_save(self) -> List[Question]:
        """
        Load the saved questions from the save file.

        Returns:
            A list of Question objects loaded from the save file.
        """
        if not self.is_saved():
            print('Quiz has no save.')
            return []

        with open(self.save_file, 'r') as file:
            return jsonpickle.decode(json.load(file), classes=Question)

    def save(self, questions: List[Question]):
        """
        Save the given list of questions to the save file.

        Args:
            questions: A list of Question objects to save.
        """
        with open(self.save_file, 'w') as file:
            json.dump(jsonpickle.encode(questions), file)


class Quiz:
    """
    Quiz object for taking the quiz, and persisting results.
    """

    def __init__(self, questions: List[Question], saver: QuestionsSaver, result_path: str, min_correct: int = 1) -> None:
        """
        Initialize the Quiz object with a list of questions, a QuestionsSaver object, and an optional minimum number of correct answers required to
        consider a question "learned". If a save file exists, the quiz will be initialized with the saved questions.

        Args:
            questions: A list of Question objects representing the questions
                       in the quiz.
            saver: A QuestionsSaver object for loading and saving the quiz.
            result_path: Path to file where quiz results are stored in a readable format.
            min_correct: The minimum number of times an answer must be given
                         correctly to consider the question "learned". This
                         will prevent the question from being asked again.
                         Defaults to 1.
        """
        self.questions = questions
        self.saver = saver
        self.min_correct = min_correct
        self.result_path = result_path
        if self.saver.is_saved():
            self.questions = self.saver.load_save()

    def ask_question(self, question: Question):
        """
        Ask the user the given question and check if their answer is correct.

        Args:
            question: The Question object to ask.
        """
        print(question.question)
        user_answer = input("Enter your answer: ")
        is_correct = question.check_answer(user_answer)
        if not is_correct:
            print(f"Incorrect, the answer was: {question.correct_answer}.")
            return

        print("Correct!")

        if question.num_correct >= self.min_correct:
            print(f'Question correct {self.min_correct} times, it wont be asked again.')

    def get_incorrect_questions(self) -> List[Union[Question, None]]:
        """
        Get a list of all questions that have not been answered correctly at least min_correct times.

        Returns:
            A list of Question objects that have not been answered correctly
            at least min_correct times.
        """
        return [question for question in self.questions if question.num_correct < self.min_correct]

    def get_quiz_score(self):
        """
        Get the number of questions in the quiz that have been answered
        correctly at least min_correct times.

        Returns:
            The number of questions in the quiz that have been answered
            correctly at least min_correct times.
        """
        return sum([question.num_correct for question in self.questions])

    def print_score(self):
        """
        Print the number of questions in the quiz that have been answered
        correctly at least min_correct times.
        """
        score = self.get_quiz_score()
        print(f'{score} correct answers out of {len(self.questions) * self.min_correct} required correct answers')

    def write_results(self) -> None:
        """
        Print results from the quiz to the 'results' folder.
        """
        with open(self.result_path, "w") as f:
            for question in self.questions:
                f.write(f"{question.question}: {question.num_correct} correct, {question.num_incorrect} incorrect\n")

    def take_quiz(self) -> None:
        """
        Take the quiz, asking all questions that have not been answered correctly at least min_correct times, until there are no more
        such questions. Save the quiz after each question.
        """
        while True:
            incorrect_questions = self.get_incorrect_questions()
            random.shuffle(incorrect_questions)
            if len(incorrect_questions) == 0:
                break

            for question in incorrect_questions:
                self.saver.save(self.questions)
                self.ask_question(question)
                self.print_score()
                self.write_results()

        self.saver.save(self.questions)
        print(f'-- finished. --')
        self.print_score()
        self.write_results()


def load_questions(filename: str) -> List[Question]:
    """
    Load a list of quiz questions from a CSV file.

    Args:
        filename: The file path of the CSV file to load questions from.

    Returns:
        A list of Question objects representing the questions in the CSV file.
    """
    questions = []
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            question = row[0]
            correct_answer = row[1]
            q = Question(question, correct_answer)
            questions.append(q)
    return questions


def ask_quiz() -> str:
    """
    Print a list of available quizzes and ask the user to choose one.

    Returns:
        The file name of the selected quiz.
    """
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
    quiz = Quiz(questions, saver, result_path=f"data/results/{username}_{chosen_quiz_file.replace('.csv', '')}_results.txt",  min_correct=2)
    quiz.take_quiz()


if __name__ == "__main__":
    main()
