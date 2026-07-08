class TraceMutationNormalizer:

    @staticmethod
    def normalize(trace):

        # recalcular order
        for idx, event in enumerate(trace.events):
            event.order = idx

        return trace