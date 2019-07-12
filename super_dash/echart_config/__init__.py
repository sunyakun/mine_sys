TREE = {
    "title": {
        "text": "决策树"
    },
    "series": [{
        "top": "10%",
        "bottom": "10%",
        "type": "tree",
        "initialTreeDepth": -1,
        "label": {
          "normal": {
            "position": "left",
            "verticalAlign": "middle",
            "align": "right",
            "fontSize": 14
          }
        },
        "leaves": {
          "label": {
            "normal": {
              "position": "right",
              "verticalAlign": "middle",
              "align": "left"
            }
          }
        }
    }]
}

PIE = {
    "title": {
        "text": "频次饼状图"
    },
    "series": [{
        "type": "pie",
        "roseType": "radius"
      },
    ]
}

HISTOGRAM = {
    "title": {
        "text": "3D直方图"
    },
    "grid3D": {},
    "xAxis3D": {
        "type": "category",
        "gridIndex": 0
    },
    "yAxis3D": {
        "type": "category",
        "gridIndex": 1}
    ,
    "zAxis3D": {
        "type": "value"
    },
    "virtualMap": {
        "dimension": "number"
    },
    "dataset": {
        "source": []
    },
    "series": [{
        "type": "bar3D",
        "encode": {
          "x": "sex",
          "y": "height",
          "z": "number"
        }
    }]
}

SCATTER = {
    "title": {
        "text": "散点图"
    },
    "xAxis": {
        "type": "value"
    },
    "yAxis": {
        "type": "value"
    },
    "series": [{
        "type": "scatter",
    }]
}
