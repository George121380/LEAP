import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="Run an embodied agent evaluation.")    
    parser.add_argument('--llm_model', type=str, default='gpt-4o', 
                        help="Specify the LLM model to be used. gpt-4o, deepseek")
    parser.add_argument('--library_extraction', type=str,
                        help="Specify the library extraction method to be used.")
    parser.add_argument('--model', type=str,default='ours', help="ours, LLM, LLM+P, CAP")
    parser.add_argument('--human_guidance', type=str,default='Manual',help="LLM,Manual,None")
    parser.add_argument('--use_library', type=bool, default=False,
                    help="Whether to use library (True or False).")
    parser.add_argument('--human_check_eventually', type=bool, default=False,
                    help="Whether use human to check.")

    return parser.parse_args()