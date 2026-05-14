# -*- coding: mbcs -*-
# Abaqus/CAE Python 2.7

import os
import sys
import traceback

# ============================================================
# SCRIPT FOLDER
# ============================================================
SCRIPTS_DIR = r"C:\Rhino Hiwi\Thesis\cad_to_stp\BoxShape_Iprofile\iprofile_grid_one_stage_scripts"

PIPELINE = [
    "00_import_parts_makeprecise_assemble3_Iprofile_grid.py",
    "Mesh_testing2_Iprofile_grid.py",
    "Creating_Sets5_ALLINONE_Iprofile_grid.py",
    #"Creating_Sets5_ALLINONE2.py",
    #"Creating_Sets5_ALLINONE2_old.py",
    "04_property_step_interaction_load_bc_Iprofile_grid.py",
    #"04_property_step_interaction_load_bc3.py",
    "05_job_write_datacheck_submit_Iprofile_grid.py",
    #"06_postprocess_dat2.py",
    "06_postprocess_dat_Iprofile_grid.py",
]
# ============================================================


def _get_case_dir():
    """
    CASE_DIR must be provided from outside when Abaqus is launched.

    Preferred usage:
        abaqus cae noGUI=RUN_ALL_PIPELINE.py -- "C:\\path\\to\\case_folder"

    Then inside Abaqus:
        sys.argv[-1] -> case folder path
    """
    if len(sys.argv) < 2:
        raise RuntimeError(
            "CASE_DIR argument not provided.\n"
            "Launch Abaqus like:\n"
            'abaqus cae noGUI="RUN_ALL_PIPELINE2.py" -- "C:\\path\\to\\case_folder"'
        )

    case_dir = sys.argv[-1]

    if not case_dir:
        raise RuntimeError("Received empty CASE_DIR argument.")

    case_dir = os.path.normpath(case_dir)

    if not os.path.isdir(case_dir):
        raise RuntimeError("CASE_DIR does not exist:\n%s" % case_dir)

    return case_dir


def run_script(script_name):
    script_path = os.path.join(SCRIPTS_DIR, script_name)

    if not os.path.exists(script_path):
        raise RuntimeError("Script not found: %s" % script_path)

    print("\n===================================================")
    print("RUNNING:", script_name)
    print("===================================================\n")

    # Important: use shared globals() so CASE_DIR remains available
    execfile(script_path, globals())


def main():
    global CASE_DIR

    CASE_DIR = _get_case_dir()

    print("\nSTARTING ABAQUS AUTOMATED PIPELINE\n")
    print("CASE_DIR :", CASE_DIR)
    print("SCRIPTS_DIR :", SCRIPTS_DIR)

    for script in PIPELINE:
        try:
            run_script(script)

        except Exception as e:
            print("\n###################################################")
            print("PIPELINE STOPPED")
            print("FAILED SCRIPT:", script)
            print("CASE_DIR:", CASE_DIR)
            print("ERROR:", str(e))
            print("###################################################\n")

            traceback.print_exc()
            raise

    print("\n===================================================")
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("CASE_DIR :", CASE_DIR)
    print("===================================================\n")


if __name__ == "__main__":
    main()