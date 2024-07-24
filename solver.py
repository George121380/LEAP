#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# File   : 2-solve-blocksworld.py
# Author : Jiayuan Mao
# Email  : maojiayuan@gmail.com
# Date   : 03/04/2024
#
# This file is part of Project Concepts.
# Distributed under terms of the MIT license.

import jacinle
import concepts.dm.crow as crow
from concepts.dm.crow.parsers.cdl_parser import TransformationError
parser = jacinle.JacArgumentParser()
# parser.add_argument('--domain', default='virtualhome.cdl')
parser.add_argument('--domain', default='virtualhome.cdl')
parser.add_argument('--verbose', action='store_true')
args = parser.parse_args()


def goal_solver(goal):
    domain = crow.load_domain_file(args.domain)

    problem = crow.load_problem_file('combined_generated.cdl', domain=domain)
    
    state = problem.state
    output=plan(problem)
    return output

def plan(problem):
    goal=problem.goal
    candidate_plans, search_stat = crow.crow_regression(
        problem.domain, problem, goal=goal, min_search_depth=7, max_search_depth=7,
        is_goal_ordered=True, is_goal_serializable=False, always_commit_skeleton=True
    )
    table = list()
    for p in candidate_plans:
        table.append('; '.join(map(str, p)))
    print()
    print('=' * 80)
    print('Goal:', goal)
    for i, row in enumerate(table):
        print(f'Plan {i}:', row)
    print(search_stat)
    # input('Press Enter to continue...')
    return table


if __name__ == '__main__':
    # main()
    with open("/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/failure_cases/is_on(washing_machine).cdl", "r") as file:
        original_content = file.read()
    try:
      goal_solver(original_content)
    except TransformationError as e:
        print(f"Transformation failed: {e.errors}")
    

