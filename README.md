# NodeCM

A GPU-enabled photogrammetry pipeline to generate georeferenced point clouds, orthophotos and elevation models from aerial images using [COLMAP](https://github.com/colmap/colmap/).

![image](https://user-images.githubusercontent.com/1951843/88435907-30466480-cdd1-11ea-992d-9c77ed85943b.png)

![image](https://user-images.githubusercontent.com/1951843/88436063-7f8c9500-cdd1-11ea-9e06-9df9e87c4e7f.png)


It's compatible with the [NodeODM API](https://github.com/OpenDroneMap/NodeODM) so it works out of the box with many of the tools of the OpenDroneMap ecosystem such as [WebODM](https://github.com/OpenDroneMap/WebODM), [ClusterODM](https://github.com/OpenDroneMap/ClusterODM) and [CloudODM](https://github.com/OpenDroneMap/CloudODM).

While a GPU can speed up certain steps of the pipeline, it is not required for use. CPU algorithms are implemented in case a GPU is not available.

:warning: NodeCM is in early stages of development. It works on several test datasets, but software faults are expected.

## Getting Started

We recommend that you setup NodeCM using [Docker](https://www.docker.com/).

First, build your image (this will take a while):

```bash
$ git clone https://github.com/uav4geo/NodeCM
$ cd NodeCM
$ docker build -t uav4geo/nodecm .
```

* Then from a shell, simply run:

```
$ docker run --rm -ti -p 3000:3000 uav4geo/nodecm
```

* Open a Web Browser to `http://localhost:3000` (or the IP of your docker machine)
* Load [some images](https://github.com/OpenDroneMap/ODM/tree/master/tests/test_data/images)
* Press "Start Task"
* Go for a walk :)

:warning: If you want to use the GPU features of NodeCM, you need to have one or more NVIDIA GPUs compatible with CUDA and make sure that docker can communite with it. You can run `nvidia-smi` to test that docker is configured properly:

```bash
$ docker run --rm --gpus all nvidia/cuda:10.0-base nvidia-smi
```

If you see an output that looks like this:

```
Fri Jul 24 18:51:55 2020       
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 440.82       Driver Version: 440.82       CUDA Version: 10.2     |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
```

You're in good shape!

Then you **must pass** `--gpus all` to the docker command:

```bash
$ docker run --rm --gpus all -ti -p 3000:3000 uav4geo/nodecm
```

See https://github.com/NVIDIA/nvidia-docker for information on docker/NVIDIA setup.

## Run from the command line

You don't have to run NodeCM from a browser. You can also run it directly from the command line (useful for scripting workflows):

First, place some images in your project's `images` folder:

```bash
$ ls /path/to/project
images
$ ls /path/to/project/images
DJI_0018.JPG    DJI_0019.JPG    ...
```

Then run:

```bash
$ ./nodecm /path/to/project --orthophoto-resolution 2
```

If you want to use GPUs use:

```bash
$ USE_GPU=ON ./nodecm /path/to/project --orthophoto-resolution 2
```

To view all command line options run:

```bash
$ ./nodecm --help
```

## Using an external hard drive

If you want to store results on a separate drive, map the `/app/NodeODM/data` folder to the location of your drive:

```bash
$ docker run -p 3000:3000 -v /mnt/external_hd:/app/NodeODM/data uav4geo/nodecm
```

This can be also used to access the computation results directly from the file system.

### Test images

You can find some test drone images [here](https://github.com/OpenDroneMap/odm_data).

## Contributing

We welcome contributions! Send pull requests :heart: bug reports and whatever is useful to you.

## Roadmap

NodeCM is in beta. It hasn't been battle-tested and issues are expected. We are aware of the following list of things that still need to be improved (help us improve them)!

 - [ ] DSM/DTM interpolation (currently DEMs don't look so good)
 - [ ] Better meshing algorithms (currently PoissonRecon is less than ideal)
 - [ ] GSD estimates. Currently they are not taken in consideration, so memory is potentially wasted and output resolutions cannot be automatically calculated
 - [ ] GCPs support. COLMAP has basic support for geo-registration which will align the reconstruction based on an affine transformation of the camera centers, but no support for GCPs.
 - [ ] Bug fixing (help us and report them on the issue tracker)

## License

This codebase: Affero GPL

COLMAP: BSD

OpenDroneMap/NodeODM modules: GPL


## GPU License Restrictions

Because of restrictive licenses in some of COLMAP's dependencies, if you use the GPU features of NodeCM, you **cannot** use NodeCM for purposes other than educational, research and non-profit without obtaining permission from the `University of North Carolina at Chapel Hill`. COLMAP uses the SIFT GPU library, which is released under the following [license](https://github.com/colmap/colmap/blob/dev/lib/SiftGPU/LICENSE):

```
////////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2007 University of North Carolina at Chapel Hill
//  All Rights Reserved
//
//  Permission to use, copy, modify and distribute this software and its
//  documentation for educational, research and non-profit purposes, without
//  fee, and without a written agreement is hereby granted, provided that the
//  above copyright notice and the following paragraph appear in all copies.
//
//  The University of North Carolina at Chapel Hill make no representations
//  about the suitability of this software for any purpose. It is provided
//  'as is' without express or implied warranty.
//
//  Please send BUG REPORTS to ccwu@cs.unc.edu
//
////////////////////////////////////////////////////////////////////////////
```

We understand this is unfortunate. Contribute a PR to replace SIFT GPU in COLMAP.
