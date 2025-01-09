from vlab.models.sample import Sample
from vlab.models.composition import  Quantity
from vlab.actions.simulation import SimulationEngine
from vlab.models.molecule import BaseMolecule, BaseMoleculeOrganizationalInfo
from vlab.actions.combine import CombineAction, CombineActionParameters

from vlab.models.sample import Sample
from vlab.models.molecule import BaseMoleculeOrganizationalInfo, BaseMolecule
from vlab.llm.action_types import ActionType

# Rebuild models in dependency order
BaseMoleculeOrganizationalInfo.model_rebuild()
BaseMolecule.model_rebuild()
Sample.model_rebuild()


def print_combine_result(result):
    """Print combine action result in a readable format"""
    print("\nCombine Action Result:")
    print(f"Success: {result.success}")
    
    if not result.success:
        print(f"Error: {result.error_message}")
        return
        
    if result.warnings:
        print("\nWarnings:")
        for warning in result.warnings:
            print(f"- {warning}")
            
    if result.resulting_samples:
        print("\nResulting Sample:")
        for sample in result.resulting_samples:
            print(f"\nName: {sample.name}")
            
            # Handle superposition states if they exist
            composition = sample.organizational_info.composition
            if hasattr(composition, 'states') and composition.states:
                print(f"\nSample has {len(composition.states)} possible states:")
                for state in composition.states:
                    print(f"\nState (likelihood: {state.pseudocount}):")
                    for component in state.composition.components:
                        print(f"- {component.entity.name}: {component.quantity.value} {component.quantity.unit}")
            else:
                # Handle regular composition
                print("Composition:")
                for component in composition.components:
                    print(f"- {component.entity.name}: {component.quantity.value} {component.quantity.unit}")
            
            if hasattr(composition, 'total_volume') and composition.total_volume:
                print(f"\nTotal Volume: {composition.total_volume.value} L")
            if hasattr(composition, 'total_mass') and composition.total_mass:
                print(f"Total Mass: {composition.total_mass.value} g")

