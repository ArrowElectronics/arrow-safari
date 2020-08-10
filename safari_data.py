import math
import logging
import matplotlib
import matplotlib.figure as figure
import matplotlib.animation as animation
from matplotlib import rc
import matplotlib.dates as mdates
from matplotlib.ticker import FormatStrFormatter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np

from IPython.display import display, Markdown, clear_output, Image, HTML
import ipywidgets as widgets
from ipywidgets import interact, interact_manual, Layout, Box, Button, Label, FloatText, Textarea, Dropdown, IntText

class Data:   
    def __init__(self, channels):
        self.channels = channels
        self.update_interval = 1  # Time (ms) between polling/animation updates
        
        self.units = 'Voltage'
        # conversion radio button widget
        self.conversion_button = widgets.RadioButtons(description = 'Data Format',
                                                     options=['Voltage', 'Converted'],
                                                     disabled=False)
        display(widgets.HBox([self.conversion_button]))

        self.max_rows = 4
        self.nplots = len(channels)
        # Try to arrange plot in columns of 4
        self.ncols = math.ceil(self.nplots / self.max_rows)
        self.nrows = self.max_rows if self.ncols > 1 else self.nplots
        self.plot_title_fontsize = 12
        self.plot_label_fontsize = 12
        self.tick_count = 5
        self.props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

        self.fig, axs = plt.subplots(self.nrows, self.ncols, figsize=(8, 8), sharex='all')
        row = 0
        col = 0
        for channel in self.channels:
            if self.nplots <= 1:
                self.channels[channel]["axis"] = axs
            else:
                if self.ncols > 1:
                    self.channels[channel]["axis"] = axs[row][col]
                    #axs = np.delete(axs[row], 0)
                else:
                    self.channels[channel]["axis"] = axs[row]
                    #axs = np.delete(axs, 0)
                    
                if col < (self.ncols -1):
                    col += 1 
                else:
                    col = 0
                    row += 1

            self.channels[channel]["axis"].set_title(self.channels[channel]["plot_title"], fontsize=12)
            self.channels[channel]["axis"].set_ylabel(self.channels[channel]["y_label"], color=self.channels[channel]["axes_color"])
            self.channels[channel]["axis"].tick_params(axis='y', labelcolor=self.channels[channel]["axes_color"])
            self.channels[channel]["axis"].xaxis.set_tick_params(labelbottom=True)
            self.channels[channel]["axis"].xaxis.set_major_locator(plt.MaxNLocator(self.tick_count))
            self.channels[channel]["annotation"] = self.channels[channel]["axis"].annotate("", xy=(0, 0), xytext=(-20, 20),
                                                                                           textcoords="offset points",
                                                                                           bbox=dict(boxstyle="round", fc="w"),
                                                                                           arrowprops=dict(arrowstyle="->"))

        self.fig.subplots_adjust(hspace=0.9, right=0.85)

        # https://bit.ly/2AWOqiu
        self.fig.canvas.mpl_connect("motion_notify_event", self.hover)

        self.ani = animation.FuncAnimation(self.fig,
                                           self.animate,
                                           interval=self.update_interval)

    # https://bit.ly/2AWOqiu
    # Function for updating the hovering annotations
    def update_annot(self, axis, ind):
        for channel in self.channels:
            if axis == self.channels[channel]["axis"]:
                x, y = self.channels[channel]["line"].get_data()
                self.channels[channel]["annot_ax_xy"] = (x[ind["ind"][0]], y[ind["ind"][0]])
                self.channels[channel]["annotation_text"] = "{}".format(y[ind["ind"][0]])

    # Callback for the hover event
    def hover(self, event):
        for channel in self.channels:
            try:
                if event.inaxes == self.channels[channel]["axis"]:
                    if self.channels[channel]["line"]:
                        cont, ind = self.channels[channel]["line"].contains(event)
                        if cont:
                            self.update_annot(self.channels[channel]["axis"], ind)
                            self.channels[channel]["annotation_visible"] = True
                        else:
                            if self.channels[channel]["annotation"].get_visible():
                                self.channels[channel]["annotation_visible"] = False

            except IndexError:
                print("Uh-Oh")

    def animate(self, i):                
        for channel in self.channels:
            self.channels[channel]["axis"].clear()
            self.channels[channel]["axis"].set_title(self.channels[channel]["plot_title"], fontsize=12)
            self.channels[channel]["axis"].yaxis.set_major_formatter(FormatStrFormatter('%.4f'))
            self.channels[channel]["axis"].xaxis.set_major_locator(plt.MaxNLocator(self.tick_count))

            try:
                if ((self.conversion_button.value == 'Voltage' and len(self.channels[channel]["voltages"]) > 0) or 
                    (self.conversion_button.value and len(self.channels[channel]["values"]) > 0)):
                        if self.conversion_button.value == 'Voltage':
                            self.channels[channel]["axis"].set_ylabel(self.channels[channel]["y_label"], 
                                                                      color=self.channels[channel]["axes_color"])
                            self.channels[channel]["axis"].plot(self.channels[channel]["timestamps"], 
                                                                self.channels[channel]["voltages"], 
                                                                color=self.channels[channel]["axes_color"])
                        else:
                            self.channels[channel]["axis"].set_ylabel(self.channels[channel]["y_label_converted"], 
                                                                      color=self.channels[channel]["axes_color"])
                            self.channels[channel]["axis"].plot(self.channels[channel]["timestamps"], 
                                                                self.channels[channel]["values"], 
                                                                color=self.channels[channel]["axes_color"])
                        self.channels[channel]["line"] = self.channels[channel]["axis"].get_lines()[0]
                        self.channels[channel]["annotation"] = self.channels[channel]["axis"].annotate("", xy=(0, 0), 
                                                                                                       xytext=(-20, 20), 
                                                                                                       textcoords="offset points",
                                                                                                       bbox=dict(boxstyle="round", 
                                                                                                                 fc="w"),
                                                                                                       arrowprops=dict(arrowstyle="->"))
                        self.channels[channel]["annotation"].set_visible(self.channels[channel]["annotation_visible"])
                        self.channels[channel]["annotation"].xy = self.channels[channel]["annot_ax_xy"]
                        self.channels[channel]["annotation"].set_text(self.channels[channel]["annotation_text"])
                        self.channels[channel]["annotation"].get_bbox_patch().set_alpha(0.4)
                        try:
                            ax_min = min(self.channels[channel]["voltages"])
                            ax_mean = sum(self.channels[channel]["voltages"]) / len(self.channels[channel]["voltages"])
                            ax_max = max(self.channels[channel]["voltages"])
                            ax_last = self.channels[channel]["voltages"][-1]
                            ax_annotation = '\n'.join((
                                r'Max=%.4f' % (ax_max,),
                                r'Mean=%.4f' % (ax_mean,),
                                r'Min=%.4f' % (ax_min,),
                                r'Last=%.4f' % (ax_last,)))

                            self.channels[channel]["axis"].text(1.01, 0.7, ax_annotation, 
                                                                transform=self.channels[channel]["axis"].transAxes, 
                                                                fontsize=10, verticalalignment='top', bbox=self.props)
                        except ValueError:
                            #logging.exception(e)
                            pass

            except Exception as e:
                #logging.exception(e)
                pass