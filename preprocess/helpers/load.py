#!/usr/bin/env python

# This script has functions that can be used to load a particular pickle file

import fnmatch
import numpy
import os
import pickle

## Find Files

def recursive_find(base, pattern=None):
    '''recursive find will yield files in all directory levels that 
       match a particular pattern below a base path.
       
       Parameters
       ==========
       base: the base path to look under
       pattern: the pattern to search for
       
    '''
    if pattern is None:
        pattern = "*"

    for root, dirnames, filenames in os.walk(base):
        for filename in fnmatch.filter(filenames, pattern):
            yield os.path.join(root, filename)


## Loading

def load_all(image_pkl, 
             pad_images=True,
             length_cutoff=30,
             padding_length=80,
             script_name=None):

    '''load all data from repository, ignoring extensions, etc.
       Images that are under 2 lines will be filtered out,
       those between 2 and 80 will have padding added.
       
       Parameters
       ==========
       image_pkl: full path to the image pickle to load
       pad_images: if True, run add_padding function based on padding params
       length_cutoff: images with fewer than length_cutoff lines discarded
       padding_length: add padding so length == this value (# lines)
       script_name: if defined, load only scripts with this name included.
       
    '''

    images = pickle.load(open(image_pkl,"rb"))

    # Create a final list of images
    final = []

    for filename,subset in images.items():

        # Skip script if doesn't match name, if user wants this
        if script_name is not None:
            if script_name.lower() not in filename:
                continue

        # Are we adding padding / filtering?
        if pad_images is True:
            subset = add_padding(subset, length_cutoff, padding_length)

        if len(subset) > 0:
            final.append(subset)

    return make_input_data(final)


def load_by_extension(image_pkl, 
                      pad_images=True,
                      length_cutoff=30,
                      padding_length=80):

    '''load data based on file extensions. The single pickle provided
       for a repository will be returned with a vector of extensions
       matching it. Images that are under 2 lines will be filtered out,
       those between 2 and 80 will have padding added.
       
       Parameters
       ==========
       image_pkl: full path to the image pickle to load
       pad_images: if True, run add_padding function based on padding params
       length_cutoff: images with fewer than length_cutoff lines discarded
       padding_length: add padding so length == this value (# lines)
       
    '''

    images = pickle.load(open(image_pkl,"rb"))

    # Create a dictionary lookup
    lookup = dict()

    for filename,subset in images.items():

        # Are we adding padding / filtering?
        if pad_images is True:
            subset = add_padding(subset, length_cutoff, padding_length)

        ext = filename.split('/')[-1].split('.')[-1]
        if ext in lookup and subset:
            lookup[ext].append(subset)
        else:
            lookup[ext] = [subset]  

    # Convert to correct type
    for ext, images in lookup.items():
        lookup[ext] = make_input_data(images)

    return lookup


def add_padding(images, 
                length_cutoff=30, 
                padding_length=80):

    '''Add padding to an images array.
    
       Parameters
       ==========
       images: an NxN array of images
       length_cutoff: images with fewer than length_cutoff lines discarded
       padding_length: add padding so length == this value (# lines)
       
    '''
    padded = []

    # iterate through the list of 80x80 images
    for idx in range(len(images)):
        current_image = images[idx]

        # Only consider if greater than the length cutoff
        if current_image.shape[0] > length_cutoff:

            # Image needs padding.
            if current_image.shape[0] < padding_length:
                current_image = pad_image(current_image)

            # Only add to the padded list if we had any matching
            if len(current_image) > 0:
                padded.append(current_image)
 
    return padded


def pad_image(image, size=(80,80), const=32):
    '''Pad an array to a certain size with constant value (ordinal value of 32
       corresponds to a space).
       
       Parameters
       ==========
       image: an NxM numpy array
       size: a tuple of dimensions for the image
       const: the constant value to use for the padding (ordinal 32 is space)
       
    '''
    # check for equivalent dimensions (2)
    assert len(size) == len(image.shape)

    # Check that each dimension is within upper boundary
    for i in range(len(size)):
        assert image.shape[i] <= size[i]
        
    padded = numpy.ones(size) * const
    padded[:image.shape[0], :image.shape[1]] = image
    return padded


def make_input_data(images): 
    '''Take a list of lists and convert to the correct (numpy array)
       for being an input/output train/test set 

        Parameters
        ==========
        images: a list of lists, each sub list has one or more 80x80 images
        
     '''
    return numpy.concatenate([numpy.array(a) for a in images])
