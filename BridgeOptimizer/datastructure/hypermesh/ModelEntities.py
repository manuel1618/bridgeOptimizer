"""
Classes for Creating the Elements in Hypermesh
"""


class Material:
    """
    Simple Material class modelling isotropic behaviour 

    Parameters:
    ---------
    yngs_mdl: float
        The Youngs Module (recommended to be inputted in MPa)
    poisson_ratio : float
        The Poisson's ratio (unitless)
    density : float
        Density of the material (important for mass calculations)

    """

    def __init__(self, yngs_mdl: float, poisson_ratio: float, density: float) -> None:
        self.yngs_mdl = yngs_mdl
        self.poisson_ratio = poisson_ratio
        self.density = density


class Property:
    """
    Property Class for modelling PROD Properties in Hypermesh

    Parameters:
    ---------
    material : Material
        the material assigned to the property
    diameter : float
        the diameter for the PRod Beamsection (full rod, no tube)
    optimization : bool
        flag if its a optimization property - used in creating design responses and variables
    """
    instances = []

    def __init__(self, material: Material, diameter: float, optimization: bool) -> None:
        Property.instances.append(self)
        self.material = material
        self.diameter = diameter
        self.optimization = optimization


class Component:
    """
    Class for the Component Entity in Hypermesh

    Pramaters:
    ---------

    property : Property
        the Property which is assigned to the Component (and by that the Material definition)
    """
    instances = []

    def __init__(self, property: Property) -> None:
        Component.instances.append(self)
        self.property = property
        pass
