from regular_expression import *
from nfa import *

def rename_states(target, reference):
    off = max(reference.states) + 1
    target.start_state += off
    target.states = set(map(lambda s: s + off, target.states))
    target.final_states = set(map(lambda s: s + off, target.final_states))
    new_delta = {}
    for (state, symbol), next_states in target.delta.items():
        new_next_states = set(map(lambda s: s + off, next_states))
        new_delta[(state + off, symbol)] = new_next_states

    target.delta = new_delta

def new_states(*nfas):
    state = 0
    for nfa in nfas:
        m = max(nfa.states)
        if m >= state:
            state = m + 1

    return state, state + 1

def re_to_nfa(re):

    eps = "ε"
    alphabet = "ε"
    states = {}
    start_state = 0
    final_states = {}
    delta = {}

    if re.type == EMPTY_SET:
      alphabet = ""
      states = {0, 1}
      start_state = 0
      final_states = {1}
      delta = {}

    elif re.type == EMPTY_STRING:
      alphabet = eps
      states = {0, 1}
      start_state = 0;
      final_states = {1}
      delta = {(0, eps): {1}}

    elif re.type == SYMBOL:
      alphabet += str(re)
      states = {0,1}
      start_state = 0
      final_states = {1}
      delta = {(0, str(re)): {1}}

    elif re.type == ALTERNATION:
      lhs = re_to_nfa(re.lhs)
      rhs = re_to_nfa(re.rhs)
      rename_states(rhs, lhs)
      alphabet = "".join(set(lhs.alphabet + rhs.alphabet + eps))
      states = lhs.states | rhs.states
      start_state = max(states) + 1
      final_states = {(start_state + 1)}
      states = states | {start_state} | final_states
      delta_start = {(start_state, eps): {lhs.start_state, rhs.start_state}}
      delta_end = {}
      for state in lhs.final_states:
        delta_end.update({(state, eps): final_states})

      for state in rhs.final_states:
        delta_end.update({(state, eps): final_states})

      delta.update(lhs.delta)
      delta.update(rhs.delta)
      delta.update(delta_start)
      delta.update(delta_end)

    elif re.type == STAR:
      lhs = re_to_nfa(re.lhs)
      alphabet = "".join(set(lhs.alphabet + eps))
      states = lhs.states
      start_state = max(states) + 1
      final_states = {(start_state + 1)}
      states = states | {start_state} | final_states
      delta_start = {(start_state, eps): {lhs.start_state} | final_states}
      delta_end = {}
      for state in lhs.final_states:
        delta_end.update({(state, eps): {lhs.start_state} | final_states})
      delta.update(lhs.delta) 
      delta.update(delta_start)
      delta.update(delta_end)


    elif re.type == CONCATENATION:
      lhs = re_to_nfa(re.lhs)
      rhs = re_to_nfa(re.rhs)
      rename_states(rhs, lhs)
      alphabet = "".join(set(lhs.alphabet + rhs.alphabet + eps))
      states = lhs.states | rhs.states
      start_state = max(states) + 1
      final_states = {(start_state + 1)}
      states = states | {start_state} | final_states
      delta_start = {(start_state, eps): {lhs.start_state}}
      delta_end = {}
      for state in lhs.final_states:
        delta_end.update({(state, eps): {rhs.start_state}})

      for state in rhs.final_states:
        delta_end.update({(state, eps): final_states})

      delta.update(lhs.delta) 
      delta.update(rhs.delta) 
      delta.update(delta_start)
      delta.update(delta_end)

    return NFA(alphabet, states, start_state, final_states, delta)