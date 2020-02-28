#!/usr/bin/env python
import sys
import pickle

from regex import RegEx
from regex import *

import regular_expression as Regular
from tema_lab import re_to_nfa
from dfa import *

ALFANUM = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
EPS = "ε"


# functie care parseaza regex de tip set ("[ab-z]"")
def get_sym_for_square(input) :

    list = []

    i = 0

    while(i < len(input)):
        sym = input[i]
        if sym == "-":
            ant = list.pop()
            urm = input[i+1]
            list.append((ant, urm))
            i += 2
            continue
        else :
            list.append(sym)
            i += 1

    return list

# functie care returneaza range-ul dintre "{}"
def get_from_curly(input) :
    list = input.split(",")

    if len(list) == 1 :
        return int(list[0]), int(list[0])

    x = list[0]
    y = list[1]

    if x == "" :
        x = -1

    if y == "" :
        y = -1

    return int(x), int(y)

# functia principala de parsare
def parse(regex_string) :
    # in acc retin regex-urile deja parsate
    acc = []
    open_par = 0
    closed_par = 0
    first_open_par = -1
    last_closed_par = -1
    between_par = ""

    open_curly_pos = -1
    closed_curly_pos = -1

    open_square_pos = -1
    closed_square_pos = -1

    # Marcheaza initializarea unui regex
    ex = RegEx(EMPTY_STRING)

    for i in range(len(regex_string)) :
        symbol = regex_string[i]

        # open_par == 1 => se citeste ceea ce este intre paranteze rotunde
        # open_par == 0 => parsare normala fara paranteze
        if open_par == 0 :

            # pentru regexul set retin pozitiile parantezelor patrate si apelez functia get_sym_for_square de mai sus
            if symbol == "[" :
                open_square_pos = i + 1

            if symbol == "]" :
                closed_square_pos = i
                square_expr_set = get_sym_for_square(regex_string[open_square_pos:closed_square_pos])
                sym = RegEx(SYMBOL_SET, square_expr_set)
                acc.append(sym)
                open_square_pos = -1
                closed_square_pos = -1

            if open_square_pos != -1 :
                continue


            #  pentru regexul range este identic ca mai sus
            if symbol == "{" :
                open_curly_pos = i + 1

            if symbol == "}" :
                closed_curly_pos = i
                i += 1
                x, y = get_from_curly(regex_string[open_curly_pos:closed_curly_pos])
                sym = acc.pop()
                new_sym = RegEx(RANGE, sym, (x, y))
                acc.append(new_sym)
                open_curly_pos = -1
                closed_curly_pos = -1

            # daca gasesc simbol (fara a fi intre "{}")
            if symbol in ALFANUM and open_curly_pos == -1:
                sym = RegEx(SYMBOL_SIMPLE, symbol)
                acc.append(sym)

            # sirul vid
            if regex_string == "" :
                sym = RegEx(EMPTY_STRING)
                acc.append(sym)

            # Pentru . se creeaza regex la fel ca pentru orice alt caracter alfanum
            if symbol == "." :
                sym = RegEx(SYMBOL_ANY)
                acc.append(sym)

            # Pentru ? scot din lista ceea ce a fost parsat inainte si creez alt regex inserandu-l pe cel nou in lista
            if symbol == "?" :
                anterior = acc.pop()
                sym = RegEx(MAYBE, anterior)
                acc.append(sym)

            # Pentru * la fel
            if symbol == "*" :
                anterior = acc.pop()
                sym = RegEx(STAR, anterior)
                acc.append(sym)
        
            # Pentru + la fel
            if symbol == "+" :
                anterior = acc.pop()
                sym = RegEx(PLUS, anterior)
                acc.append(sym)

            # Pentru | concatenez in lhs toti termenii din acc
            # In rhs construiesc regexul dat de parse pe restul sirului neparsat
            if symbol == "|" :
                lhs = RegEx(EMPTY_STRING)

                for reg in acc :
                    if lhs.type == EMPTY_STRING :
                        lhs = reg
                    else :
                        lhs = RegEx(CONCATENATION, lhs, reg)

                acc = []

                rhs = parse(regex_string[i+1:])
                sym = RegEx(ALTERNATION, lhs, rhs)
                acc.append(sym)
                
                break

        # Marchez indexii parantezelor inchise si deschise
        # Numar cate paranteze au fost inchise si cate deschise
        # Apelez parsare pe ceea ce este intre paranteze cand paranteze_deschise == paranteze_inchise
        if symbol == "(" :
            open_par += 1

            if first_open_par == -1 :
                first_open_par = i + 1


        if symbol == ")" :
            closed_par += 1
            if open_par == closed_par :
                last_closed_par = i
                sym = parse(regex_string[first_open_par:last_closed_par])
                acc.append(sym)
                open_par = 0
                closed_par = 0
                first_open_par = -1
                last_closed_par = -1

    # La final dupa ce am terminat sirul de parsat concatenez toti termenii RegEx din
    for reg in acc :
        if ex.type == EMPTY_STRING :
            ex = reg
        else :
            ex = RegEx(CONCATENATION, ex, reg)


    return ex

