#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# File   : parse.py
# Author : Jiayuan Mao
# Email  : maojiayuan@gmail.com
# Date   : 08/13/2024
#
# Distributed under terms of the MIT license.

import torch
import jacinle
import concepts.dm.crow as crow
from jacinle.utils.debug import time


def parse_txt(txt):
    lines = txt.strip().split('\n')
    lines = [line.strip() for line in lines]
    liens = [line for line in lines if line]

    ret = dict()
    # the format is predicate[args...] = True/False

    for line in lines:
        if '=' not in line:
            raise ValueError(f'Invalid line: {line}')

        pred, value = line.split('=')
        pred = pred.strip()
        value = value.strip()

        if value not in {'True', 'False'}:
            raise ValueError(f'Invalid value: {value}')

        if '[' in pred:
            pred, args = pred.split('[')
            args = args[:-1].split(',')
            args = [arg.strip() for arg in args]
        else:
            args = []

        ret.setdefault(pred, dict())[tuple(args)] = value == 'True'

    return ret


def main():
    with time('load_domain'):
        domain = crow.load_domain_file('./virtualhome.cdl')

    with time('load_problem'):
        problem1 = crow.load_problem_file('./combined_generated_raw.cdl', domain=domain)

    with open('./init.txt') as f:
        init_as_dict = parse_txt(f.read())

    with time('load_problem_from_python_structure'):
        problem2 = crow.load_problem_file('./combined_generated.cdl', domain=domain)  # only load the "bare" problem

        state = problem2.state
        object_types = {o: state.get_typed_index(o) for o in state.object_names}

        for pred, values in init_as_dict.items():
            for args, value in values.items():
                if value:
                    state.features[pred].tensor[tuple(object_types[x] for x in args)] = True

    for pred in problem1.state.features.keys():
        assert torch.allclose(problem1.state.features[pred].tensor, problem2.state.features[pred].tensor)
    print(jacinle.colored('All features are equal.', 'green'))


if __name__ == '__main__':
    main()

