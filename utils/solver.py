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
# from concepts.dm.crow.parsers.cdl_parser import TransformationError
# from concepts.dm.crow.behavior_utils import execute_behavior_effect_advanced 
parser = jacinle.JacArgumentParser()
# parser.add_argument('--domain', default='virtualhome.cdl')
parser.add_argument('--domain', default='/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/experiments/virtualhome/CDLs/virtualhome_partial.cdl')
parser.add_argument('--verbose', action='store_true')
args = parser.parse_args()

def goal_solver(goal):
    domain = crow.load_domain_file(args.domain)
    problem = crow.load_problem_file('/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/experiments/virtualhome/CDLs/exicutable_cdl.cdl', domain=domain)
    # problem = crow.load_problem_file('agent_internal_state.cdl', domain=domain)

    # behavior= crow.load_domain_file('explore_test.cdl')
    # bounded_variables=dict()
    # execute_behavior_effect_advanced(domain, behavior, state, bounded_variables)
    # state = problem.state
    output=plan(problem)
    return output

def plan(problem):
    goal=problem.goal
    candidate_plans, search_stat = crow.crow_regression(
        problem.domain, problem, goal=goal, min_search_depth=20, max_search_depth=20,
        is_goal_ordered=True, is_goal_serializable=False, always_commit_skeleton=True,
        enable_state_hash=False,
        verbose=False
    )
    table = list()
    for p in candidate_plans:
        table.append('; '.join(map(str, p)))
    print()
    print('=' * 80)
    print('Goal:', goal)
    for i, row in enumerate(table):
    #     row = row.split('; ')
    #     for lines in row:
    #         print(lines.replace("_executor",""))
        print(f'Plan {i}:', row.replace("_executor",""))
    print(search_stat)
    # input('Press Enter to continue...')
    return table

if __name__ == '__main__':
    goal=None
    goal_solver(goal)