# functie care primeste un regex si intoarce echivalentul in RegularExpression
# Transformarile echivalente sunt cele mentionate in PDF-ul temei
def regex_to_regexp(regex) :
    if regex.type == EMPTY_STRING :
        return Regular.RegularExpression(Regular.EMPTY_STRING)

    if regex.type == SYMBOL_SIMPLE :
        return Regular.RegularExpression(Regular.SYMBOL, regex.symbol)
    
    if regex.type == SYMBOL_ANY :

        regular = Regular.RegularExpression(Regular.EMPTY_STRING)
        
        for i, c in enumerate(ALFANUM) :
            if i == 0 :
                regular = Regular.RegularExpression(Regular.SYMBOL, c)
            else :
                sym = Regular.RegularExpression(Regular.SYMBOL, c)
                regular = Regular.RegularExpression(Regular.ALTERNATION, regular, sym)

        return regular

    if regex.type == SYMBOL_SET :

        regular = Regular.RegularExpression(Regular.EMPTY_STRING)
        sym_set = regex.symbol_set

        for elem in sym_set :
            if type(elem) is tuple :
                x, y = elem
                for c in range(ord(x), ord(y) + 1) :
                    sym = Regular.RegularExpression(Regular.SYMBOL, chr(c))

                    if regular.type == Regular.EMPTY_STRING :
                        regular = sym
                    else :
                        regular = Regular.RegularExpression(Regular.ALTERNATION, regular, sym)

            else :
                sym = Regular.RegularExpression(Regular.SYMBOL, elem)

                if regular.type == Regular.EMPTY_STRING :
                    regular = sym
                else :
                    regular = Regular.RegularExpression(Regular.ALTERNATION, regular, sym)

                    

        return regular

    if regex.type == MAYBE :
        sym = regex_to_regexp(regex.lhs)
        regular = Regular.RegularExpression(Regular.EMPTY_STRING)
        regular = Regular.RegularExpression(Regular.ALTERNATION, regular, sym)

        return regular

    if regex.type == STAR :

        sym = regex_to_regexp(regex.lhs)
        regular = Regular.RegularExpression(Regular.STAR, sym)

        return regular

    if regex.type == PLUS :

        sym = regex_to_regexp(regex.lhs)
        star = Regular.RegularExpression(Regular.STAR, sym)
        regular = Regular.RegularExpression(Regular.CONCATENATION, sym, star)

        return regular

    if regex.type == RANGE :

        sym = regex_to_regexp(regex.lhs)
        regular = sym

        x, y = regex.range

        if x == y :
            for i in range(1, x) :
                regular = Regular.RegularExpression(Regular.CONCATENATION, regular, sym)

        if x == -1 :
            regular = Regular.RegularExpression(Regular.EMPTY_STRING)
            acc = sym

            for i in range(y) :
                regular = Regular.RegularExpression(Regular.ALTERNATION, regular, acc)
                acc = Regular.RegularExpression(Regular.CONCATENATION, acc, sym)

        if y == -1 :
            acc = sym
            for i in range(1, x) :
                acc = Regular.RegularExpression(Regular.CONCATENATION, acc, sym)

            regular = acc
            star = Regular.RegularExpression(Regular.STAR, sym)
            regular = Regular.RegularExpression(Regular.CONCATENATION, regular, star)

        if x != -1 and y != -1 :
            acc = sym
            for i in range(1, x) :
                acc = Regular.RegularExpression(Regular.CONCATENATION, acc, sym)

            regular = acc

            for i in range(y - x) :
                acc = Regular.RegularExpression(Regular.CONCATENATION, acc, sym)
                regular = Regular.RegularExpression(Regular.ALTERNATION, regular, acc)


        return regular

    if regex.type == CONCATENATION :

        lhs = regex_to_regexp(regex.lhs)
        rhs = regex_to_regexp(regex.rhs)
        regular = Regular.RegularExpression(Regular.CONCATENATION, lhs, rhs)

        return regular

    if regex.type == ALTERNATION :
        
        lhs = regex_to_regexp(regex.lhs)
        rhs = regex_to_regexp(regex.rhs)
        regular = Regular.RegularExpression(Regular.ALTERNATION, lhs, rhs)
        
        return regular

# Aceasta functie calculeaza inchiderile epsilon pentru o stare data din NFA
def eps_closure(nfa, state) :

    l = [state]

    for key, value in nfa.delta.items() :
        c_state, sym = key
        next_states = value

        if c_state == state and sym == EPS :
            for elem in next_states :
                l += eps_closure(nfa, elem)

    l.sort()

    return l

# Aceasta functie primeste o lista de stari de NFA care reprezinta o stare din DFA
# si converteste "[1,2,3]" in "1,2,3" pentru a putea indexa fiecare stare a DFA-ului 
def state_to_string(state) :
    s = ""

    string = map(str, state)
    string = list(string)

    for i, elem in enumerate(string) :
        if i == 0:
            s = "" + elem
        else :
            s = s + "," + elem

    return s

