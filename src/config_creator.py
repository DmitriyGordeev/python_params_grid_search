import ntpath
import os
import re
from xml.etree import ElementTree

import pandas

import varparser


class ConfigCreator:
    def __init__(self, pattern_path, configs_out_dir):
        """
            Constructor
            :param pattern_path: path to the pattern config file with tweakable params
            :param configs_out_dir: path to a directory where generated config files will be stored
        """
        self.pattern = self.read_pattern(pattern_path)
        self.configs_out_dir = configs_out_dir
        self.vars = []
        self.find_vars()
        self.expr = self.get_constraints()
        self.pattern_basename = os.path.splitext(ntpath.basename(pattern_path))[0]
        param_names = self.get_names()
        param_names.insert(0, "itr")
        self.params_table = pandas.DataFrame(columns=param_names)
        self.current_params = pandas.Series()

    @staticmethod
    def read_pattern(pattern_path):
        """
            Reads a pattern file
            :param pattern_path: path specified to a pattern config file
            :return: string with file content
        """
        f = open(pattern_path, "r")
        content = f.read()
        f.close()
        return content

    def find_vars(self):
        """
            Collects the names of the variables specified for optimizing
            e.g. {{param1, 10, 20, F}}, {{param2, 10, 20, F}} and adds it to 'self.vars' array
        """
        for l in self.pattern.split("\n"):
            self.parse_variables(l)
        self.search_duplicates()

    def parse_variables(self, s):
        """
            Parses a particular variable and gets its settings:
             name, min value, max value and flag: I-int, F-float
             and adds it to 'self.vars' array
             example: {{x, 0, 10, I}}
            :param s: a line where variable pattern might be stored
        """
        core_linspace = re.findall("{{\s*[a-zA-Z_0-9-]+\s*,\s*[0-9.-]+\s*,\s*[0-9.-]+\s*,\s*[0-9.-]+\s*}}", s)
        linspace_vars = []
        if len(core_linspace) != 0:
            linspace_vars = varparser.VarParser.parse_linspace(core_linspace)

        core_enumeration = re.findall("\[\[\s*[0-9A-Za-z_]+\s*:\s*[\s0-9.,-]+\s*\]\]", s)
        enum_vars = []
        if len(core_enumeration) != 0:
            enum_vars = varparser.VarParser.parse_enumerations(core_enumeration)

        if len(linspace_vars + enum_vars) != 0:
            self.vars = self.vars + (linspace_vars + enum_vars)

    def search_duplicates(self):
        """
            Searches for duplicates in 'self.vars'
             and produces a ValueError in case there are
        """
        for i in range(0, len(self.vars)):
            for j in range(i + 1, len(self.vars)):
                if self.vars[j]["name"] == self.vars[i]["name"]:
                    raise ValueError("=================================================\n" +
                                     "Variable '" + self.vars[i]["name"] + "' is specified "
                                                                           "for optimization multiple times with " +
                                     "different params")

    def create_config(self, x, num_of_itr, suffix, write_config=True):
        """
            Generates and writes a config with params according to x
            Each call of create_config will put a pandas.Series of
            current params to self.params_table

            :param x: an array of values to place in the pattern
            :param num_of_itr: number of iteration
            :param suffix: any string to place in the filename ending
            :param write_config
            :return: tuple: (params dict, an absolute path of a generated config file which has been written down)
        """
        config = self.pattern
        self.current_params = pandas.Series()

        # Applying constraints specified inside <optimizer>...</optimizer>:
        expr = self.modify_expression()
        try:
            exec(expr)
        except Exception as e:
            print("[EXCEPTION] exec has produced an exception:", e)
            print("Expression is: ", expr)
            exit(1)

        local_vars_dict = locals()

        # Unmapping variable name and replace it inside the pattern
        self.current_params["itr"] = num_of_itr
        for i, v in enumerate(x):
            var_name = self.vars[i]["name"]
            val = float(v)
            if val.is_integer():
                val = int(val)
            config = re.sub("{{\s*" + var_name + "\s*,\s*[0-9.-]+\s*,\s*[0-9.-]+\s*,\s*[0-9.-]+\s*}}", str(val), config)
            config = re.sub("\[\[\s*" + var_name + "\s*:\s*[\s0-9.,-]+\s*\]\]", str(val), config)
            self.current_params[var_name] = v

        self.params_table = self.params_table.append(self.current_params, ignore_index=True)

        # Searching for variables generated inside <optimzier></optimizer> via exec and
        # replace with value
        config_lines = config.split("\n")
        for i in range(0, len(config_lines)):
            for varname in local_vars_dict:
                varmatches = re.findall("{{.*" + varname + ".*}}", config_lines[i])
                if len(varmatches) != 0:
                    varmatch = varmatches[0]
                    varmatch = varmatch.replace(varname, str(local_vars_dict[varname]))
                    config_lines[i] = config_lines[i].replace(varmatches[0], varmatch)

        # Replacing formulas with eval():
        # splitting config into lines, then search equations in each line
        # if there are - do evaluation and replace with resulting value
        for i in range(0, len(config_lines)):
            expressions_in_line = ConfigCreator.all_expr(config_lines[i])
            for e in expressions_in_line:
                val = float(ConfigCreator.eval(self, e, x))
                if val.is_integer():
                    val = int(val)
                config_lines[i] = config_lines[i].replace("{{" + e + "}}", str(val))

        # Join back config_lines:
        config = "\n".join(config_lines)

        # Removing optimizer tag:
        config = self.remove_optimizer_node(config)
        config_path = self.configs_out_dir + "/" + self.pattern_basename + ".itr-" + str(suffix) + ".xml"
        if write_config:
            config_file = open(config_path, "w")
            config_file.writelines(config)
            config_file.close()

        return self.current_params, config_path

    def get_names(self):
        """
            Exposes name of each variable from 'self.vars'
            as array
            :return: array of strings
        """
        out = []
        for v in self.vars:
            out.append(v["name"])
        return out

    def get_lowers(self):
        """
            Exposes minimal value of each variable from 'self.vars'
            as array
            :return: array of floats
        """
        out = []
        for v in self.vars:
            out.append(v["min"])
        return out

    def get_uppers(self):
        """
            Exposes maximum value of each variable from 'self.vars'
            as array
            :return: array of floats
        """
        out = []
        for v in self.vars:
            out.append(v["max"])
        return out

    def get_types(self):
        """
            Exposes type of each variable from 'self.vars'
            as array
            :return: array of string
        """
        out = []
        for v in self.vars:
            out.append(v["type"])
        return out

    def get_constraints(self):
        # Reading <optimizer> tag from xml
        root = ElementTree.ElementTree(ElementTree.fromstring(self.pattern))
        value = ""
        for element in root.findall("optimizer"):
            value = element.text

        # Trimming each expression line to avoid exec errors:
        lines = value.split("\n")
        for i, l in enumerate(lines):
            if l is "":
                continue
            lines[i] = str.strip(l)

        # Joining together into single expression with ;-separated to exec as a single line
        lines = filter(lambda a: a != "", lines)
        expr = ";".join(lines)
        return expr

    def modify_expression(self):
        # find index of a variable in the vars array and replace it with 'x[i]'
        expr = self.expr
        for i, v in enumerate(self.vars):
            if v["name"] in self.expr:
                expr = expr.replace(v["name"], "x[" + str(i) + "]")
        return expr

    @staticmethod
    def remove_optimizer_node(input_xml):
        doc = ElementTree.ElementTree(ElementTree.fromstring(input_xml))
        root = doc.getroot()
        for e in root.findall('optimizer'):
            root.remove(e)
        xmlstr = ElementTree.tostring(root, encoding='utf8', method='xml')
        return xmlstr

    def eval(self, expression_string, values):
        """ Evaluates and expression with given values according to self.vars
            :param expression_string - a string representing and expression to evaluate
            :param values - array of values to substitute variables (from self.vars) in expression
            :return - equation result
        """
        if len(self.vars) != len(values):
            raise ValueError("len(self.vars) != len(values)")

        for i, v in enumerate(self.vars):
            if v['name'] in expression_string:
                expression_string = expression_string.replace(v['name'], str(values[i]))

        return eval(expression_string)

    @staticmethod
    def find_expr(input_str, start_index):
        p_open = input_str.find('{{', start_index)
        p_close = input_str.find("}}", p_open + 1)

        if p_open != -1 and p_close != -1:
            return p_close, input_str[p_open + 2:p_close]
        else:
            return -1, ""

    @staticmethod
    def all_expr(input_str):
        refs = []
        start_index = 0
        while start_index < len(input_str):
            start_index, match = ConfigCreator.find_expr(input_str, start_index)
            if match != "":
                refs.append(match)
            if start_index == -1:
                break
        return refs

    def get_params_table(self):
        return self.params_table
