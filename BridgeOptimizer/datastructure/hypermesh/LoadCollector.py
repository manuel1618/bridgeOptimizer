class LoadCollector:
    instances = []

    def __init__(self) -> None:
        self.loads = []
        LoadCollector.instances.append(self)

    def get_id(self):
        return LoadCollector.instances.index(self)+1

    """
    Load collecotr can contain Forces or SPCs currently - this method finds out what this collector contains
    """

    def get_load_collector_type(self):
        load_collector_type = None
        if len(self.loads) > 0:
            load_collector_type = type(self.loads[0])
        # check if its homogenous
        for bc in self.loads:
            if type(bc) != load_collector_type:
                print(type(bc))
                print("and the var:")
                print(load_collector_type)
                print(
                    "ERROR: Load Collector has non homogenous list of loads (spc and loads)")
                return None
        return load_collector_type
