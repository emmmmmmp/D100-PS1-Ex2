import matplotlib.pyplot as plt


def plot_gdp(data, indexed=False):
    """Plot real GDP levels, or an index with 2000 equal to 100."""
    wide = data.pivot(
        index="year",
        columns="country",
        values="gdp",
    ).sort_index()

    if indexed:
        values = wide.div(wide.loc[2000]).mul(100)
        ylabel = "GDP index (2000 = 100)"
        title = "Real GDP growth since 2000"
    else:
        values = wide / 1e12
        ylabel = "GDP (trillion constant 2015 US$)"
        title = "Real GDP, 2000-2022"

    fig, ax = plt.subplots(figsize=(10, 6))
    values.plot(ax=ax, linewidth=2)

    ax.set(title=title, xlabel="Year", ylabel=ylabel)
    ax.grid(alpha=0.3)
    ax.legend(
        title="Country",
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
    )

    fig.tight_layout()
    return fig, ax
