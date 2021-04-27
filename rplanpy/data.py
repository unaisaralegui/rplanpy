import imageio
import numpy as np
import networkx as nx
from skimage import measure, feature, segmentation
from scipy import stats, ndimage


from . import utils


class RplanData:
    """
    Set of utilities for RPLAN dataset images

    :param image_path: Path to the image from the RPLAN dataset
    :type image_path: str
    """

    def __init__(self, image_path):
        self.image_path = image_path
        self.image = imageio.imread(image_path)
        self.boundary = utils.get_channel(self.image, 0)
        self.category = utils.get_channel(self.image, 1)
        self.instance = utils.get_channel(self.image, 2)
        self.inside = utils.get_channel(self.image, 3)
        self._rooms = None
        self._edges = None
        self._interior_doors = None

    def get_front_door_mask(self):
        """
        Get the mask for the front door

        :returns: Bounding box (min_row, min_col, max_row, max_col). Pixels belonging to the bounding box for the front door
        :rtype: np.ndarray
        """
        front_door_mask = self.boundary == 255
        region = measure.regionprops(front_door_mask.astype(int))[0]
        return np.array(region.bbox, dtype=int)

    def get_rooms(self):
        """
        Get the rooms in the floor plan
        :return:
        """
        if self._rooms is not None:
            return self._rooms
        rooms = []
        regions = measure.regionprops(self.instance)
        for region in regions:
            # c is the most common value in the region,
            # in this case c is the category of the room (channel 2)
            c = stats.mode(
                self.category[region.coords[:, 0],
                              region.coords[:, 1]],
                axis=None
            )[0][0]
            i = stats.mode(
                self.instance[region.coords[:, 0],
                              region.coords[:, 1]],
                axis=None
            )[0][0]
            y0, x0, y1, x1 = np.array(region.bbox)
            rooms.append([y0, x0, y1, x1, c, i])
        self._rooms = np.array(rooms, dtype=int)
        return self._rooms

    def get_edges(self, th=9):
        if self._edges is not None:
            return self._edges
        if self._rooms is None:
            self.get_rooms()
        edges = []
        for u in range(len(self._rooms)):
            for v in range(u + 1, len(self._rooms)):
                # check if two rooms are connected, if they are check the spatial relation between them
                if not utils.collide2d(self._rooms[u, :4], self._rooms[v, :4], th=th):
                    # rooms are not connected
                    continue
                uy0, ux0, uy1, ux1, c1, i1 = self._rooms[u]
                vy0, vx0, vy1, vx1, c2, i2 = self._rooms[v]
                uc = (uy0 + uy1) / 2, (ux0 + ux1) / 2
                vc = (vy0 + vy1) / 2, (vx0 + vx1) / 2
                if ux0 < vx0 and ux1 > vx1 and uy0 < vy0 and uy1 > vy1:
                    relation = 5  # 'surrounding'
                elif ux0 >= vx0 and ux1 <= vx1 and uy0 >= vy0 and uy1 <= vy1:
                    relation = 4  # 'inside'
                else:
                    relation = utils.point_box_relation(uc, self._rooms[v, :4])
                edges.append([u, v, relation])
        self._edges = np.array(edges, dtype=int)
        return self._edges

    def get_interior_doors(self):
        if self._interior_doors is not None:
            return self._interior_doors
        doors = []
        category = 17  # InteriorDoor
        mask = (self.category == category).astype(np.uint8)
        distance = ndimage.morphology.distance_transform_cdt(mask)
        local_maxi = (distance > 1).astype(np.uint8)
        corner_measurement = feature.corner_harris(local_maxi)
        local_maxi[corner_measurement > 0] = 0
        markers = measure.label(local_maxi)

        labels = segmentation.watershed(-distance, markers, mask=mask, connectivity=8)
        regions = measure.regionprops(labels)

        for region in regions:
            y0, x0, y1, x1 = np.array(region.bbox)
            doors.append([y0, x0, y1, x1, category])

        self._interior_doors = np.array(doors, dtype=int)
        return self._interior_doors

    def get_rooms_with_properties(self):
        """
        Get each room with their properties formatted in a dict

        :return: dictionary with room id as key and its category and additional properties as values
        :rtype: dict
        """
        properties_per_room = {
            room[-1]: {
                'category': room[-2],
                'bounding_box': room[0:4]
            }
            for room in self.get_rooms()
        }
        return properties_per_room

    def door_in_edge(self, edge):
        doors = self.get_interior_doors()
        room1 = self.get_rooms()[edge[0]]
        room2 = self.get_rooms()[edge[1]]
        for i in range(len(doors)):
            if utils.door_room_relation(doors[i], room1) and utils.door_room_relation(doors[i], room2):
                return True
        return False

    def get_edges_with_properties(self):
        """
        Get edges between rooms with their properties formatted in a dict

        :return: list of edges and edge properties [(u, v, props)]
        :rtype: list
        """
        rooms = self.get_rooms()
        properties_per_edge = [
            (
                rooms[edge[0]][-1], rooms[edge[1]][-1],
                {
                    'location': edge[2],
                    'door': self.door_in_edge(edge)
                }
            )
            for edge in self.get_edges()
        ]
        return properties_per_edge

    def get_graph(self):
        """
        Get the graph representation for the floorplan

        :return: a networkx graph with the nodes, the edges and their properties
        :rtype: networkx.classes.graph.Graph
        """
        G = nx.Graph()
        # add nodes
        G.add_nodes_from([(room, props) for room, props in self.get_rooms_with_properties().items()])
        # add edges
        G.add_edges_from(self.get_edges_with_properties())
        return G
