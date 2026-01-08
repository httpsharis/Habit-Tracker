"""
NeuroHabit Terminal Chat Interface.

A CLI tool to test the conversational ML engine without the API layer.
"""
import os
import sys
import time

# Ensure app directory is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from app.routers.chat import chat_with_ai
from app.schemas import ChatInput


def type_writer(text: str, delay: float = 0.005) -> None:
    """Print text with typewriter effect."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()


def main():
    """Main CLI loop."""
    print("\033[96m" + "=" * 50)
    print("       NEUROHABIT TERMINAL INTERFACE")
    print("         (Pure ML - No External AI)")
    print("=" * 50 + "\033[0m\n")
    
    current_step = 0
    temp_data = {}
    
    # Initial greeting
    initial_input = ChatInput(user_message="start", current_step=0, temp_data={})
    response = chat_with_ai(initial_input)
    print("\033[96mNeuroHabit:\033[0m")
    type_writer(response.bot_message)
    current_step = response.next_step
    
    while True:
        try:
            user_input = input("\n\033[93mYou:\033[0m ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'bye', 'q']:
                print("\033[96mNeuroHabit:\033[0m Session terminated. Stay optimized. 👋")
                break
                
            chat_input = ChatInput(
                user_message=user_input,
                current_step=current_step,
                temp_data=temp_data
            )
            
            response = chat_with_ai(chat_input)
            
            print("\033[96mNeuroHabit:\033[0m")
            type_writer(response.bot_message)
            
            current_step = response.next_step
            temp_data = response.updated_data
            
            if response.prediction:
                print("\n\033[92m" + "=" * 40)
                print("         PREDICTION SUMMARY")
                print("=" * 40)
                print(f"  Score:   {response.prediction['daily_score']}/100")
                print(f"  Mode:    {response.prediction['day_classification']}")
                print(f"  Persona: {response.prediction['persona']}")
                print("=" * 40 + "\033[0m")
                
        except KeyboardInterrupt:
            print("\n\nSession interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n\033[91mError: {e}\033[0m")


if __name__ == "__main__":
    main()