# Aceasta functie primeste un NFA, lista calculata cu inchiderile epsilon
# si o coada cu prima stare a DFA-ului
# Ea construieste starile DFA-ului folosind algoritmul invatat la laborator
def build_states(nfa, eps_list, q) :

    states = []
    delta = {}
    sink = "sink"

    while len(q) > 0 :
        start_state = q.pop()

        if start_state not in states :
            states.append(start_state)

        for sym in nfa.alphabet :
            if sym == EPS :
                continue

            new_dfa_state = []
            for state in start_state :
                next_partial_state = nfa.delta.get((state, sym))
                if next_partial_state :
                    for n in next_partial_state :
                        new_dfa_state.extend(eps_list.get(n))
            
            if new_dfa_state :
                new_dfa_state.sort()

                if new_dfa_state not in states :
                    states.append(new_dfa_state)
                    q.append(new_dfa_state)

                str_start_state = state_to_string(start_state)
                str_new_dfa_state = state_to_string(new_dfa_state)

                transition = {(str_start_state, sym): str_new_dfa_state}
                delta.update(transition)

            
            else :
                str_start_state = state_to_string(start_state)
                transition = {(str_start_state, sym): sink}
                delta.update(transition)

            str_start_state = state_to_string(start_state)
            str_new_dfa_state = state_to_string(new_dfa_state)

    return states, delta

# Functia principala de convertire a NFA-ului in DFA
def NFA_DFA_conversion(nfa) :

    alphabet = nfa.alphabet
    states = []
    start_state = None
    final_states = set()
    delta = {}
    sink_state = "sink"

    # calculez inchiderile epsilon pentru fiecare stare din NFA      
    eps_list = {}
    for state in nfa.states :
        key = state
        value = eps_closure(nfa, state)
        eps_list.update({key: value})

    # Aflu prima stare a DFA-ului calculata anterior si apelez build_states 
    # pentru calcularea celorlalte stari ale DFA-ului
    start_state = eps_list.get(nfa.start_state)
    states, delta = build_states(nfa, eps_list, [start_state])

    # Verific care din starile construite anterior contin stari finale din NFA, apoi le adaug
    # in lista de stari finale ale DFA-ului
    for state in states :
        for n in state :
            if n in nfa.final_states :
                final_states.add(state_to_string(state))
                break

    # Convertesc fiecare stare (are tip lista) a DFA-ului in string pentru a ma putea referi la ele
    states = list(map(state_to_string, states))
    start_state = state_to_string(start_state)

    return DFA(alphabet, states, start_state, final_states, delta) 

# Aceasta functie simuleaza DFA-ul construit pe un cuvant
def simulate(dfa, word) :
    # Presupun ca, cuvantul nu este acceptat
    result = False

    alphabet = dfa.alphabet
    states = dfa.states
    start_state = dfa.start_state
    final_states = dfa.final_states
    delta = dfa.delta
    sink = "sink"

    # Folosesc o stare curenta care porneste ca fiind stare initiala
    current_state = start_state

    # Pentru fiecare caracter din cuvant gasesc urmatoarea stare din tranzitie pe simbolul c din starea curenta
    for c in word:
        if c == " " or c == "\n" :
            continue

        if c not in alphabet :
            return False

        for key, value in delta.items() :
            state, sym = key
            if state == current_state and sym == c :
                current_state = value
                break

    # Dupa ce am consumat tot cuvantul verific daca starea in care s-a ajuns este o stare finala
    if current_state in final_states :
        result = True
        
    return result

if __name__ == "__main__":
    valid = (len(sys.argv) == 4 and sys.argv[1] in ["RAW", "TDA"]) or \
            (len(sys.argv) == 3 and sys.argv[1] == "PARSE")
    if not valid:
        sys.stderr.write(
            "Usage:\n"
            "\tpython3 main.py RAW <regex-str> <words-file>\n"
            "\tOR\n"
            "\tpython3 main.py TDA <tda-file> <words-file>\n"
            "\tOR\n"
            "\tpython3 main.py PARSE <regex-str>\n"
        )
        sys.exit(1)

    if sys.argv[1] == "TDA":
        tda_file = sys.argv[2]
        with open(tda_file, "rb") as fin:
            parsed_regex = pickle.loads(fin.read())
    else:
        regex_string = sys.argv[2]
        
        parsed_regex = parse(regex_string)
        
        if sys.argv[1] == "PARSE":
            print(str(parsed_regex))
            sys.exit(0)

    regular = regex_to_regexp(parsed_regex)
    nfa = re_to_nfa(regular)
    dfa = NFA_DFA_conversion(nfa)

    with open(sys.argv[3], "r") as fin:
        content = fin.readlines()

    for word in content:
        result = simulate(dfa, word)
        print(result)

