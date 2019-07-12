import pandas

from sklearn.cluster import KMeans
from super_dash.signals import register_jsonschema
from mine.algorithm.models import Scatter


config_schema = {
    "properties": {
        "n_clusters": {
            "type": "number",
            "minimum": 1,
        },
        "axis": {
            "type": "array",
            "items": {
                "type": "string",
            }
        }
    },
    "required": ["axis"]
}

register_jsonschema.send(sender=None, schema=config_schema,
                         import_path='mine.algorithm.kmeans')


def entry(ds, cfg):
    ds = pandas.read_csv(ds)
    n_clusters = cfg.get('n_clusters')
    if n_clusters:
        kmeans = KMeans(n_clusters=n_clusters)
    else:
        kmeans = KMeans()
    labels = kmeans.fit(ds[cfg['axis']]).labels_

    models = []
    for i in range(kmeans.n_clusters):
        scatter = Scatter(cfg.get('name'))
        scatter.label = labels[i]
        models.append(scatter)
    for i_loc, series in ds[cfg['axis']].iterrows():
        models[labels[i_loc]].add(series.tolist())
    return models, kmeans.predict
