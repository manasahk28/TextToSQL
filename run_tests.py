import sys
import os

# Insert workspace root to sys.path so src is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tests.main import run
from tests import example_cases

if __name__ == "__main__":
    start = 0
    end = 7
    for example_case_index in range(start, end):
        reflection_state = example_cases.get_example_case(example_case_index)
        # Reset state structure
        reflection_state['iteration'] = 0
        reflection_state['source'] = 'First-pass'
        
        print(f"===========================================================")
        print(f"Running Preset Case {example_case_index}: {reflection_state['user_query']}")
        print(f"===========================================================")
        run(reflection_state)
        print("\n\n")
