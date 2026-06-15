import reflection_tasks
import example_cases
import app_constants
import json


def run(example_case):

    iteration = 0
    while True:
        print(f"----Generated output at current stage:--------\n{json.dumps(example_case, indent=4)}")

        print("----Validation---------------------------------")
        # get validation result and analysis
        validation_result = reflection_tasks.validation(example_case)
        print(f"Validation result:\n{json.dumps(validation_result, indent=4)}")

        if validation_result['validation'] is True or \
                iteration >= app_constants.MAX_REFLECTION_ITERATIONS:
            print("End of iterations")
            break
        else:
            print(f"Start iteration {iteration}")

        # prepare a prompt for reflection - 
        # using system prompt, user query, tables schema, 
        # tables rules, previously generated output
        print("----Prepare prompt for reflection--------------")
        reflection_prompt = reflection_tasks.generate_reflection_prompt(example_case)
        print("Prompt for performing reflection:")
        reflection_tasks.print_prompt(reflection_prompt)

        # LLM's response to the prompt
        print("----Invoke LLM to review and remedy------------")
        llm_response = reflection_tasks.llm_inference(reflection_prompt)

        # print thinking
        thinking = reflection_tasks.get_thinking_from_completion(llm_response)
        print(f"<thinking> tag in LLM's response:\n{thinking.strip()}")
        print()

        output_sql = reflection_tasks.get_sql_from_completion(llm_response)
        print(f"<sql> tag in LLM's response:\n{output_sql.strip()}")
        reflection_tasks.set_sql_in_genoutput(example_case, output_sql)

        iteration = iteration + 1
        reflection_tasks.set_iteration_in_genoutput(example_case, iteration)
        reflection_tasks.set_source_in_genoutput(example_case,'Reflection')


start = 0
end = 7
for example_case_index in range(start, end):
    reflection_state = example_cases.get_example_case(example_case_index)
    reflection_tasks.set_iteration_in_genoutput(reflection_state, 0)
    reflection_tasks.set_source_in_genoutput(reflection_state, 'First-pass')

    run(reflection_state)
    print("===========================================================\n\n")