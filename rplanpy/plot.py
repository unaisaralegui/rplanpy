import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from . import data
from . import utils


def floorplan_to_color(data: data.RplanData):
    """
    Get an image like object with the color for each pixel

    :param data: a data object from RPLAN dataset
    :type data: data.RplanData
    :return: list of colors for each pixel
    :rtype: list
    """
    coloured_image = [[utils.ROOM_COLOR[pix] for pix in row] for row in data.category]
    return coloured_image


def plot_floorplan(data: data.RplanData, ax=None, title=None):
    """
    Plot a floorplan

    :param data: a data object from RPLAN dataset
    :type data: data.RplanData
    :param ax: optional axes to plot in
    :type ax: matplotlib.axes._subplots.AxesSubplot
    :param title: optional title to add to the plot
    :type title: str
    :return: the plotted axes
    :rtype: matplotlib.axes._subplots.AxesSubplot
    """
    coloured_image = floorplan_to_color(data)
    if ax is None:
        ax = plt.subplot()
    ax.imshow(coloured_image)
    ax.set_title(title)
    ax.axis("off")
    return ax


def plot_floorplan_graph(data: data.RplanData, ax=None, title=None,
                         with_colors=True, edge_label=None):
    """
    Plot the graph representation for a floorplan

    :param data: a data object from RPLAN dataset
    :type data: data.RplanData
    :param ax: optional axes to plot in
    :type ax: matplotlib.axes._subplots.AxesSubplot
    :param title: optional title to add to the plot
    :type title: str
    :param with_colors: optional, wether to colour nodes by ther class or not, defaults to True
    :type with_colors: bool
    :return: the plotted axes
    :rtype: matplotlib.axes._subplots.AxesSubplot
    """
    if ax is None:
        ax = plt.subplot()
    G = data.get_graph()
    pos = nx.spring_layout(G)
    if with_colors:
        colors = [np.array(utils.ROOM_COLOR.get(G.nodes[n]['category'], [255, 255, 255]))/255 for n in G.nodes]
        nx.draw(G, pos, with_labels=True, ax=ax, node_color=colors)
    else:
        nx.draw(G, pos, with_labels=True, ax=ax, )
    if edge_label:
        edge_labels = nx.get_edge_attributes(G, edge_label)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax)
    ax.set_title(title)
    return ax
