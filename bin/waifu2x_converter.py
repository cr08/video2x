#!/usr/bin/env python3
# -*- coding: future_fstrings -*-


"""
Name: Waifu2x Converter CPP Driver
Author: K4YT3X
Date Created: February 8, 2019
Last Modified: June 15, 2019

Description: This class is a high-level wrapper
for waifu2x-converter-cpp.
"""
from avalon_framework import Avalon
import os
import subprocess
import threading


class Waifu2xConverter:
    """This class communicates with waifu2x cui engine

    An object will be created for this class, containing information
    about the binary address and the processing method. When being called
    by the main program, other detailed information will be passed to
    the upscale function.
    """

    def __init__(self, waifu2x_settings, model_dir):
        self.waifu2x_settings = waifu2x_settings
        self.waifu2x_settings['model_dir'] = model_dir
        self.print_lock = threading.Lock()

    def upscale(self, input_directory, output_directory, scale_ratio, jobs, image_format, upscaler_exceptions):
        """ Waifu2x Converter Driver Upscaler
        This method executes the upscaling of extracted frames.

        Arguments:
            input_directory {string} -- source directory path
            output_directory {string} -- output directory path
            scale_ratio {int} -- frames' scale ratio
            threads {int} -- number of threads
        """

        try:
            # overwrite config file settings
            self.waifu2x_settings['input'] = input_directory
            self.waifu2x_settings['output'] = output_directory

            # temporary fix for https://github.com/DeadSix27/waifu2x-converter-cpp/issues/109
            """
            self.waifu2x_settings['i'] = input_directory
            self.waifu2x_settings['o'] = output_directory
            self.waifu2x_settings['input'] = None
            self.waifu2x_settings['output'] = None
            """

            self.waifu2x_settings['scale-ratio'] = scale_ratio
            self.waifu2x_settings['jobs'] = jobs
            self.waifu2x_settings['output-format'] = image_format

            # models_rgb must be specified manually for waifu2x-converter-cpp
            # if it's not specified in the arguments, create automatically
            if self.waifu2x_settings['model-dir'] is None:
                self.waifu2x_settings['model-dir'] = os.path.join(self.waifu2x_settings['waifu2x_converter_path'],
                                                                  'models_rgb')

            # print thread start message
            self.print_lock.acquire()
            Avalon.debug_info(f'[upscaler] Thread {threading.current_thread().name} started')
            self.print_lock.release()

            # list to be executed
            execute = []

            for key in self.waifu2x_settings.keys():

                value = self.waifu2x_settings[key]

                # the key doesn't need to be passed in this case
                if key == 'waifu2x_converter_path':
                    execute.append(os.path.join(str(value), 'waifu2x-converter-cpp.exe'))

                # null or None means that leave this option out (keep default)
                elif value is None or value is False:
                    continue
                else:
                    if len(key) == 1:
                        execute.append(f'-{key}')
                    else:
                        execute.append(f'--{key}')

                    # true means key is an option
                    if value is True:
                        continue

                    execute.append(str(value))

            Avalon.debug_info(f'Executing: {execute}')
            return subprocess.run(execute, check=True).returncode

        except Exception as e:
            upscaler_exceptions.append(e)
