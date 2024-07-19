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
    problem = crow.load_problem_file('virtualhome-problem.cdl', domain=domain)
    problem = crow.load_problem_file('generated.cdl', domain=domain)
    
    state = problem.state
    goal="close(char, table_63)"
    plan(domain, problem, goal)


def main():
    domain = crow.load_domain_file(args.domain)
    problem = crow.load_problem_file('virtualhome-problem.cdl', domain=domain)
    problem = crow.load_problem_file('generated.cdl', domain=domain)
    
    state = problem.state
    print('=' * 80)
    print('Initial state:')
    print(state)

    # plan(domain, problem, 'is_off(light)')

    plan(domain, problem, 'clean(pillow_287)')

    # plan(domain, problem, 'on(apple,light)')

    # plan(domain, problem, 'close_item(apple,light)')


def plan(domain, problem, goal):
    goal=problem.goal
    candidate_plans, search_stat = crow.crow_regression(
        domain, problem, goal=goal, min_search_depth=5, max_search_depth=7,
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
    input('Press Enter to continue...')


if __name__ == '__main__':
    # main()
    goal="""def dinner_prepared_for_two():
  return on(plate_1004, table_63) and on(plate_1005, table_63) and on(cup_2010, table_63) and on(cup_1001, table_63) and clean(plate_1004) and clean(plate_1005) and clean(cup_2010) and clean(cup_1001) and sitting(char_1) and sitting(char_2)
  
  behavior prepare_dinner_for_two():
  goal:
    dinner_prepared_for_two()
  body:
    promotable:
      achieve on(plate_1004, table_63)
      achieve on(plate_1005, table_63)
      achieve on(cup_2010, table_63)
      achieve on(cup_1001, table_63)
    achieve clean(plate_1004)
    achieve clean(plate_1005)
    achieve clean(cup_2010)
    achieve clean(cup_1001)

GOAL:
  dinner_prepared_for_two()"""
    goal_solver(goal)
    

