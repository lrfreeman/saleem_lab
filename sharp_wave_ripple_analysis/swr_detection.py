#Custom libs
from utils import helper

#OS libaries
import numpy as np
import matplotlib.pyplot as plt
import time
from scipy import signal
from ripple_detection import Karlsson_ripple_detector, Kay_ripple_detector
from ripple_detection.simulate import simulate_time
from ripple_detection import filter_ripple_band
from utils.auto_mat_to_python import convert_matlab_struct

#hyper parameters
fs_of_cam = 25 #hz
fs_desired = 30000 #khz

#A function to detect sharp wave ripples
def detect_SWRs(orgignal_fs,
                new_fs,
                lfp_data,
                hippocampal_channels,
                saved_file_string,
                mat_file,
                flag):

    print("Commencing Kay 2016 ripple detection algorithm..")

    #Calculate pre and post sleep times
    matlab_object = convert_matlab_struct(mat_file)
    time = matlab_object.dic['t']
    linear_time = matlab_object.dic['linear']['timestamps']
    velocity = matlab_object.dic['v_cm']
    pre_task_sleep_time, post_task_sleep_time = helper.determine_sleep_times(time, linear_time)
    velocity = helper.interpolate(velocity, fs_of_cam, fs_desired)

    #Load, downsample and filter data
    matrix = np.load(lfp_data) #Load the data into a numpy array

    #Convert time to sample length
    pre_task_sleep_time = len(helper.interpolate(pre_task_sleep_time,
                                                 fs_of_cam,
                                                 fs_desired))
    post_task_sleep_time = len(helper.interpolate(post_task_sleep_time,
                                                  fs_of_cam,
                                                  fs_desired))

    print("len of pre",  pre_task_sleep_time)
    print("len of post", post_task_sleep_time)

    #Condition for pre sleep
    if flag == "pre":
        matrix = matrix[:pre_task_sleep_time , :] #Load the data into a numpy array

    #Condition for pre sleep
    elif flag == "post":
        matrix = matrix[-post_task_sleep_time: , :] #Load the data into a numpy array

    else:
        print('Error when choosing pre or post sleep calculations')

    raw_data, n_samples = helper.downsample(matrix, orgignal_fs, new_fs) #Downsample the data
    filtered_signal = filter_ripple_band(raw_data) #Bandpass filter lfp signal to 15-250hz
    desired_channels = slice(hippocampal_channels[0],
                             hippocampal_channels[-1] + 1,
                             1) #Create a slice to index lfp matrix by
    filtered_signal = filtered_signal[:, desired_channels] #Select hippocampal channels
    time = simulate_time(n_samples, new_fs) #Calculate the time of each sample in seconds

    #Detect and save ripples to numpy array
    velocity = velocity[:len(filtered_signal)] #The ncs conversion file looses some data so have to remove end of velocity
    assert len(velocity) == len(filtered_signal), "The two don't match, caused by error from ncs import and indexing hasn't rectified len error"
    kay_ripples = Kay_ripple_detector(time,
                                      filtered_signal,
                                      velocity,
                                      new_fs,
                                      zscore_threshold=3.0) #Alter zscore threshold to make more or less sensitive
    ripple_list = kay_ripples.values
    np.save("/Users/freeman/Documents/saleem_folder/data/VC_Data_Marta/np_arrays/"
            +
            "{}".format(flag + saved_file_string), ripple_list)
    print("The number of ripples detected: {} \n".format(len(kay_ripples.values)))

#Lfp data should be in the format [mv, channel]
if __name__ == "__main__":
    lfp = "/Users/freeman/Documents/saleem_folder/data/VC_Data_Marta/np_arrays/QBLU_Dark_Day5_250719.npy"
    mat = "/Users/freeman/Documents/saleem_folder/data/VC_Data_Marta/QBLU_Dark_Day5_250719/extracted_position.mat"
    file_save_name = "_sleep_Ripples_for_QBLU_Dark_Day5_250719.npy"
    channels = [8,9,10]

    # lfp = "/Users/freeman/Documents/saleem_folder/data/VC_Data_Marta/np_arrays/MBLU_Dark_Day10_090119.npy.npy"
    # mat = "/Users/freeman/Documents/saleem_folder/data/VC_Data_Marta/MBLU_Dark_Day10_090119.npy/extracted_position.mat"
    # file_save_name = "_sleep_Ripples_for_MBLU_Dark_Day10_090119.npy"
    # # channels = [8,9,10]

    # lfp = "/Users/freeman/Documents/saleem_folder/data/VC_Data_Marta/np_arrays/QBLU_YMaze_Day8_280719.npy"
    # mat = "/Users/freeman/Documents/saleem_folder/data/VC_Data_Marta/QBLU_YMaze_Day8_280719/extracted_position.mat"
    # file_save_name = "_sleep_Ripples_for_QBLU_YMaze_Day8_280719"
    # channels = [8,9,10]

    # lfp = "/Users/freeman/Documents/saleem_folder/data/VC_Data_Marta/np_arrays/Ymaze_Day3_220719.npy"
    # mat = "/Users/freeman/Documents/saleem_folder/data/VC_Data_Marta/Ymaze_Day3_220719/extracted_position.mat"
    # file_save_name = "_sleep_Ripples_for_Ymaze_Day3_220719"
    # channels = [8,9,10]

    # lfp = "/Users/freeman/Documents/saleem_folder/data/VC_Data_Marta/np_arrays/QBLU_YMaze_Day8_280719.npy"
    # mat = "/Users/freeman/Documents/saleem_folder/data/VC_Data_Marta/QBLU_YMaze_Day8_280719/extracted_position.mat"
    # file_save_name = '_sleep_Ripples_for_QBLU_YMaze_Day8_280719.npy'
    # channels = [8,9,10]

    # mat = "/Users/freeman/Documents/saleem_folder/data/VC_Data_Marta/QBLU_YMaze_Day7_270719/extracted_position.mat"
    # lfp = '/Users/freeman/Documents/saleem_folder/data/VC_Data_Marta/np_arrays/QBLU_YMaze_Day7_270719.npy'
    # file_save_name = '_sleep_Ripples_for_QBLU_YMaze_Day7_270719.npy'
    # channels = [8,9,10]

    # lfp = "/Users/freeman/Documents/saleem_folder/data/VC_Data_Marta/np_arrays/OBLU_YMaze_Day9_170519.npy"
    # file_save_name = '_sleep_Ripples_for_OBLU_YMaze_Day9_170519.npy'
    # mat = "/Users/freeman/Documents/saleem_folder/data/VC_Data_Marta/OBLU_YMaze_Day9_170519/extracted_position.mat"
    # channels = [0,1,2,3]

    # lfp = "/Users/freeman/Documents/saleem_folder/data/VC_Data_Marta/np_arrays/QBLU_Dark_Day9_290719.npy"
    # mat = "/Users/freeman/Documents/saleem_folder/data/VC_Data_Marta/QBLU_Dark_Day9_290719/extracted_position.mat"
    # file_save_name = '_sleep_Ripples_for_QBLU_Dark_Day9_290719.npy'
    # channels = [8,9,10]

    detect_SWRs(orgignal_fs = 30000,
                new_fs = 2000,
                lfp_data = lfp,
                hippocampal_channels = channels,
                saved_file_string = file_save_name,
                mat_file = mat,
                flag = "pre")

    detect_SWRs(orgignal_fs = 30000,
                new_fs = 2000,
                lfp_data = lfp,
                hippocampal_channels = channels,
                saved_file_string = file_save_name,
                mat_file = mat,
                flag = "post")