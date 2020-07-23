#!/usr/bin/python
import os
from opendm import log
from opendm import config
from opendm import system
from opendm import io
from opendm.progress import progressbc
from stages.dataset import DatasetStage
from stages.colmap import FeaturesStage, MatchingStage, SparseStage, DenseStage

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
    dense = DenseStage('dense', args, progress=60.0)

    # Normal pipeline
    dataset.connect(features) \
            .connect(matching) \
            .connect(sparse) \
            .connect(dense)

        # dataset.connect(split) \
   # try:
    dataset.run()

    log.ODM_INFO("*******************************************************")
    log.ODM_INFO("NodeCOLMAP has ended! Woohoo! %s" % system.now())
    log.ODM_INFO("*******************************************************")
#    except Exception as e:
 #       log.ODM_ERROR(e)
  #      exit(1)