def demo_mixing_simulation():
    """Demo simulating mixing two samples"""
    simulation_engine = SimulationEngine()
    print("\n=== Mixing Simulation Demo ===")

    # Create two samples to mix
    acid = simulation_engine.create_sample("Hydrochloric Acid", context={"material_format": "100% HCl"})
    print("Acid:", acid)
    """
    Acid: 
    Sample: Hydrochloric Acid
    ID: 907d12f4-2ffe-412a-8b11-0fd79ad45b30
    ----------------------------------------
    Name: Hydrochloric Acid
    Container: Glass bottle with PTFE-lined cap for storing concentrated hydrochloric acid
    ----------------------------------------

    Specifications:
        Description: Glass bottle with PTFE-lined cap for storing concentrated hydrochloric acid
        Reusable: True
        Ampoule: False
        Hermetic: True
        Squeezable: False
        Permanently Sealed: False
        Opaque: False
        Container Materials: ['Borosilicate glass', 'PTFE']
        Transportable: True
        Immobile: False
        Aspiratable: True
        Dispensable: True

    Operating Limits:
        Min Temperature: 273.0 K
        Max Temperature: 323.0 K
        Min Volume: 0.1 L
        Max Volume: 2.5 L

    Composition:
        Hydrogen Chloride: value=100.0 unit='%'
    """
    base = simulation_engine.create_sample("Sodium Hydroxide", context={"material_format": "100% NaOH"})  
    print("Base:", base)
    """
    Base: 
    Sample: Sodium Hydroxide
    ID: 1ee99da2-83f2-499f-ba4f-c720124ec81e
    ----------------------------------------
    Name: Sodium Hydroxide
    Container: High-density polyethylene (HDPE) bottle with screw cap for storing solid Sodium Hydroxide
    ----------------------------------------
    Specifications:
        Description: High-density polyethylene (HDPE) bottle with screw cap for storing solid Sodium Hydroxide
        Reusable: True
        Ampoule: False
        Hermetic: True
        Squeezable: False
        Permanently Sealed: False
        Opaque: True
        Container Materials: ['High-density polyethylene (HDPE)']
        Transportable: True
        Immobile: False
        Aspiratable: False
        Dispensable: True

    Operating Limits:
        Min Temperature: 273.0 K
        Max Temperature: 323.0 K
        Min Volume: 0.1 L
        Max Volume: 2.5 L

    Composition:
        Sodium Hydroxide: value=100.0 unit='%'
    """
    
    print("Initial compositions:")
    print("Acid:")
    for component in acid.organizational_info.composition.components:
        print(f"* {component.entity.name}: {component.quantity.value} {component.quantity.unit}")
    print("\nBase:")
    for component in base.organizational_info.composition.components:
        print(f"* {component.entity.name}: {component.quantity.value} {component.quantity.unit}")
    
    """==============================================
    Initial compositions:
    Acid:
    * Hydrogen Chloride: 100.0 %

    Base:
    * Sodium Hydroxide: 100.0 %
    ==============================================
    """
    
    combine_action_params = CombineActionParameters(
            volumes={acid.name: Quantity(value=1, unit="L"),
                     base.name: Quantity(value=1, unit="L")}
        )
    
    # Determine container suitable for reaction
    container = simulation_engine.determine_container(
        name="combine",
        context={
            "input_samples": {
                "acid": acid,
                "base": base
            },
            "action_type": "combine",
            "action_parameters": combine_action_params
        }
    )
    print(f"Container: {container}")
    """
    ==============================================
    Container: Large polypropylene (PP) beaker for combining and neutralizing strong acids and bases.
    ----------------------------------------

    Specifications:
        Description: Large polypropylene (PP) beaker for combining and neutralizing strong acids and bases.
        Reusable: True
        Ampoule: False
        Hermetic: False
        Squeezable: False
        Permanently Sealed: False
        Opaque: False
        Container Materials: ['Polypropylene (PP)']
        Transportable: True
        Immobile: False
        Aspiratable: True
        Dispensable: True

    Operating Limits:
        Min Temperature: 273.0 K
        Max Temperature: 773.0 K
        Min Volume: 0.1 L
        Max Volume: 3.0 L
    ==============================================
    """
    

    print("combine_action_params", combine_action_params)
    
    combine_action = CombineAction(
        name="Combine",
        action_type=ActionType.COMBINE,
        input_samples={acid.name: acid, base.name: base},
        description="Combining two samples together",
        parameters=combine_action_params, 
        reflexive=False,
        simulate=True,
        simulator = simulation_engine,
        container=container
    )
    
    combine_result = combine_action.execute()
    
    """==============================================
    Language model simulation response: 
    I'll think through this step-by-step:

    1. We're combining 1L of Hydrochloric Acid (HCl) with 1L of Sodium Hydroxide (NaOH).
    2. HCl is a strong acid, and NaOH is a strong base.
    3. When combined, they will undergo a neutralization reaction: HCl + NaOH → NaCl + H2O
    4. The reaction produces sodium chloride (table salt) and water.
    5. Since we have equal volumes of acid and base, they will likely neutralize each other completely.
    6. The concentration of the acid and base isn't specified, so we'll assume they're of equal concentration.

    Now, let's consider the outcomes:

    Outcome 1 (Likelihood 100.0):
    - Composition changes:
    * Hydrochloric Acid: 0%
    * Sodium Hydroxide: 0%
    * Sodium Chloride: 50%
    * Water: 50%
    - Reasoning: The HCl and NaOH react completely in a 1:1 ratio, neutralizing each other and forming NaCl and H2O. Assuming equal concentrations, the resulting solution would be approximately 50% NaCl and 50% H2O by volume.

    Outcome 2 (Likelihood 10.0):
    - Composition changes:
    * Hydrochloric Acid: 5%
    * Sodium Hydroxide: 0%
    * Sodium Chloride: 47.5%
    * Water: 47.5%
    - Reasoning: If the HCl was slightly more concentrated than the NaOH, there might be a small excess of acid left after the neutralization. This is less likely as we assumed equal concentrations, but it's a possibility.

    Outcome 3 (Likelihood 10.0):
    - Composition changes:
    * Hydrochloric Acid: 0%
    * Sodium Hydroxide: 5%
    * Sodium Chloride: 47.5%
    * Water: 47.5%
    - Reasoning: Conversely, if the NaOH was slightly more concentrated than the HCl, there might be a small excess of base left after the neutralization. This is equally as likely as Outcome 2, but less likely than complete neutralization.
    ==============================================
    """
    
    print_combine_result(combine_result)
    """
    Combine Action Result:
    Success: True

    Resulting Sample:

    Name: Combine_result

    Sample has 3 possible states:

    State (likelihood: 100.0):
    - Hydrochloric Acid: 0.0 %
    - Sodium Hydroxide: 0.0 %
    - Sodium Chloride: 50.0 %
    - Water: 50.0 %

    State (likelihood: 10.0):
    - Hydrochloric Acid: 5.0 %
    - Sodium Hydroxide: 0.0 %
    - Sodium Chloride: 47.5 %
    - Water: 47.5 %

    State (likelihood: 10.0):
    - Hydrochloric Acid: 0.0 %
    - Sodium Hydroxide: 5.0 %
    - Sodium Chloride: 47.5 %
    - Water: 47.5 %
    """
    

if __name__ == "__main__":
    demo_mixing_simulation() 