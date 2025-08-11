#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# File   : 1-load-crow-domain.py
# Author : Jiayuan Mao
# Email  : maojiayuan@gmail.com
# Date   : 03/17/2024
#
# This file is part of Project Concepts.
# Distributed under terms of the MIT license.

import jacinle
import concepts.dm.crow as crow


domain = crow.load_domain_file('/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/src/domain/virtualhome_partial.cdl')


print(domain.name)
table = list()
for k, v in domain.types.items():
    table.append((f'Type::{k}', str(v)))
for k, v in domain.features.items():
    table.append((f'Feature::{k}', str(v)))
for k, v in domain.functions.items():
    table.append((f'Function::{k}', str(v)))
for k, v in domain.controllers.items():
    table.append((f'Controller::{k}', str(v)))
for k, v in domain.behaviors.items():
    table.append((f'Behavior::{k}', str(v)))

print(jacinle.tabulate(table))

problem = crow.load_problem_file('/Users/liupeiqi/workshop/Research/Instruction_Representation/lpq/Concepts/projects/crow/examples/06-virtual-home/src/domain/virtualhome_partial.cdl')
executor = domain.make_executor()

result = executor.execute(
    expression='close_char[char,light_1]',
    state=problem.state,
    bounded_variables=dict()
)

print('Evaluation result:', result)

