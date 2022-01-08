from .LoadCollector import LoadCollector


class LoadStep:
    """
    Load Collector (for now just linear static)
    Prameters: 
    ----------
    instances: List
        class variable, all load steps
    """

    instances = []
    spc_loadCollector: LoadCollector
    load_loadCollector: LoadCollector

    def __init__(self, spc_loadCollector: LoadCollector, load_loadCollector: LoadCollector) -> None:
        LoadStep.instances.append(self)
        self.spc_loadCollector = spc_loadCollector
        self.load_loadCollector = load_loadCollector

    def get_id(self) -> int:
        id = LoadStep.instances.index(self)+1
        return id
