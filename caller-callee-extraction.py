#!/usr/bin/env python3

import argparse
import re
import os
import subprocess

def simplify_sym(string):
    tmp = re.sub(r'<.*>', '<T>', string, 1)
    tmp = re.sub(r'\(.*\)', '()', tmp, 1)
    tmp = re.sub(r'\ ', '_', tmp, 1)
    return tmp

def demangle(data, symbol):
    sym_dict = data['sym_dict']

    if symbol in sym_dict:
        ret = sym_dict[symbol]
    else:
        try:
            res = subprocess.check_output(['c++filt', symbol])
            ret = res.decode('utf-8').strip()
            sym_dict[symbol] = ret
        except:
            print("Error")
            exit()
    return ret

def process_stack(data, arr, sym):
    stack = data['stack']
    pair_list = data['pair_list']

    if arr == "->":
        if len(stack):
            if (stack[-1], sym) in pair_list:
                pass
            else:
                pair_list.add((stack[-1], sym))
                caller = simplify_sym(stack[-1])
                callee = simplify_sym(sym)
                print("  \"{0}\" -> \"{1}\";".format(caller, callee))
        stack.append(sym)
    elif arr == "<-":
        if len(stack):
            if stack[-1] == sym:
                stack.pop() 
        else:
            exit()
    else:
        exit()

def create_dot_file(args):
    assert(os.path.isfile(args.infile))

    data = {'stack' : list(),
            'pair_list' : set(),
            'sym_dict' : dict()}
    
    print("digraph {0} {{".format(args.name))
    
    with open(args.infile, 'r') as f:
        for l1 in f:
            l2 = re.sub(r'^.*:', '', l1, 1).strip()
            arr = l2[0:2]
            sym = demangle(data, l2[2:-1])
            process_stack(data, arr, sym)
    
    print("}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Draw dynamic callgraph using SystemTap')
    parser.add_argument('-i', '--infile', dest='infile', type=str, default=None)
    parser.add_argument('-n', '--name', dest='name', type=str, default="Graph")
    args = parser.parse_args()
  
    create_dot_file(args)
