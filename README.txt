VLAD ANDREI-ALEXANDRU
331CB

================================ README TEMA 1 ================================
================================ Regex Engine  ================================


PARSARE:
	Parsarea am ales sa o fac manual.
	Aceasta functie de parsare se foloseste de o lista acumulator "acc" in care
retin ce am parsat pana la acel moment de timp.
	Am pornit de la verificarea fiecarui caracter din string si am construit
RegEx pentru fiecare caracter alfanumeric si pentru ".". Apoi am adaugat
parsarea si pentru cazurile cu paranteze rotunde.
	Pentru parantezele rotunde retin indecsii primei paranteze deschise,
ultimei paranteze inchise si numarul parantezelor deschise, respectiv inchise.
Cand gasesc o paranteza deschisa nu mai intru in modul de parsare directa a 
simbolilor urmatori pana nu se termina de parsat ceea ce este in paranteza. Dupa
ce am gasit nr_paranteze_deschise == nr_paranteze_inchise apelez parsare pe ceea
ce se afla intre ele. Functia se apeleaza recursiv pana se ajunge la caractere
sau celelalte cazuri.
	Cazurile pentru "?", "*", "+" se folosesc de ultimul regex parsat din acc.
Acesta este scos, construiesc alt regex corespunzator si il inserez pe cel nou
in lista.
	Pentru EPSILON verific daca simbolul este "".
	Pentru "|" concatenez in lhs toti termenii din acc. In rhs construiesc 
regexul dat de parse pe restul sirului neparsat.
    La final dupa ce am terminat sirul de parsat concatenez toti termenii RegEx din acc


RegEx --> RegularExpression:
	Pentru aceasta parte a temei am construit functia regex_to_regexp.
	Procedura este asemanatoare cu parsarea, doar ca in loc de caractere folosesc
tipul RegEx-ului.
	RegEx.EMPTY_STRING 	-> Regular.EMPTY_STRING
	RegEx.SYMBOL_SIMPLE -> Regular.SYMBOL_SIMPLE
	RegEx.SYMBOL_ANY 	-> SAU intre toate Regular-urile "a-zA-Z0-9"
	RegEx.SYMBOL_SET	-> SAU intre simboli si perechi. Perechile se transforma in 
							SAU intre toti simbolii din range-ul respectiv
	RegEx.MAYBE 		-> SAU intre EPS si Regular(expresie)
	RegEx.STAR 			-> Regular.STAR
	RegEx.PLUS 			-> Concatenare dintre Regular(regex) si Regular(regex_star)
	RegEx.RANGE 		-> Aflu range-ul si construiesc Regular de caractere din range
							pe care le concatenez sau le alternez in functie de caz
	RegEx.CONCATENATION -> Regular.CONCATENATION
	RegEx.ALTERNATION 	-> Regular.ALTERNATION


RegularExpression --> NFA:
	Pentru aceasta parte am folosit codul de la tema de laborator

NFA --> DFA:
	Conversia NFA-ului in DFA incepe prin a calcula inchiderile epsilor pentru fiecare
stare a NFA-ului.
	Aflu prima stare a DFA-ului calculata anterior si apelez build_states pentru 
calcularea celorlalte stari ale DFA-ului.
	Verific care din starile construite anterior contin stari finale din NFA, apoi 
le adaug in lista de stari finale ale DFA-ului.
	Convertesc fiecare stare (are tip lista) a DFA-ului in string pentru a ma 
putea referi la ele.

	Pentru inchiderea epsilon pornesc dintr-un nod si o losta vida. Cand gasesc tranzitie
pe starea curenta si EPSILON adaug in lista ceea ce returneaza apelul recursiv al acestei
functii pe urmatoarea stare
	La final intorc lista sortata

	Constructia starilor DFA-ului porneste de la inchiderea epsilon a starii initiale a NFA-ului
si urmareste algoritmul invatat la laborator.

	Starile si tranzitiile sunt de forma string pentru a putea face referire la ele in automat.
	Ex: Starea initiala a dfa-ului [1,2,5] este de fapt "1,2,5", iar starea Sink este "sink"


Simularea DFA-ului :
	Pentru acest pas ma folosesc de o functie simulate care primeste un DFA si un cuvant.
	La inceput presupun ca, cuvantul nu este acceptat.
    Folosesc o stare curenta care porneste ca fiind stare initiala
    Pentru fiecare caracter din cuvant gasesc urmatoarea stare din tranzitie pe simbolul c din starea curenta
    Dupa ce am consumat tot cuvantul verific daca starea in care s-a ajuns este o stare finala


PUNCTAJ :
	Pe masina locala obtin 1.33 puncte