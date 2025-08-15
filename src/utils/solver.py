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
import time
# from concepts.dm.crow.parsers.cdl_parser import TransformationError
# from concepts.dm.crow.behavior_utils import execute_behavior_effect_advanced 
parser = jacinle.JacArgumentParser()
# Default to the proper VirtualHome domain file; allow override via env VH_DOMAIN_CDL
import os as _os
_default_domain = _os.environ.get('VH_DOMAIN_CDL', 'src/domain/virtualhome_partial.cdl')
parser.add_argument('--domain', default=_default_domain)
parser.add_argument('--verbose', action='store_true')
args = parser.parse_args(args=[])  # avoid clobbering by outer argparse

def goal_solver(cdl_path, planning=True):
    domain = crow.load_domain_file(args.domain)
    problem = crow.load_problem_file(cdl_path, domain=domain)
    # problem = crow.load_problem_file('agent_internal_state.cdl', domain=domain)

    # behavior= crow.load_domain_file('explore_test.cdl')
    # bounded_variables=dict()
    # execute_behavior_effect_advanced(domain, behavior, state, bounded_variables)
    # state = problem.state
    output=plan(problem, planning=planning)
    return output

def plan(problem, planning=True):
    """
    Args:    
        problem: crow.Problem
        planning: bool -> True for planning, False for policy
    
    """
    goal=problem.goal
    if planning:
        # candidate_plans, search_stat = crow.crow_regression(
        #     problem.domain, problem, goal=goal, min_search_depth=12, max_search_depth=12,
        #     is_goal_ordered=True, is_goal_serializable=False, always_commit_skeleton=True, commit_skeleton_everything=False,
        #     enable_state_hash=False,
        #     verbose=False
        # )
        candidate_plans, search_stat = crow.crow_regression(
            problem.domain, problem, goal=problem.goal,
            is_goal_ordered=True, is_goal_serializable=False, always_commit_skeleton=True,
            enable_state_hash=False,
            verbose=False,
            algo='priority_tree_v1'
        )
    else: # policy
        candidate_plans, search_stat = crow.crow_regression(
            problem.domain, problem, goal=goal, min_search_depth=12, max_search_depth=12,
            is_goal_ordered=True, is_goal_serializable=False, always_commit_skeleton=True, commit_skeleton_everything=True,
            enable_state_hash=False,
            verbose=False
        )
    table = list()
    for p in candidate_plans:
        table.append('; '.join(map(str, p)))
    print()
    print('=' * 60)
    print('Goal:', goal)
    for i, row in enumerate(table):
    #     row = row.split('; ')
    #     for lines in row:
    #         print(lines.replace("_executor",""))
        print(f'Plan {i}:', row.replace("_executor",""))
        break # only take the first plan
    print(search_stat)
    # input('Press Enter to continue...')
    return table

    