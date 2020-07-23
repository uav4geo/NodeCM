import os
from opendm import io
from opendm import log
from opendm import system
from pipes import quote

class ColmapContext:
    def __init__(self, project_path):
        self.project_path = project_path

    def run(self, command, **kwargs):
        params = ["--{} {}".format(k, quote(str(v))) for (k,v) in kwargs.items()]
        system.run("colmap {} {}".format(command, " ".join(params)))
