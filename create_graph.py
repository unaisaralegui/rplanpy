import imageio
import matplotlib.pyplot as plt


import rplanpy

def test_functions(file, out_file='example_graph.png'):

    data = rplanpy.data.RplanData(file)

    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(15, 5))
    image = imageio.imread(file)
    ax[0].imshow(image)
    ax[0].axis("off")
    ax[0].set_title("Original image")
    rplanpy.plot.plot_floorplan(data, ax=ax[1], title="Rooms and doors")
    ax = rplanpy.plot.plot_floorplan_graph(
        data=data, with_colors=True, edge_label='door', ax=ax[2],
        title="Building graph"
    )
    plt.tight_layout()
    plt.savefig(out_file)

    plt.show()

if __name__ == '__main__':
    file = 'example.png'
    test_functions(file, out_file='example_graph.png')
