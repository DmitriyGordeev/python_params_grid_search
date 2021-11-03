import re


class VarParser:

    def __init__(self):
        pass


    @staticmethod
    def parse_linspace(regex_matches):
        """Todo"""
        output_variables = []
        if len(regex_matches) != 0:
            for m in regex_matches:
                m = m[2:][:-2] # removing curly brakets
                elements = re.split("\s*,\s*", m)
                if len(elements) != 4:
                    raise ValueError(m, "len(elements) != 4")

                # trimming each element
                for i, e in enumerate(elements):
                    elements[i] = elements[i].strip()

                output_variables.append({
                    "name": elements[0],
                    "min": float(elements[1]),
                    "max": float(elements[2]),
                    "step": float(elements[3]),
                    "type": "S"
                })
        return output_variables


    @staticmethod
    def parse_enumerations(regex_matches):
        """Todo"""
        output_variables = []
        if len(regex_matches) != 0:
            for m in regex_matches:
                m = m[2:][:-2] # removing curly brakets
                parts = m.split(":")
                if len(parts) == 0:
                    raise ValueError("couldn't parse enumeration, example: [[var:10, 20, 30]]")

                name = parts[0].strip()
                digits = re.findall("[0-9]", parts[1])
                if len(digits) == 0:
                    raise ValueError("couldn't find values in enumeration: ", m)

                values_str = parts[1].split(",")
                values = []
                for v in values_str:
                    if v is "":
                        continue
                    f = float(v.strip())
                    if f.is_integer():
                        values.append(int(f))
                    else:
                        values.append(f)
                output_variables.append({"name": name, "values": values, "type": "E"})
        return output_variables
                






