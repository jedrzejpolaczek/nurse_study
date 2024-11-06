import openai
import json
from typing import (List, Dict, Optional)


def load_config() -> Dict[str, str]:
    """
    Loads the API key from the config.json file.

    Returns (dict[str, str]):
        A dictionary containing the API key.
    """
    with open("config.json", "r", encoding="UTF-8") as f:
        config = json.load(f)

    return config


def choose_case() -> int:
    """
    Prompts the user to choose a case study from a list.

    Returns (int):
        The index of the chosen case study.
    """
    file_path = "cases.txt"
    with open(file_path, "r", encoding="UTF-8") as f:
        for i, line in enumerate(f):
            print(f"{i+1}. {line.strip()}")
    choice = int(input("Wybierz numer przypadku: "))

    return choice


def load_case(
        path: str,
        choice: int
    ) -> List[str]:
    """
    Loads the specified case study from a text file.

    Args:
        path (str):
            Path to folder with text files.
        choice (int):
            The index of the case study to load.

    Returns (list[str]):
        A list of lines fr  om the case study file.
    """
    file_path = f"{path}\\pacient_{choice}.txt"

    with open(file_path, "r", encoding="UTF-8") as f:
        lines = f.readlines()

    return lines


def get_question(
        question_description: str
    ) -> str:
    """
    Prompts the user to enter a question for the AI model.

    Returns (str):
        The user's input question.
  """
    question = str(input(question_description))

    return question


def get_initial_prompt(
        case: str,
        question: str
    ) -> str:
    """
    Creates the initial prompt for the AI model, including the case study and question.

    Args:
        case (str):
            The case study text.
        question (str):
            The question to ask the AI model.

    Returns (str):
        The initial prompt string.
    """

    prompt = f"Chce byś na podstawie poniższych \"case study\" \
    wygenerował możliwą odpowiedź pacjenta na zadane pytanie.\n \
    \"CASE STUDY\" PACJENTA:{case}\n \
    PYTANIE: {question}"

    return prompt


def get_next_prompt(
        question: str
    ) -> str:
    """
    Creates a prompt for the AI model to generate a response to a subsequent question.

    Args:
        question (str):
            The subsequent question.

    Returns (str):
        The prompt string for the subsequent question.
    """
    prompt = f"Dla tych samych danych wygeneruj odpowiedź na pytanie: {question}"

    return prompt


def send_prompt(
        prompt: str,
        api_key: str,
        model: str
    ) -> None:
    """
    Sends a prompt to the OpenAI API and prints the generated response.

    Args:
        prompt (str):
            The prompt to send to the AI model.
        api_key (str):
            The OpenAI API key.
        model (str):
            The OpenAI ChatGPT model to use.
    
    Returns:
        None
    """
    openai.api_key = api_key
    messages = [{"role": "system", "content": "You are an intelligent assistant."}]
    messages.append({"role": "user", "content": prompt})

    chat = openai.ChatCompletion.create(
        model=model,
        messages=prompt
    )

    reply = chat.choices[0].message.content

    print(reply)


def chat_with_patient(
        api_key: str,
        model: str,
        texts_path: str,
        question_description: str,
        second_question_description: str,
        end_questioning_flag: str
    ) -> None:
    """
    Conducts a conversation with a virtual patient.

    This function repeatedly prompts the user for questions,
    sends them to the OpenAI API, and prints the generated responses.

    It handles potential errors such as invalid input,
    file not found, rate limits, and general exceptions.

    Args:
        api_key (str):
            The OpenAI API key.
        model (str):
            The OpenAI model to use.
        texts_path (str):
            The path to the directory containing patient case files.
        question_description (str):
            A description of the initial question to ask the user.
        second_question_description (str):
            A description of the subsequent questions to ask the user.
        end_questioning_flag (str):
            A flag to indicate the end of the questioning session.    
  """
    while 1:
        try:
            choice = choose_case()
            case = load_case(texts_path, choice)
            question = get_question(question_description)
            prompt = get_initial_prompt(case, question)
            send_prompt(prompt, api_key, model)

            while question != end_questioning_flag:
                print(second_question_description + end_questioning_flag)
                question = get_question(question_description)
                prompt = get_next_prompt(question)
                send_prompt(prompt, api_key, model)

        except ValueError:
            print("Nie wybrałeś numeru z listy. Proszę wybierz ponownie.")
        except FileNotFoundError:
            print(f"Plik z pacjentem nie znaleziony \"pacjent_{choice}\".")
            print("Upewnij się czy plik istnieje w folderze \"pacjenci\".")
        except openai.error.RateLimitError:
            print("Wyczerpano limit pytan. Sprobuj pozniej!")
        except Exception as e:
            print(f"Wystąpił błąd: {str(e)}")


if __name__ == "__main__":
    config = load_config()
    api_key = config["api_key"]
    model = config["model"]
    texts_path = config["path"]
    question_description = config["question_description"]
    second_question_description = config["second_question_description"]
    end_questioning_flag = config["end_questioning_flag"]

    chat_with_patient(
        api_key=api_key,
        model=model,
        texts_path=texts_path,
        question_description=question_description,
        second_question_description=second_question_description,
        end_questioning_flag=end_questioning_flag
    )