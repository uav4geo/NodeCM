import os, subprocess
from opendm import log
from repoze.lru import lru_cache

@lru_cache(maxsize=None)
def has_gpus():
    # TODO: python3 use shutil.which
    if not os.path.exists("/usr/bin/nvidia-smi"):
        return False

    try:
        out = subprocess.check_output(["nvidia-smi", "-q"])
        for line in out.split("\n"):
            line = line.strip()
            if "Attached GPUs" in line:
                _, numGpus = map(lambda i: i.strip(), line.split(":"))
                numGpus = int(numGpus)
                return numGpus > 0

    except Exception as e:
        log.ODM_WARNING("Cannot call nvidia-smi: %s" % str(e))
        return False