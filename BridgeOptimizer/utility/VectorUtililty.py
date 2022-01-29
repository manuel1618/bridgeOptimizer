from typing import List


class VectorUtility:

    @classmethod
    def are_linear_dependent(self, v1: List, v2: List) -> bool:
        """
        Simple method to see if two vectors (as lists) have the same direction
        """
        if (len(v1) != len(v2)):
            print("Error: Vectors don't have the same length")
            return False
        else:
            for i in range(len(v1)):
                if v1[i] == 0 and v2[i] != 0:
                    return False
                if v2[i] == 0 and v1[i] != 0:
                    return False
                if v2[i] != 0:
                    factor = v1[i]/float(v2[i])
            if factor == 0:
                return False

            for i in range(len(v1)):
                if (v1[i] == 0 and v2[i] == 0):
                    if factor != 1:
                        return False
                elif (v1[i]/float(v2[i]) != factor):
                    return False
            return True
