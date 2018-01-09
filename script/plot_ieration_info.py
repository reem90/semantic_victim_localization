#!/usr/bin/env python

import rospy
from victim_localization.msg import IterationInfo
from numpy import mean, array, hypot, diff, convolve, arange, sin, cos, ones, pi, matrix
import time
import signal
import sys
import csv
import os

from matplotlib import pyplot

f, ax_plot = pyplot.subplots(2,2)

# Define as dict so we can support values from multiple methods
file_prefix = time.strftime("%Y-%m-%d_%H-%M-%S_", time.localtime())
files_csv = {} #Array of open csv files

iterations = {}
distance = {}
distance_inc = {}
entropy_total = {}
time_iteration = {}
selected_utility = {}


def main():
  global file_prefix
  if ( len(sys.argv) > 1):
    file_prefix = sys.argv[1] + "_" + file_prefix

  rospy.init_node('plot_iteration_info', anonymous=True)
  rospy.Subscriber("victim_localization/iteration_info", IterationInfo, callback)

  try:
    while (True):
        ax_plot[0][0].clear()
        ax_plot[0][1].clear()
        ax_plot[1][0].clear()
        ax_plot[1][1].clear()


        for key in iterations:
          ax_plot[0][0].plot(iterations[key], selected_utility[key], label=key)
          ax_plot[0][1].plot(iterations[key], entropy_total[key], label=key)
          ax_plot[1][0].plot(iterations[key], distance[key], label=key)
          ax_plot[1][1].plot(iterations[key], time_iteration[key], label=key)

        ax_plot[0][0].set_ylabel('Utility (Total)')
        ax_plot[0][1].set_ylabel('Global Entropy')
        ax_plot[1][0].set_ylabel('Distance Travelled (m)')
        ax_plot[1][1].set_ylabel('Iteration Time (ms)')
        ax_plot[-1][0].set_xlabel('Iterations')
        ax_plot[-1][1].set_xlabel('Iterations')


        # Add legends
        legends = []
        legends.append( ax_plot[0][0].legend(loc='upper center', bbox_to_anchor=(0.5, 1.3), shadow=True) )

        # Set the fontsize
        for leg in legends:
          if leg is not None:
            for label in leg.get_texts():
              label.set_fontsize('small')

        pyplot.pause(1)


  except KeyboardInterrupt:
    print ("Exitting plotting node")


def callback(data):
  method = data.method_selection + " ~ " + data.method_generation

  # Check if method is already defined as key in dict
  if not method in iterations:
    # Create blank arrays
    iterations[method] = []
    distance[method] = []
    distance_inc[method] = []
    entropy_total[method] = []
    time_iteration[method] = []
    selected_utility[method] = []

    # Open csv file in append mode
    files_csv[method] = open(file_prefix + method + ".csv", "a")
    csvwriter = csv.writer(files_csv[method], delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    csvwriter.writerow([
      'Iteration',
      'Entropy Total',
      'Entropy Change %',
      'Distance Travelled',
      'Utility (Total)',
      'Time Iteration (ms)',
      ])

  # Iterations went back in time. Indicates start of new NBV loop. Exit program
  if (len(iterations[method]) > 1 and
      data.iteration < iterations[method][-1]):
      exit_gracefully()

  iterations[method].append(data.iteration)
  entropy_total[method].append(data.entropy_total)
  distance[method].append(data.distance_total)
  time_iteration[method].append(data.time_iteration)
  selected_utility[method].append(data.selected_utility)

  entropy_change = '';
  if (len(entropy_total[method]) > 1):
    prev = entropy_total[method][-2]
    curr = entropy_total[method][-1]
    entropy_change = (curr - prev)/((curr + prev)/2) * 100

    distance_inc[method].append(distance[method][-1] - distance[method][-2])
  else:
    distance_inc[method].append(0)

  csvwriter = csv.writer(files_csv[method], delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
  csvwriter.writerow([
    data.iteration,
    data.entropy_total,
    entropy_change,
    data.distance_total,
    data.selected_utility,
    data.time_iteration,
    ]
    )

def cleanup_before_exit():
  print("[Plot] Closing all csv files")
  # Close any open csv files
  for key, file in files_csv.items():
    file.close()

def exit_gracefully(signum = None, frame = None):
  cleanup_before_exit()
  os._exit(1)

if __name__ == '__main__':
  # Workaround to force plots to close when pressing CTRL-C
  original_sigint = signal.getsignal(signal.SIGINT)
  signal.signal(signal.SIGINT, exit_gracefully)

  try:
    main()
  except Exception, e:
    cleanup_before_exit()
    #print("Exception: " + sys.exc_info()[1])
    print("Exception: " + str(e))
    print('Application terminated')