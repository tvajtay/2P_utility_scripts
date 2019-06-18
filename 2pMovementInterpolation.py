#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 22 13:25:56 2019

@author: tvajtay

Purpose is to take a Tiff stored in an HDF5 and interpolate between frame matrices
before and after indexed frames for movement from a boolean list also stored in the same HDF5.
"""

import h5py
import numpy as np

#Load in Data, this may need to be changed but I saved the binary index of movement and the concatenated TIFF in an HDF5 file.
Data = h5py.File('2D1_Day1.hdf5','r')
#Need to work on the previous step of how to ID bad frames, also maybe a reference frame approach?

#Seperate data and change to numpy arrays
index = Data['/index'][()] #New way to do .value
stack = Data['/stack'][()]

#Michael Osthege's vectorized 1-D interpolator @michaelosthege
#https://gist.github.com/michaelosthege/e20d242bc62a434843b586c78ebce6cc
def interpolate(x_fix, y_fix, x_var):
    x_repeat = np.tile(x_var[:,None], (len(x_fix),))
    distances = np.abs(x_repeat - x_fix)

    x_indices = np.searchsorted(x_fix, x_var)

    weights = np.zeros_like(distances)
    idx = np.arange(len(x_indices))
    weights[idx,x_indices] = distances[idx,x_indices-1]
    weights[idx,x_indices-1] = distances[idx,x_indices]
    weights /= np.sum(weights, axis=1)[:,None]

    y_var = np.dot(weights, y_fix.T)
    return y_var


def badframe_interpolation(index, stack):
    """
    Cycles through a supplied index list and 1D interpolates between the frames
    before and after the indexed movement/bad frames in the stack numpy array
    'index' is a 1D numpy array
    'stack' is a 3D numpy array with indices [frames, height, width]
    """
    flag = 1
    i = 0
    max_frames = len(index)

    while flag:
        #What to do if movement is already occurring at beginning
        if i == 0:
            if index[i]: #If first frame has movement
                while index[i]:
                    i = i + 1

                end_source = stack[i,:,:]

                for j in range(0,i):
                    stack[j,:,:] = end_source
            else:
                i = i + 1

        #The rest of the conditions
        else:
            if index[i]: #If current frame is indexed as movement
                start_source = stack[i-1,:,:]
                start_frame = i

                while index[i] and i < max_frames:
                    i = i + 1

                if i == max_frames: #Worst case scenario, movement till the end
                    for j in range(i,max_frames):
                        stack[j,:,:] = end_source
                    flag = 0
                    break

                end_source = stack[i,:,:]

                # Create sequential list of frames to interpolate
                frames = range(start_frame,i)

                #Need to watch out for how the dimensions maintain orientation
                stack[start_frame:i,:,:] = interpolate(frames,[start_frame, i],[start_source, end_source])

            else:
                if i < max_frames:
                    i = i+1 #To just skip over good frames

                else:
                    flag = 0
                    break
    return stack
