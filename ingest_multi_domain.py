import sys
import os
from termcolor import colored

# Ensure we can import system modules
sys.path.append(os.getcwd())
from main import WMCS_Kernel
from system_a_cognitive.ingestion.ingestor import ContentIngestor
from system_a_cognitive.logic.identity import IdentityManager

# 1. MECHANICAL DOMAIN (Physics/Engineering)
TEXT_ENGINE = """
THE INTERNAL COMBUSTION ENGINE (FOUR-STROKE)

The internal combustion engine converts chemical energy into mechanical work through a four-stroke cycle:
1. Intake: The Piston moves down, drawing a fuel-air mixture into the Cylinder through the Intake Valve.
2. Compression: The Piston moves up, compressing the mixture.
3. Power (Combustion): The Spark Plug ignites the compressed mixture. The resulting explosion forces the Piston down with great force. This is the source of mechanical power.
4. Exhaust: The Piston moves up again, pushing burnt gases out through the Exhaust Valve.

Components:
- Piston: A cylindrical metal part that moves up and down inside the cylinder.
- Spark Plug: A device that delivers electric current to the combustion chamber to ignite the compressed fuel/air mixture.
- Crankshaft: A rotating shaft which converts the reciprocating motion of the piston into rotational motion to drive the wheels.
"""

# 2. ECONOMIC DOMAIN (Social/Abstract)
TEXT_ECONOMICS = """
ECONOMIC INFLATION

Inflation is a sustained increase in the general price level of goods and services in an economy over a period of time.

Causes:
- Demand-Pull Inflation: When aggregate demand for goods and services exceeds aggregate supply.
- Cost-Push Inflation: When the cost of production (wages, raw materials) increases, causing producers to raise prices.
- Monetary Expansion: An increase in the money supply (printing money) can reduce the purchasing power of the currency, leading to higher prices.

Effects:
- Reduced Purchasing Power: Each unit of currency buys fewer goods.
- Uncertainty: Businesses may hesitate to invest due to unpredictable costs.
"""

def run_multi_domain_baths():
    print(colored("### INGESTING MULTI-DOMAIN KNOWLEDGE ###", "magenta", attrs=['bold']))
    
    identity_manager = IdentityManager()
    ingestor = ContentIngestor(identity_manager=identity_manager)
    
    # 1. ENGINE
    print(colored("\n--- Domain 1: Mechanical Engineering ---", "cyan"))
    concepts_mech = ingestor.ingest_text(TEXT_ENGINE, source_name="engineering_manual")
    print(colored(f"Generated {len(concepts_mech)} blocks: {concepts_mech}", "green"))

    # 2. ECONOMICS
    print(colored("\n--- Domain 2: Macroeconomics ---", "cyan"))
    concepts_econ = ingestor.ingest_text(TEXT_ECONOMICS, source_name="economics_textbook")
    print(colored(f"Generated {len(concepts_econ)} blocks: {concepts_econ}", "green"))

if __name__ == "__main__":
    run_multi_domain_baths()
