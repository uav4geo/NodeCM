#!/usr/bin/python
import os
from opendm import log
from opendm import config
from opendm import system
from opendm import io
from opendm.progress import progressbc
from stages.dataset import DatasetStage
from stages.colmap import FeaturesStage, MatchingStage, SparseStage, GeoregisterStage, DenseStage
from stages.mesh import MeshStage
from stages.mvstex import TextureStage
from stages.dem import DEMStage
from stages.ortho import OrthoStage
from stages.georeferencing import GeoreferencingStage

if __name__ == '__main__':
    args = config.config()

    log.ODM_INFO('Initializing NodeCOLMAP app - %s' % system.now())
    log.ODM_INFO(args)

    progressbc.set_project_name(os.path.basename(args.project_path))

    # Initializes the application and defines the pipeline stages
    dataset = DatasetStage('dataset', args, progress=5.0)
    features = FeaturesStage('features', args, progress=10.0)
    matching = MatchingStage('matching', args, progress=15.0)
    sparse = SparseStage('sparse', args, progress=30.0)
    georegister = GeoregisterStage('georegister', args, progress=32.0)
    dense = DenseStage('dense', args, progress=60.0)
    georeferencing = GeoreferencingStage('georeferencing', args, progress=65.0)
    dem = DEMStage('dem', args, progress=68.0)
    mesh = MeshStage('mesh', args, progress=75.0)
    texture = TextureStage('texture', args, progress=90.0)
    ortho = OrthoStage('ortho', args, progress=100.0)

    # Normal pipeline
    dataset.connect(features) \
            .connect(matching) \
            .connect(sparse) \
            .connect(georegister) \
            .connect(dense) \
            .connect(georeferencing) \
            .connect(dem) \
            .connect(mesh) \
            .connect(texture) \
            .connect(ortho)

        # dataset.connect(split) \
    dataset.run()

    log.ODM_INFO("*******************************************************")
    log.ODM_INFO("NodeCOLMAP has ended! Woohoo! %s" % system.now())
    log.ODM_INFO("*******************************************************")
