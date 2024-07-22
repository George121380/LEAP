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

parser = jacinle.JacArgumentParser()
# parser.add_argument('--domain', default='virtualhome.cdl')
parser.add_argument('--domain', default='virtualhome.cdl')
parser.add_argument('--verbose', action='store_true')
args = parser.parse_args()


def goal_solver(goal):
    domain = crow.load_domain_file(args.domain)

    problem = crow.load_problem_file('combined_generated.cdl', domain=domain)
    
    state = problem.state
    output=plan(problem, problem, goal)
    return output


def main():
    domain = crow.load_domain_file(args.domain)
    problem = crow.load_problem_file('virtualhome-problem.cdl', domain=domain)
    problem = crow.load_problem_file('combined_generated.cdl', domain=domain)
    
    state = problem.state
    print('=' * 80)
    print('Initial state:')
    print(state)

    # plan(domain, problem, 'is_off(light)')

    plan(domain, problem, 'clean(pillow_287)')

    # plan(domain, problem, 'on(apple,light)')

    # plan(domain, problem, 'close_item(apple,light)')


def plan(domain, problem, goal):
    goal=None
    candidate_plans, search_stat = crow.crow_regression(
        problem.domain, problem, goal=goal, min_search_depth=5, max_search_depth=7,
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
    with open("combined_generated.cdl", "r") as file:
        original_content = file.read()
    goal_solver(original_content)
    

