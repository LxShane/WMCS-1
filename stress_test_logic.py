import sys
import os
from termcolor import colored

sys.path.append(os.getcwd())
from system_a_cognitive.epistemic.gate import EpistemicGate

def run_logic_test():
    print(colored("### STRESS TEST: SYMBOLIC LOGIC GATE ###", "magenta", attrs=['bold']))
    
    gate = EpistemicGate()
    
    # CASE 1: VALID LOGIC
    print(colored("\nCASE 1: Valid Logic (Cat EATS Food)", "cyan"))
    contract_1 = gate.generate_contract(
        confidence=0.9,
        assumptions=["Cat(20,1) is a Mammal"],
        positive_assertions=["Cat(20,1) EATS Food(10,5)"],
        negative_assertions=[]
    )
    print(f"Grade: {contract_1.grade.grade}")
    if contract_1.grade.grade == "ANSWER":
        print(colored("PASS", "green"))
    else:
        print(colored("FAIL", "red"))

    # CASE 2: INVALID ONTOLOGY
    print(colored("\nCASE 2: Invalid Ontology (Number 5 EATS Food)", "cyan"))
    contract_2 = gate.generate_contract(
        confidence=0.9,
        assumptions=["Number 5(40,5) is Abstract"],
        positive_assertions=["Number 5(40,5) EATS Food(10,5)"],
        negative_assertions=[]
    )
    print(f"Grade: {contract_2.grade.grade}")
    
    if contract_2.grade.grade == "CANNOT_CONCLUDE":
         print(colored(f"PASS (Rejected: {contract_2.cannot_assert[0]})", "green"))
    else:
         print(colored(f"FAIL (Allowed: {contract_2.grade.grade})", "red"))

if __name__ == "__main__":
    run_logic_test()
