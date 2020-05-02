"""
PROG: Automatisation du multi-docking
"""
# Python modules
import sys
import os
import glob
# Custom modules
import modules.parse_arguments as arg
import modules.custom_excepts as err
# Program
import src.loop_docking as dock
import src.loop_dlg_parsing as dlg
import src.loop_plip as plip


def main():
    '''
    Main function
    '''
    try:
        inputs = arg.InputArguments()
        inputs.init_arg()
        if inputs.option == "docking":
            dock.adt_nested_loops(inputs.parsed_input, "free", inputs.path_output)
        elif inputs.option == "complex":
            dlg.dlg_nested_loop(inputs.parsed_input, "free", inputs.path_output)
        elif inputs.option == "interact":
            plip.plip_nested_loop(inputs.parsed_input, "free", inputs.path_output)

    except err.customError as e:
        print(e.message)


if __name__=='__main__':
    main()
    print()