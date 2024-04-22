import AccCam.direction_of_arival as doa
import AccCam.realtime_dsp.pipeline as pipe


class DOAEstimator(pipe.Stage):
    """
    Implement a DOA estimate into a stage. Accepts an estimater and inherits it into a stage.
    """

    def __init__(self, estimator: doa.Estimator, port_size=4, destinations=None):
        """
        :param estimator: The estimator to uses in the pipeline
        """
        super().__init__(1, port_size, destinations)
        self.estimator = estimator

    def run(self):
        message = self.port_get()[0]
        data = message.payload
        direction = self.estimator.process(data)
        self.port_put(pipe.Message(direction))
