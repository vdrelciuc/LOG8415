class MetricData:
    def __init__(self, metric):
        label = metric["Label"]

        if "cluster" in label:
            self.grouplabel = label.split("/")[2]
            label = label.split(" ")
            label = label.pop()
        else:
            label = label.replace("/", "_")
            label = label.replace(" ", "-")

        self.label = label
        self.timestamps = metric["Timestamps"]
        self.values = metric["Values"]
