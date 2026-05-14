# -*- coding: mbcs -*-
# Abaqus/CAE Python 2.7
#
# 05_job_write_datacheck_submit3.py
#
# Runs 3 explicit load-case models:
#   - Model-Compression
#   - Model-Shear
#   - Model-Combined
#
# Behavior:
#   1. Create all 3 jobs
#   2. Save CAE after all jobs are fully created
#   3. Run datacheck + analysis for each job
#
# Result layout:
#   Results/
#       Model_<CASE>.cae
#       Compression/
#       Shear/
#       Combined/

from abaqus import mdb
from abaqusConstants import *
import os
import re

# ============================================================
# USER SETTINGS
# ============================================================
MODELS_TO_RUN = [
    ("Model-Compression", "Compression"),
    ("Model-Shear",       "Shear"),
    ("Model-Combined",    "Combined"),
]

RESULTS_DIRNAME = "Results"
JOB_BASENAME = "Buckling"

NUM_CPUS = 8
MEMORY_PERCENT = 90

SAVE_CAE_AFTER_JOB_CREATION = True
CAE_BASENAME = "Model"

RUN_DATACHECK = True
RUN_ANALYSIS  = True
# ============================================================


# ============================================================
# CASE DIRECTORY
# ============================================================
if 'CASE_DIR' not in globals() or not CASE_DIR:
    raise RuntimeError(
        "CASE_DIR is not defined.\n"
        "This script must be launched by RUN_ALL_PIPELINE3.py with CASE_DIR set "
        "to the Rhino Compute generated case folder."
    )

CASE_DIR = os.path.normpath(CASE_DIR)
CASE_NAME = os.path.basename(CASE_DIR.rstrip("\\/"))
# ============================================================


def _sanitize_name(s):
    s = re.sub(r'[^A-Za-z0-9_]+', '_', s)
    s = s.strip('_')
    if len(s) == 0:
        s = "JOB"
    return s[:80]


def _results_root():
    return os.path.join(CASE_DIR, RESULTS_DIRNAME)


def _case_results_path(case_label):
    return os.path.join(_results_root(), _sanitize_name(case_label))


def _ensure_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path)


def _safe_delete_job(job_name):
    try:
        if job_name in mdb.jobs.keys():
            del mdb.jobs[job_name]
    except:
        pass


def _build_job_name(case_label):
    return _sanitize_name("%s_%s_%s" % (JOB_BASENAME, case_label, CASE_NAME))


def _assert_models_exist():
    missing = []
    for model_name, case_label in MODELS_TO_RUN:
        if model_name not in mdb.models.keys():
            missing.append("%s (%s)" % (model_name, case_label))

    if missing:
        raise RuntimeError(
            "Required model(s) not found. Run previous scripts first.\nMissing:\n  - " +
            "\n  - ".join(missing)
        )


def _create_all_jobs():
    job_infos = []

    for model_name, case_label in MODELS_TO_RUN:
        res_path = _case_results_path(case_label)
        _ensure_dir(res_path)

        job_name = _build_job_name(case_label)
        _safe_delete_job(job_name)

        print("\nCreating job...")
        print("  CASE       :", case_label)
        print("  MODEL      :", model_name)
        print("  RESULTS_DIR:", res_path)
        print("  JOB_NAME   :", job_name)

        mdb.Job(
            name=job_name,
            model=model_name,
            description="Auto %s buckling job for case %s" % (case_label, CASE_NAME),
            type=ANALYSIS,
            memory=MEMORY_PERCENT,
            memoryUnits=PERCENTAGE,
            numCpus=NUM_CPUS,
            numDomains=NUM_CPUS,
            multiprocessingMode=DEFAULT
        )

        job_infos.append({
            "case_label": case_label,
            "model_name": model_name,
            "results_dir": res_path,
            "job_name": job_name,
        })

    return job_infos


def _save_cae(results_root):
    cae_name = _sanitize_name("%s_%s" % (CAE_BASENAME, CASE_NAME)) + ".cae"
    cae_path = os.path.join(results_root, cae_name)

    print("\nSaving CAE after all jobs are created...")
    print("CAE_PATH:", cae_path)

    mdb.saveAs(pathName=cae_path)
    return cae_path


def _run_job(job_info):
    case_label = job_info["case_label"]
    model_name = job_info["model_name"]
    res_path   = job_info["results_dir"]
    job_name   = job_info["job_name"]

    os.chdir(res_path)

    print("\n===================================================")
    print("RUNNING CASE :", case_label)
    print("MODEL        :", model_name)
    print("RESULTS_DIR  :", res_path)
    print("JOB_NAME     :", job_name)
    print("===================================================\n")

    job = mdb.jobs[job_name]

    print("Writing input...")
    job.writeInput(consistencyChecking=OFF)

    if RUN_DATACHECK:
        print("Running data check...")
        job.submit(consistencyChecking=OFF, datacheckJob=True)
        job.waitForCompletion()

    if RUN_ANALYSIS:
        print("Submitting analysis...")
        job.submit(consistencyChecking=OFF)
        job.waitForCompletion()

    print("DONE CASE   :", case_label)
    print("ODB         :", os.path.join(res_path, job_name + ".odb"))
    print("DAT         :", os.path.join(res_path, job_name + ".dat"))
    print("INP         :", os.path.join(res_path, job_name + ".inp"))

    job_info["odb_path"] = os.path.join(res_path, job_name + ".odb")
    job_info["dat_path"] = os.path.join(res_path, job_name + ".dat")
    job_info["inp_path"] = os.path.join(res_path, job_name + ".inp")

    return job_info


def main():
    results_root = _results_root()

    if not os.path.isdir(CASE_DIR):
        raise RuntimeError("CASE_DIR folder not found: %s" % CASE_DIR)

    _assert_models_exist()
    _ensure_dir(results_root)

    print("CASE_DIR     :", CASE_DIR)
    print("CASE_NAME    :", CASE_NAME)
    print("RESULTS_ROOT :", results_root)

    # 1) Create all jobs first
    job_infos = _create_all_jobs()

    # 2) Save CAE after job creation, before submission
    cae_path = None
    if SAVE_CAE_AFTER_JOB_CREATION:
        cae_path = _save_cae(results_root)

    # 3) Run all jobs
    all_runs = []
    for info in job_infos:
        out = _run_job(info)
        all_runs.append(out)

    print("\n===================================================")
    print("ALL JOBS COMPLETED")
    print("CASE_DIR     :", CASE_DIR)
    print("RESULTS_ROOT :", results_root)
    if cae_path:
        print("CAE FILE     :", cae_path)
    print("Cases run    : %d" % len(all_runs))
    for r in all_runs:
        print("  - %-12s -> %s" % (r["case_label"], r["job_name"]))
    print("===================================================\n")


if __name__ == "__main__":
    main()