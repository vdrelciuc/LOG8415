class MetricData:
    def __init__(self, metric):
        # "app/t2-app-load-balancer/4db0b61e07b90a45 ActiveConnectionCount"
        label = metric["Label"].split("/")  # ["app", "t2-app-load-balancer", "4db0b61e07b90a45 ActiveConnectionCount"]
        label[2] = label[2].split()[1]      # ["app", "t2-app-load-balancer", "ActiveConnectionCount"]
        label.pop(1)                        # ["app", "ActiveConnectionCount"]

        self.label = "-".join(label)
        self.timestamps = metric["Timestamps"]
        self.values = metric["Values"]