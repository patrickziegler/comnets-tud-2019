import networkx as nx
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt


def create_circular_network(n=5, cost=10):
    g = nx.Graph()

    first = None
    last = None

    for i in range(n):
        current = "n%i" % (i + 1)
        g.add_node(current)

        if first is None:
            first = current

        if last is not None:
            g.add_edge(last, current, cost=cost)

        last = current

    g.add_edge(first, last, cost=1000*cost)

    return g


def plot_network_graph(g, **kwargs):
    options = {
        "node_color": "black",
        "node_size": 1000,
        "width": 1,
        "with_labels": True,
        "font_weight": "bold",
        "font_color": "white",
        "font_size": 10,
    }

    options.update(**kwargs)

    plt.figure()
    plt.subplot(111)
    nx.draw(g, **options)
    plt.show()


if __name__ == "__main__":
    g = create_circular_network(n=10)
    p = nx.shortest_path(g, "n2", "n9", weight="cost", method="bellman-ford")
    plot_network_graph(g)
    print(p)
